# Antonio V. Franco x Huyawo v13

Release date: 2026-11-01. This is the complete repository source for Hermes.
The deployable website is `static/`. No design rebuild or Hugo rendering is required.

## What changed

- Existing translations are included in the initial HTML of all 110 localized pages.
- All 33 article pages have one localized schema graph with full article text,
  named sections, existing citations, author identity and translation references.
- Metadata titles, descriptions, canonical URLs, social previews and language
  alternates are consistent. The English landing-page descriptions are populated.
- The sitemap lists all 110 canonical pages, including reciprocal language
  alternates and a stable English `x-default` URL for each group.
- `robots.txt` advertises the sitemap and keeps crawling permitted.
- All 11 languages have complete RSS feeds, with three articles each.
- Image preloads preserve original image files and rendering.
- `llms.txt` provides an optional article discovery index.
- GitHub Pages validates the checked-in static output before deployment.

## What is preserved

CSS, fonts, images, layout, components, visible article text, article headings,
article sources, two lead forms per article, analytics configuration, lead
configuration, Supabase code and geographic routing are retained. No remote
publication, infrastructure change, credential access or form submission was
performed while preparing this release.

Two existing hydration errors in `site.js` were removed: the custom contact page
no longer enters a landing renderer that expects nonexistent elements, and
privacy rendering no longer calls an undefined function. The privacy renderer
keeps its original visible output; it does not add a link or a component.

## Validate the source

Python 3.12+ and Node.js 20+:

```bash
python3 -m pip install -r scripts/requirements-seo.txt
python3 scripts/validate-seo.py
node --test geo-worker/index.test.mjs
```

The output is already built. `scripts/optimize-seo.py` is an optional regeneration
tool for this release's existing translations and three articles. It reads the
existing JavaScript dictionaries. It does not translate or rewrite research.
When adding future articles, extend the article metadata in the generator and
the expected inventory in the validator before regenerating. Update the actual
release date used for sitemap modification dates; do not invent editorial dates.

See `HERMES-HANDOFF.md`, `reports/SEO-GEO-AUDIT.md` and
`reports/validation.json` for the scope and verification evidence.
