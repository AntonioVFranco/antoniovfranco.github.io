# SEO and GEO audit: v13

Reviewed on 2026-11-01 against the supplied `blog.zip`. This report concerns
the supplied source and locally served pages, not a production deployment.

## Verdict

The articles already followed the strongest editorial principles in the six
Neil Patel references: specific business questions, substantive explanations,
named authorship, primary references, headings, comparisons and a route to
private engineering work. Their existing text did not require replacement.

The implementation had material technical gaps. V13 fixes discovery,
international metadata and initial HTML delivery while preserving the UI and
all article bodies. Offsite authority and measured AI visibility are ongoing
distribution tasks; they cannot be established by modifying an archive.

## Observed findings and changes

| Area | Supplied source | V13 |
| --- | --- | --- |
| Languages | 11 supported languages | All 11 retained |
| Article inventory | 3 articles, 33 localized article pages | All 33 preserved |
| Article schema | 22 article pages; first article lacked schema in every language | All 33 have localized `BlogPosting` graphs |
| Other page schema | Absent | Graphs on all 117 HTML documents |
| Initial translated HTML | Much of the shared copy and several page bodies depended on client JavaScript | Existing translations and initial tab content pre-rendered on all 110 localized pages |
| English descriptions | 7 localized English documents had empty descriptions | All descriptions populated |
| Page descriptions | Section pages reused the same general description within a language | Descriptions derived from each page's existing content; unique within each language |
| Title elements | Very long article titles copied directly into title elements | Concise localized metadata titles; visible H1 headings unchanged |
| Social metadata | Present on 33 article pages; absent elsewhere | Localized Open Graph and Twitter metadata throughout |
| Language alternates | No `x-default`; root compatibility documents lacked complete clusters | Reciprocal 11-language clusters and stable English `x-default` throughout |
| Sitemap | 24 URL entries, omitting most localized landing pages | Exactly 110 canonical translated URLs and complete alternate clusters |
| Robots | Only `User-agent: *` | Explicit allow rule and sitemap discovery |
| Feeds | General feed contained 2 articles | All 3 articles in each of 11 language feeds, plus English compatibility feeds |
| Image discovery | Existing cover images and styling | Original image bytes and styling retained; loading preloads added in the head |
| CI | Direct upload to GitHub Pages | Static SEO validation and existing routing tests before upload |

The 117 HTML documents consist of 110 localized canonical pages plus 7 existing
unlocalized compatibility documents. The latter point to their English
equivalents and remain outside the sitemap. Existing URL paths are retained.

## Applying the six Patel references

| Reference | Applicable lesson | Implementation or retained behavior |
| --- | --- | --- |
| [Prompt volume](https://neilpatel.com/br/blog/prompt-volume/) | Start with buyer questions rather than estimated prompt volumes | Preserve the three concrete engineering/business topics. No invented demand figures, keyword volumes or prompt metrics are introduced. |
| [Fintech AI visibility](https://neilpatel.com/blog/fintech-ai-visibility/) | Be recognizable within a specific category and measure context, not just mentions | Clarify the author, Huyawo, Huyawo Solutions and each article's technical subjects in linked schema entities. Category-level visibility is a future measurement task, not a claimed result. |
| [ChatGPT SEO](https://neilpatel.com/br/blog/chatgpt-seo/) | Make answers readable and attributable, with a sound technical foundation | Serve complete existing article bodies and translated shared content in HTML. Link existing sections, primary citations, language versions and author identity in schema. Preserve the existing tables and answers. |
| [GEO guide](https://neilpatel.com/br/blog/generative-engine-optimization-geo/) | Favor depth, evidence, source clarity and thematic consistency | Retain substantive explanations and source links. Add full article/section parity checks so schema represents visible material. No fabricated Huyawo benchmark results or editorial updates. |
| [GEO agency](https://neilpatel.com/br/blog/agencia-de-geo/) | Connect useful information to an appropriate commercial next step | Retain the two existing article contact cards and written/asynchronous positioning. Technical work improves the discovery of this existing path; it does not activate or alter lead infrastructure. |
| [LLM SEO](https://neilpatel.com/blog/llm-seo/) | Use clear structure, transparent sourcing, crawlability and continuing measurement | Pre-render translations, complete metadata and feeds, expose author/citation relationships, and provide a measurement protocol below. |

These lessons were checked against the live reference pages. They were applied
as engineering judgments, not as a ranking formula.

## Article representation

Each localized article graph contains the existing visible headline,
description, full article body, existing introduction, technical subjects,
section anchors with their original text, primary references, author,
publisher and ten translation references. Contact-card text is excluded from
`articleBody` so the editorial body is represented accurately.

The author is Antonio V. Franco. Huyawo and Huyawo Solutions are represented as
separate organizations using the relationships already described on the site
and in the supplied project context. No review scores, client counts, awards,
pricing, benchmark achievements or product-maturity claims are added.

No hidden FAQ content, `FAQPage`, review markup, synthetic testimonials or
unsupported `SearchAction` is introduced. Existing headings and tables stay
unchanged. A metadata title can be shorter than the visible H1 without changing
the article's meaning or its presentation.

The n8n and catalog articles retain their original publication and editorial
modification dates. The first article has no publication date in the supplied
source; v13 deliberately does not invent one. Sitemap `lastmod` identifies the
actual HTML release modification date, not a rewritten publication date.

Unicode article paths use consistently percent-encoded absolute URLs in the
metadata, sitemap, feeds and schema. Their existing directory names and routes
are unchanged.

## Source verification

The six primary article references below were opened during this review. Their
titles and main claims matched the role they play in the existing articles:

- [Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce](https://aclanthology.org/2026.acl-industry.40/).
- [Scaling E-Commerce Attribute Extraction with Parallel Decoding](https://aclanthology.org/2026.akbc-1.13/).
- [When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs](https://aclanthology.org/2026.emnlp-industry.187/).
- [Introducing n8n 3.0](https://blog.n8n.io/introducing-n8n-v3/).
- [SFT or RL for Tool-Calling Agents? A Controlled Study Across Data, Method, and Scale](https://aclanthology.org/2026.realm-1.90/).
- [Robust Tool Use via Fission-GRPO: Learning to Recover from Execution Errors](https://aclanthology.org/2026.acl-long.1880/).

This was a focused credibility check of primary references, not an independent
reproduction of their experiments or a line-by-line factual review of every
translation. Existing article citations remain intact and are mirrored in schema.

## Verification

Static validation checks every HTML document, all canonical destinations,
internal asset/navigation targets, language alternates, schema/visible-text
parity, article section/citation coverage, feed entries and sitemap closure.
It also confirms that translated `data-t`, `data-t-html` and placeholder text
already exists in the served HTML. See `validation.json` for the exact result.

Comparison with the original archive confirms that the complete article DOM
and text remain unchanged on all 33 article pages. CSS, images and every other
existing asset except the narrowly repaired `site.js` are byte-identical.
The original geographic routing implementation and its five tests are unchanged.

Browser comparisons cover all 11 localized homepages plus 9 representative
section and article pages, including Arabic, Chinese and Japanese. Visible
main content and layout offsets/dimensions matched on all 20 samples. Existing
motion can vary between captures; layout checks use offsets rather than
animation-dependent screen coordinates. See `ui-validation.json`.

The small JavaScript repair prevents the custom contact page from entering a
renderer that expects missing elements and removes an undefined privacy call.
It preserves the original rendered privacy content without adding its formerly
unreachable extra link. Forms, consent controls and analytics are unchanged.

## What to measure after publication

1. In the existing Search Console property, inspect representative language
   URLs and submit the sitemap. Check the fetched HTML and indexing results.
2. Track organic landing pages, AI referral sources and actual qualified
   inquiries in the existing analytics setup, subject to its consent behavior.
3. Keep a dated prompt set around catalog enrichment cost, smaller agent
   economics and durable agent execution. Use decision-specific wording rather
   than invented prompt-volume estimates.
4. Record platform, model/version when disclosed, language, date, brand mention,
   position/context, exact cited URLs and competing sources. Repeat comparable
   observations rather than treating one response as a ranking.
5. Continue publishing evidence from actual Huyawo work and earning relevant
   external references. A schema graph cannot substitute for those activities.

No monitoring jobs, third-party accounts or external publication were created.

## Technical interpretation

The optional `llms.txt` is a convenience index. It is not required by Google,
not a substitute for HTML, and not evidence of better ranking or AI citations.
[Google's AI features guidance](https://developers.google.com/search/docs/appearance/ai-features)
prioritizes accessible, helpful content and matching structured data; it does
not require a special AI file or schema. [OpenAI's crawler documentation](https://developers.openai.com/api/docs/bots)
distinguishes search crawling from model-training crawling. The existing
permissive crawling policy is preserved; no new training restriction is added.

The release fixes technical issues within the supplied source. Production CDN
access, actual HTTP responses, Core Web Vitals, Search Console indexing,
third-party mentions and AI citations require observation after deployment.
