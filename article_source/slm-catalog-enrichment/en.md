# SLM fine-tuning: why marketplaces are rethinking the cost of enriching their catalogs

A marketplace may process millions of products to answer a seemingly simple question: what does each product offer?

Imagine a coffee machine whose description specifies 15 bar of pressure. To let customers compare it with other products, the marketplace needs to identify that information and fill in the corresponding catalog field. It sounds like little work. Now multiply the operation by millions of listings, with new products and changes every day.

This is where using a general-purpose LLM for every extraction starts to strain the budget.

In 2026, three studies by Amazon teams showed a different approach. Smaller models adapted to work with product attributes achieved substantial inference cost reductions. The studies also revealed where quality drops and how to keep those savings from turning into more review work.

The question for catalog managers should not be which model writes better. It should be how much it costs to obtain a correct attribute that is ready to use.

## Why does catalog enrichment cost so much?

Anyone who has worked with product data knows the problem. Suppliers describe goods differently, even within the same category. Some information appears in the title, some in the description, and the terms are not always consistent.

This directly affects the shopping experience. Without correctly populated attributes, filters miss products, comparisons become less useful, and customers find it harder to decide.

Language models help turn descriptions into fields a system can query. The problem arises when a company uses the same general-purpose model for almost every task, including those that repeat with little variation.

Consider an operation that extracts the pressure attribute from thousands of coffee machines. It needs to recognize the value and unit, follow the catalog format, and avoid inventing missing information. It does not need a model capable of an open conversation about any subject.

Even when individual inferences seem cheap, they recur whenever the catalog grows or needs updating. A small expense per product can become significant across tens of millions of records.

Volume therefore changes the decision. The more frequently processing happens, the more sense it makes to investigate a specialized model.

## What does training an SLM to work with products mean?

SLM stands for *small language model*. The idea is to use a model with fewer parameters and adapt it to a defined task, such as extracting attributes from product descriptions.

With fine-tuning, the model receives examples of inputs and expected outputs. It learns how the operation should work, which fields to populate, and when to leave a value blank.

One technique used in this process is LoRA, which trains a smaller number of parameters instead of updating all the model's weights. This can reduce training memory requirements. It does not, by itself, mean inference will become 98% cheaper. The final cost also depends on the model and how it runs.

Another option is to use a larger model to generate training examples and transfer part of its ability to the smaller one. This process is called distillation. After training, the small model performs a task that previously depended on the larger model.

In practice, the company concentrates the adaptation work before operating at scale. Rather than continually paying for capabilities it rarely uses, it runs a model prepared for the process.

This strategy only makes sense when the learned behavior remains useful long enough to offset training and maintenance. The results published in 2026 help put that possibility in perspective.

## One study found a 98% reduction in inference cost

In July 2026, Lakshman Kolasani and Fatemeh Taheri Dezaki published [*Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*](https://aclanthology.org/2026.acl-industry.40/) in the ACL Industry Track.

The researchers adapted Amazon Nova 2 Lite with LoRA to generate attributes during product listing. Their main comparison was with Claude Sonnet 4.5, which delivered the best results for the task among the models the team evaluated at the time.

The adapted model achieved an estimated **98% lower inference cost**, calculated using public model prices at the time of the experiments. Its p90 latency also fell by approximately **70%**. This means the time within which 90% of responses completed became shorter.

The study went beyond internal tests. In an experiment with real users, suggestions from the small model had an acceptance rate of **86.4%**, compared with **88.3%** for Claude Sonnet 4.5.

One detail cannot be ignored. The smaller model also achieved an accepted attribute fill rate of **59.1%**, compared with **63.0%** for the larger model. According to the authors, the differences were statistically significant.

The savings therefore did not come with identical production performance. The business decision is whether the quality difference justifies the cost reduction and how to handle fields the model cannot fill.

The work also offers a training idea: select new examples based on information the model failed to extract but that already existed in the catalog. Instead of indiscriminately expanding the training set, the team focused its second round on cases with larger gaps between catalog data and predictions.

With two rounds of a thousand examples each, valid fill rate rose from 66.03% to 74.20% in the offline evaluation. This showed improvement on the test set used, although production performance remained below the larger model.

For a marketplace, the lesson is simple: **errors in your own catalog can help you choose the next training data**. But you must check that existing content is correct before treating it as a reference.

## Another study processed 30 million products for about US$5,000

Published in October 2026, [*Scaling E-Commerce Attribute Extraction with Parallel Decoding*](https://aclanthology.org/2026.akbc-1.13/), by Nikhita Vedula and colleagues, examined the problem from another angle.

The team began with a question many operations overlook: which attributes actually help buyers distinguish products within a category?

First, a larger model identifies the relevant attributes. Then an adapted Qwen3-4B extracts values from descriptions. The system uses *Hyper-Parallel Decoding* (HPD), which generates values for several attributes in parallel instead of producing everything sequentially.

Extraction accuracy was close to **85%**, similar to the larger reference model. The research also included a human evaluation of 500 products, which found approximately the same accuracy.

The economic difference appears when processing 30 million products:

| Configuration evaluated | Estimated inference cost | Estimated time |
| --- | ---: | ---: |
| Reference LLM through a batch API | US$63,000 | More than 300 hours, excluding queue waiting |
| Qwen3-4B with conventional generation | US$46,000 | 333 hours |
| Qwen3-4B with HPD | US$5,000 | 36 hours |

These figures are those the authors reported for their study configuration, not current cloud service quotes. The team also estimated about US$350 for a fine-tuning stage using eight A100 GPUs, without claiming that this covered all data and development costs.

The **92%** saving against the reference LLM stands out, but there is an essential distinction: fine-tuning alone did not produce it. HPD execution was decisive. The same Qwen3-4B generating attributes conventionally cost much more in the experiment.

This comparison shows why choosing a smaller model is only part of the solution. Output format and inference method can substantially change the cost of processing a catalog.

The study used English product text. Applying it directly to Portuguese catalogs requires a separate evaluation, especially when suppliers use incomplete descriptions or different unit conventions.

## What happens when the small model is wrong?

This is where many savings proposals stop being convincing.

An incorrect attribute can harm filters and comparisons. If the operation must manually review too many records, inference savings lose their value.

In October 2026, another EMNLP Industry Track paper, [*When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*](https://aclanthology.org/2026.emnlp-industry.187/), investigated how to choose which SLM answers to accept.

The solution considered both the model's confidence and the task it was performing. A model may frequently get one attribute right while often failing on another. A single confidence threshold applied to everything does not capture that difference well.

Using a selection mechanism that considers product type and attribute, the researchers accepted **11.4 percentage points more predictions** than with a global confidence threshold, while maintaining the same observed precision of **90.3%** at that evaluation point.

This does not mean the SLM became 11.4% more precise. The improvement was using more answers without lowering measured precision.

The operational implication matters. The small model can handle most of the volume while higher-risk cases go to review or another model. Not every error requires a larger LLM: sometimes the best decision is to leave a field unanswered until enough information exists.

You do not need the most expensive model for every product. You need to know **when the cheaper answer can be used**.

## How can you tell whether fine-tuning pays off for your marketplace?

Start with a category that receives many products and generates recurring work to populate or correct fields. Measure a defined task before expanding the solution to the whole catalog.

Separate products into training, validation, and test sets. Keep products unseen during adaptation in the test set and include descriptions representing current traffic. Otherwise, results may look better than they will in operation.

Compare the existing system with an unadapted SLM and the same SLM after fine-tuning. If HPD or another inference technique is of interest, compare it separately. This distinguishes improvements caused by training from those caused by execution.

Next, evaluate results per attribute, not just per product. Average accuracy can hide failures concentrated in commercially important fields. Also measure how many records need review and how many remain unfilled.

The economic metric should include the cost of delivering a correct, approved attribute, not just generating an answer:

**Cost per approved attribute = (inference + review + correction + infrastructure + amortized training) ÷ number of correctly approved attributes.**

All costs must cover the same period. Spread training cost across the volume you expect to process before another adaptation.

This calculation avoids a common mistake: assuming a model costs less because its GPU is cheaper, without counting the work needed to correct its outputs.

For an operation with frequent updates and high volume, an adapted SLM tends to be a particularly interesting option. The initial investment can be spread across many extractions. A low-volume catalog, however, may not generate enough savings to justify dedicated infrastructure.

The criterion for moving forward is objective. If the SLM delivers the required attributes, keeps errors within the operation's limits, and reduces cost per approved attribute, there is a basis for expanding its use.

## The next efficiency gain may be in your catalog, not a larger LLM

The 2026 studies show that product enrichment with small models is no longer just a laboratory possibility. There are deployment results, cost comparisons, and methods for deciding which answers can be used.

The numbers are substantial: **an estimated 98% reduction in inference cost in one study and 92% in another**. They came from different conditions and should not be treated as a promise of savings for every marketplace.

The conclusion that matters is different. When the work involves extracting attributes from millions of products, it makes sense to start by specializing a smaller model, measuring its quality, and optimizing how it performs the task. Keeping a general-purpose LLM at every stage may mean continually paying for capabilities the operation does not use.

If your company needs to evaluate this decision with its own data, volume, and quality requirements, Huyawo Solutions works on model selection and adaptation for business problems. Contact takes place in writing.

### Studies and documentation consulted

1. [Kolasani and Dezaki, *Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*, ACL Industry Track, July 2026](https://aclanthology.org/2026.acl-industry.40/).
2. [Vedula and colleagues, *Scaling E-Commerce Attribute Extraction with Parallel Decoding*, AKBC, October 2026](https://aclanthology.org/2026.akbc-1.13/).
3. [Mansoori and colleagues, *When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*, EMNLP Industry Track, October 2026](https://aclanthology.org/2026.emnlp-industry.187/).
4. [Hugging Face, LoRA documentation in PEFT](https://huggingface.co/docs/peft/v0.21.0/conceptual_guides/lora).
