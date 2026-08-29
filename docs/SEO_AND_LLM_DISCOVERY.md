# SEO and LLM Discovery — Operational Guide

This document lists the owner actions that CANNOT be done from the repository
alone, plus the operational notes for Google Search Console, Bing Webmaster
Tools, and Medium syndication.

The repository automation already handles:

- Sitemap (`/sitemap.xml`), RSS (`/index.xml`), `robots.txt`, `llms.txt`,
  `llms-full.txt`, JSON-LD, Open Graph, Twitter Cards, IndexNow key + key file.
- Automatic inclusion of **any future article** in every artifact (homepage,
  sitemap, RSS, `llms.txt`, `llms-full.txt`, JSON-LD, and social image).
- A CI validator that fails the build on objective violations.
- IndexNow submission after a successful deploy.

---

## 1. Google Search Console

Owner must do these in the Google Search Console dashboard
(https://search.google.com/search-console):

1. **Verify domain ownership** for `antoniovfranco.com`
   (DNS TXT or HTML-file method). The repo does not hold a verification token.
2. **Submit the sitemap**: `https://antoniovfranco.com/sitemap.xml`.
3. **Inspect and request indexing** for the three current articles:
   - `/posts/2026/agentic-ai-slms-why-models-above-50-cents-burning-money/`
   - `/posts/2026/glm-5-2-sonnet-4-5-and-open-models-were-enough/`
   - `/posts/2026/deepseek-v4-flash-glm-5-2-combination/`
4. **Identify all legacy URLs still indexed**, e.g.:
   - `/posts/2026/quantized-llms-cost-effectiveness/`
   - `/posts/2026/by-osmosis-fuvest-arc-prize-vitalabs-study-research-method/`
   - `/posts/2026/auditable-contract-screening-nli/`
   These articles no longer exist. **Do NOT restore them and do NOT create
   semantically-false redirects.** Use Google’s *Removals* tool for URLs that
   must not be shown, and let them 404 naturally. Do not point them at pages
   with different meaning.
5. **Monitor** the Search results report: queries, pages, impressions, CTR,
   average position. Watch for residual legacy URLs and for the three live
   articles once indexed.
6. Re-submit the sitemap and use *URL Inspection → Request indexing* whenever a
   new article ships (the IndexNow submission handles Bing; Google needs the
   manual/ping flow).

---

## 2. Bing Webmaster Tools

Owner must do these in Bing Webmaster Tools
(https://www.bing.com/webmasters):

1. **Verify the domain** `antoniovfranco.com`.
2. **Submit the sitemap**: `https://antoniovfranco.com/sitemap.xml`.
3. **Confirm IndexNow is receiving submissions.** The IndexNow key is served at
   `https://antoniovfranco.com/4aee93251a59ff29f22f84706d8b7e49.txt`. Verify the
   key file is publicly reachable and that submissions appear in the IndexNow
   reports / Bing Webmaster "IndexNow" page.
4. **Monitor errors and index coverage** in Bing Webmaster Tools; act on any
   crawl errors or indexing anomalies.
5. IndexNow does **not** submit to Google. Google coverage is handled via
   Search Console (section 1).

---

## 3. Medium syndication

The blog at `antoniovfranco.com` is the **source of truth**; Medium is the
syndication target. The Canonical must always point at the home domain.

### Current three articles

Each already has a Medium version on Antonio’s profile. Verify **manually** the
canonical on each Medium page (view-source → `<link rel="canonical">`):

- Agentic AI / SLMs / US$0.50:
  `https://medium.com/@AntonioVFranco/agentic-ai-slms-and-why-models-above-us-0-50-output-per-1m-tokens-are-equivalent-to-burning-money-3d44078fd1ed`
- GLM-5.2 / Sonnet 4.5:
  `https://medium.com/@AntonioVFranco/glm-5-2-i-thought-sonnet-4-5-and-similar-open-models-were-enough-but-936e44879530`
- DeepSeek V4 Flash + GLM-5.2:
  `https://medium.com/@AntonioVFranco/the-deepseek-v4-flash-glm-5-2-04eea3eaf0b1`

Each canonical must resolve to the article URL on `https://antoniovfranco.com/`.
If Medium points its canonical at Medium itself, correct it through Medium’s
canonical settings or re-import.

### Future articles

1. Publish first on the home domain.
2. Confirm the page is live and carries its own absolute canonical.
3. Use Medium’s official **import from URL** tool with the original
   `antoniovfranco.com` URL.
4. Inspect the Medium source code to confirm the canonical points to the home
   domain (not to Medium). If not, fix it.
5. Apply only a few exact, relevant topic tags — no tag stuffing.
6. Submit the article to a relevant technical publication only when there is
   genuine editorial fit.
7. Participate in real responses and discussions. Never automate claps,
   follows, or comments.
8. Never publish multiple independent copies without a canonical pointing to
   the original.

---

## 4. Backlinks from technical properties

Repo/docs, model cards, datasets, and Hugging Face Spaces that genuinely relate
to an article should link back to the corresponding `antoniovfranco.com` URL.
These technical backlinks are far more valuable than generic link directories.

Current relevant properties (verify and add links where they exist):

- GitHub: `https://github.com/AntonioVFranco`
- Hugging Face: `https://huggingface.co/AntonioVFranco`
- X: `https://x.com/AntonioVFranco`
- LinkedIn: `https://www.linkedin.com/in/antoniovfranco/`

Add a link back to each article only where a real relationship exists (e.g., a
model card or dataset discussed in the post).

---

## 5. Adding a new article (checklist for the owner/contributor)

The repository is fully automated, so a new published post requires only that
you create the content following `archetypes/posts.md`. CI will:

1. Generate its social image (`scripts/generate_social_images.py`).
2. Build the site.
3. Validate front matter, images, single `<h1>`, canonical, JSON-LD, internal
   links, and inclusion in sitemap/RSS/`llms.txt`/`llms-full.txt`.
4. Deploy, then submit the new URL to IndexNow.

After merge, do the Search Console request-indexing and (optionally) Medium
import per the steps above.
