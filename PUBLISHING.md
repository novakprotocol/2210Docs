# Publishing IaT Docs Engine Sites to GHE Pages

## Preferred workflow

The public mirror includes `.github/workflows/publish-pages.yml`. It compiles the static site and publishes only the generated output to the `gh-pages` branch. The intended sequence is:

1. Check out the repository.
2. Install the pinned Python dependencies.
3. Run engine diagnostics.
4. Refresh repository intelligence when authorized.
5. Run unit and contract tests.
6. Run release validation.
7. Build the static `site/` artifact.
8. Publish the generated files to the `gh-pages` branch.
9. Let Pages serve the root of that branch with `.nojekyll`.

The enterprise mirror uses the local branch-publication helper by default. Activate a workflow only after the enterprise runner and approved action mirrors are verified.

## Branch publication fallback

Where custom Pages workflows are unavailable:

1. Build and validate `site/` on an approved workstation or runner.
2. Publish only the generated files to the approved Pages branch/path.
3. Retain `.nojekyll`.
4. Record the source commit, engine version, build ID, manifest hash, and publication actor.
5. Do not hand-edit the generated branch.

## Update detection

Every build creates `site/site-version.json`. An open reader periodically checks that record. When the build ID changes, the page displays:

> Update available — refresh your browser

Refreshing saves the current exact location, requests the current build, and restores the reader's position.

## Central watermark dependency

The theme references the approved central watermark URL. Publication of a derived manual can succeed even when the external asset cannot be fetched, but the graphic will not display until the asset Pages site is operational. The asset site's build status must therefore be included in release verification.

## Publication evidence

Retain:

- build manifest;
- build receipt;
- source commit;
- workflow/run identifier;
- validation output;
- Pages URL and status;
- release revision and approval reference.
