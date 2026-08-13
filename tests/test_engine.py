from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from iatdocs.build import build_project  # noqa: E402
from iatdocs.config import load_config  # noqa: E402
from iatdocs.initdoc import initialize_document  # noqa: E402
from iatdocs.markdown import render_markdown_files  # noqa: E402
from iatdocs.migrate import migrate_jekyll_project  # noqa: E402
from iatdocs.validate import validate_project  # noqa: E402


class HtmlAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.buttons: list[str] = []
        self._button_depth = 0
        self._button_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        if tag == "button":
            self._button_depth += 1
            if self._button_depth == 1:
                self._button_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._button_depth:
            self._button_depth -= 1
            if self._button_depth == 0:
                self.buttons.append(" ".join("".join(self._button_parts).split()))

    def handle_data(self, data: str) -> None:
        if self._button_depth:
            self._button_parts.append(data)


def copy_engine(destination: Path) -> Path:
    ignored = shutil.ignore_patterns(
        ".git", "site", "__pycache__", ".template-backup", ".venv", ".pytest_cache", "*.pyc"
    )
    shutil.copytree(ROOT, destination, ignore=ignored)
    return destination


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class IaTDocsEngineTests(unittest.TestCase):
    def test_configuration_and_template_validation_pass(self) -> None:
        config = load_config(ROOT)
        report = validate_project(config, mode="template")
        self.assertTrue(report.passed, [item.as_dict() for item in report.errors])
        self.assertEqual(config.build.mode, "single-manual")
        self.assertEqual(config.output_dir.name, "site")

    def test_build_generates_static_contract_and_valid_html(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iatdocs-build-") as temp:
            project = copy_engine(Path(temp) / "derived-controlled-document")
            result = build_project(project, strict=True, release=False)
            output = Path(result["output"])
            required = {
                "index.html",
                "404.html",
                "search-index.json",
                "site-version.json",
                "source-map.json",
                "build-manifest.json",
                "build-receipt.txt",
                ".nojekyll",
                "assets/css/manual.css",
                "assets/js/manual.js",
            }
            actual = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
            self.assertTrue(required.issubset(actual), sorted(required - actual))

            html = (output / "index.html").read_text(encoding="utf-8")
            audit = HtmlAudit()
            audit.feed(html)
            self.assertEqual(len(audit.ids), len(set(audit.ids)), "duplicate HTML IDs found")
            ids = set(audit.ids)
            missing = sorted(href for href in audit.hrefs if href.startswith("#") and len(href) > 1 and href[1:] not in ids)
            self.assertFalse(missing, missing)

            self.assertIn("Bookmark", html)
            self.assertIn("Update available — refresh your browser", html)
            self.assertIn("Return to furthest read", html)
            self.assertIn("Ticket / controlled-record reference", html)
            self.assertNotIn("class=\"splash", html)
            self.assertNotIn("{%", html)
            self.assertNotIn("{{", html)
            prohibited = {"print", "export", "download document"}
            self.assertFalse(prohibited.intersection({button.casefold() for button in audit.buttons}))

            inherited_subject = "Legacy " + "Worked Procedure " + "Example"
            self.assertNotIn(inherited_subject, html)

    def test_manifest_hashes_match_generated_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iatdocs-manifest-") as temp:
            project = copy_engine(Path(temp) / "controlled-doc")
            result = build_project(project)
            output = Path(result["output"])
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["build_id"], result["build_id"])
            for item in manifest["output_files"]:
                path = output / item["path"]
                self.assertTrue(path.is_file(), item["path"])
                self.assertEqual(path.stat().st_size, item["bytes"])
                self.assertEqual(sha256(path), item["sha256"])

    def test_markdown_semantic_callout_and_stable_heading(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iatdocs-md-") as temp:
            root = Path(temp)
            source = root / "content.md"
            source.write_text(
                "## Validation & Evidence\n\n::: warning Controlled warning\nDo not proceed without approval.\n:::\n",
                encoding="utf-8",
            )
            html, rendered, headings = render_markdown_files([source], root=root, allow_raw_html=True)
            self.assertIn('class="callout warning"', html)
            self.assertIn("Controlled warning", html)
            self.assertEqual(headings[0].anchor, "validation-and-evidence")
            self.assertEqual(rendered[0].source, "content.md")

    def test_release_mode_blocks_canonical_seed(self) -> None:
        report = validate_project(load_config(ROOT), mode="release")
        self.assertFalse(report.passed)
        codes = {item.code for item in report.errors}
        self.assertIn("PLACEHOLDER", codes)
        self.assertIn("RELEASE_STATUS", codes)
        self.assertIn("RELEASE_EFFECTIVE_DATE", codes)

    def test_profile_catalog_and_init_dry_run(self) -> None:
        catalog = json.loads((ROOT / "ai" / "document-profiles.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["profiles"]), 22)
        self.assertEqual(len(catalog["module_catalog"]), 32)
        with tempfile.TemporaryDirectory(prefix="iatdocs-init-") as temp:
            project = copy_engine(Path(temp) / "private-derived-iop")
            result = initialize_document(
                project,
                profile_id="iop",
                document_id="ITOPS-IOP-TEST-0001",
                title="Synthetic Controlled Document",
                source_repository="software/private-derived-iop",
                apply=False,
            )
            self.assertEqual(result["status"], "planned")
            self.assertEqual(result["profile"], "iop")
            self.assertGreater(result["section_count"], 0)
            self.assertIn(2, result["modules"])
            self.assertIn(32, result["modules"])

    def test_profile_init_apply_updates_only_document_inputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iatdocs-init-apply-") as temp:
            project = copy_engine(Path(temp) / "private-derived-runbook")
            result = initialize_document(
                project,
                profile_id="runbook",
                document_id="ITOPS-RUNBOOK-TEST-0001",
                title="Synthetic Runbook",
                source_repository="software/private-derived-runbook",
                creator_name="Synthetic Creator",
                owner="Synthetic Owner",
                steward="Synthetic Steward",
                review_date="2027-01-01",
                apply=True,
            )
            self.assertEqual(result["status"], "applied")
            document = json.loads((project / "data" / "document.json").read_text(encoding="utf-8"))
            self.assertEqual(document["document_id"], "ITOPS-RUNBOOK-TEST-0001")
            self.assertEqual(document["content_path"], "content/index.md")
            content = (project / "content" / "index.md").read_text(encoding="utf-8")
            self.assertIn("Generated by IaT Docs Engine", content)
            self.assertNotIn("Synthetic Runbook", (project / "theme" / "templates" / "manual.html").read_text(encoding="utf-8"))

    def test_v007_migration_dry_run_and_apply(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iatdocs-migrate-") as temp:
            target = Path(temp) / "old-controlled-document"
            (target / "docs" / "_data").mkdir(parents=True)
            (target / "docs" / "assets" / "css").mkdir(parents=True)
            (target / "docs" / "assets" / "js").mkdir(parents=True)
            (target / "docs" / "index.md").write_text("---\nlayout: manual\n---\n\n## 1. Purpose\n\nSynthetic.\n", encoding="utf-8")
            document = json.loads((ROOT / "data" / "document.json").read_text(encoding="utf-8"))
            revisions = json.loads((ROOT / "data" / "revisions.json").read_text(encoding="utf-8"))
            repository = json.loads((ROOT / "data" / "repository.json").read_text(encoding="utf-8"))
            contributions = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
            for name, value in {
                "document.json": document,
                "revisions.json": revisions,
                "repository.json": repository,
                "contributions.json": contributions,
                "contribution-config.json": {"schema_version": 1, "contributors": []},
            }.items():
                (target / "docs" / "_data" / name).write_text(json.dumps(value), encoding="utf-8")
            (target / "docs" / "assets" / "css" / "manual.css").write_text("body{}", encoding="utf-8")
            (target / "docs" / "assets" / "js" / "manual.js").write_text("'use strict';", encoding="utf-8")

            plan = migrate_jekyll_project(target, engine_source=ROOT, apply=False)
            self.assertEqual(plan["status"], "planned")
            applied = migrate_jekyll_project(target, engine_source=ROOT, apply=True)
            self.assertEqual(applied["status"], "applied")
            self.assertTrue((target / "content" / "index.md").is_file())
            self.assertTrue((target / "data" / "document.json").is_file())
            self.assertTrue((target / "theme" / "templates" / "manual.html").is_file())
            migrated = json.loads((target / "data" / "document.json").read_text(encoding="utf-8"))
            self.assertEqual(migrated["content_path"], "content/index.md")
            self.assertEqual(migrated["engine_version"], "0.08.2")
            self.assertTrue((target / "LEGACY-JEKYLL-MIGRATION.md").is_file())

    def test_theme_contract_and_no_inherited_subject_in_source(self) -> None:
        css = (ROOT / "theme" / "assets" / "css" / "manual.css").read_text(encoding="utf-8")
        js = (ROOT / "theme" / "assets" / "js" / "manual.js").read_text(encoding="utf-8")
        self.assertIn('top: calc(64px + 2.2vh)', css)
        self.assertIn('right: 2.2vw', css)
        body_block = css.split("body::before", 1)[1].split("}", 1)[0]
        self.assertNotIn("bottom:", body_block)
        for marker in (
            "MAX_MANUAL_BOOKMARKS",
            "bookmarkReference",
            "bookmarkNote",
            "returnMarker",
            "Update available — refresh your browser",
        ):
            self.assertIn(marker, js)

        inherited_subject = "Legacy " + "Worked Procedure " + "Example"
        for path in ROOT.rglob("*"):
            if not path.is_file() or "site" in path.parts or path.suffix.lower() in {".pyc", ".png", ".pdf", ".zip"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            self.assertNotIn(inherited_subject, text, path.as_posix())

    def test_no_documentation_framework_dependency(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").casefold()
        dependencies = pyproject.split("dependencies = [", 1)[1].split("]", 1)[0]
        for framework in ("mkdocs", "sphinx", "docusaurus", "docsify", "antora", "vitepress", "starlight", "jekyll"):
            self.assertNotIn(framework, dependencies)
        self.assertIn("jinja2", dependencies)
        self.assertIn("mistune", dependencies)


if __name__ == "__main__":
    unittest.main()
