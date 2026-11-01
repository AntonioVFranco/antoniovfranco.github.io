# Hermes handoff: v13

## Requested operation

Apply this source to the existing antoniovfranco.com repository. Preserve the
current repository identity, remote, default branch and domain configuration.
Do not create a new website, theme, layout or repository.

Extract the archive, enter `antoniovfranco-v13-github/`, and apply its contents
at the existing repository root, including `.github/`, `.gitignore` and all
unchanged application source. The archive excludes embedded Git history and
build locks. Keep the receiving repository's own `.git/` directory.

Review the diff and run the checks documented in `README-V13.md`. The release
already contains finished HTML under `static/`. The existing GitHub Pages
workflow uploads that directory directly after validation; do not substitute
a template-generated Hugo website or upload the repository root as Pages.

## Boundaries

- Retain all CSS and image files exactly. The approved UI is unchanged.
- Retain every article body and its two lead forms exactly.
- Keep the 33 existing localized article paths and all 11 language codes.
- Keep `static/CNAME` and the original backend/analytics configurations.
- Geographic routing in `geo-worker/` is unchanged and separately deployed.
  Its five existing tests pass. Do not deploy it again as part of this handoff.
- Do not activate forms, change Supabase, change consent behavior or add scripts.
- Do not publish a localhost preview or `preview.py` to the production source.

## Release checks

The supplied audit records static validation against the original archive and
browser comparisons. The checked-in report identifies the precise coverage.

After the owner authorizes the GitHub publication, inspect the resulting live
responses for these paths:

- `/robots.txt` and `/sitemap.xml`.
- `/en/`, `/pt/`, `/ar/`, `/zh/`, `/ja/`.
- `/blog/en/index.xml` and `/blog/pt/index.xml`.
- Each of the three articles in at least English and Portuguese.

Check the raw HTML response, not just the rendered DOM. Confirm that translated
copy, the schema graph and canonical/language alternate links are present.
For Unicode slugs, percent-encoded URLs and their decoded form identify the
same existing route. Never double-encode percent signs.

The current production CDN, DNS, HTTP response headers and Search Console
account were not changed or verified by this offline release. Check that the
existing CDN allows search crawlers, that `www` reaches the preferred origin,
and that explicit language URLs do not get redirected to another language.
Submit the sitemap in the existing Search Console property and inspect a
representative URL after publication if the owner requests that operation.

## Interpretation

Structured data and crawlability improve discoverability. Rankings, indexing,
AI citations and inbound leads are outcomes to measure after publication.
Do not label these unmeasured outcomes as release results. External mentions,
original experiments and distribution remain ongoing work outside this patch.
