# Iterative Large Language Model - Guided Sampling and Expert-Annotated Benchmark Corpus for Harmful Suicide Content Detection: Development and Validation of a Benchmark Dataset

## Overview
This repo provides source code, dataset explanations and instructions on how to apply for the Harmful Suicide Content Detection Benchmark (through data usage agreement).
This repo corresponds to the paper: Iterative LLM-Guided Sampling and Expert-annotated Benchmark Corpus for Harmful Suicide Content Detection (preprint, JMIR Medical Informatics, DOI: 10.2196/73725) – see https://preprints.jmir.org/preprint/73725

## Abstract
Harmful suicide content on the Internet is a significant risk factor inducing suicidal thoughts and behaviors among vulnerable populations.
Despite global efforts, existing resources are insufficient, specifically in high-risk regions like the Republic of Korea. Current research mainly focuses on understanding negative effects of such content or suicide risk in individuals, rather than on automatically detecting the harmfulness of content.
To fill this gap, we introduce a harmful suicide content detection task for classifying online suicide content into five harmfulness levels.
We develop a multi-modal harmful suicide content detection benchmark and a task description document in collaboration with medical professionals, and leverage large language models (LLMs) to explore efficient methods for moderating such content. Our contributions include proposing a novel detection task, a multi-modal Korean benchmark with expert annotations, and suggesting strategies using LLMs to detect illegal and harmful content.
Owing to the potential harm involved, we publicize our implementations and benchmark, incorporating an ethical verification process.

## Data Usage Agreements
The Harmful Suicide Content Detection benchmark contains only publicly available web user posts (e.g., Twitter, Korean Reddit (DCInside), etc). Posts may contain information related to users' mental health, however, and are thus sensitive. To protect users' privacy, researchers who wish to obtain the dataset must sign a data usage agreement.
Succinctly, the agreement requires that researchers
* make no attempt to contact any user in the dataset
* make no attempt to deanonymize or learn the identity of any user in the dataset
* make no attempt to link users in the dataset with any external information (e.g., an account on another website)
* do not share any portion of the data, including example posts or excerpts from posts, with any other party

Researchers interested in obtaining the Harmful Suicide Content Detection benchmark may submit **a data request form to be provided with the data usage agreement [google form link]** with **IRB document**.

## Data Records

| **Column Name**          | **Description**                                                                                                                                                                                                                                                | **Data Type** |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| **Input Attributes**      |                                                                                                                                                                                                                                                            |               |
| id                        | Data identifier                                                                                                                                                                                                                                             | String        |
| content_text              | Text written in the user-generated content.                                                                                                                                                                                                                | String        |
| link_description          | Description of URL content contained in the user-generated content. Some user-generated contents include an external link (URL) and mention its content in the user-generated content; therefore, the content of the URL is considered.                   | String        |
| content_image_filename    | The filename of the image file which are written in user-generated content. All the images are in the 'image' directory.                                                                                                                                    | String        |
| image_description         | Description of the images included in the user-generated content. Some posts contain images owing to the nature of social media; therefore, images are considered together with the text to decide.                                                        | String        |
| context                   | Posts written before the target post (user-generated content). Some posts are part of a communication event; therefore, prior posts are considered when making a decision.                                                                                  | String        |
| - TWITTER                 | The text of tweets written before the user-generated content was written within the thread where it was posted.                                                                                                                                            | String        |
| - NAVER                   | For content_text being an answer on a QA platform, the original question post or comments on the article where the answer is posted are included.                                                                                                           | String        |
| - COUNSELLING             | For content_text, the question post where the answer is written is included as the counselor's answer.                                                                                                                                                     | String        |
| - LIFELINE                | -                                                                                                                                                                                                                                                          | None          |
| - DCINSIDE                | -                                                                                                                                                                                                                                                          | None          |
| source                    | The source from which the content_text was collected. There are a total of five sources: Twitter, Naver, Counselling, Lifeline, and DCinside.                                                                                                               | String        |
| source_meta               | Information provided about a user-generated content in a particular source, such as the number of views, likes, and the account description of the post's author. This information varies depending on the source.                                           | Dict          |
| **Output Attributes**     |                                                                                                                                                                                                                                                            |               |
| human_labels              | Category, subcategory, and rationale labels annotated by medical experts.                                                                                                                                                                                  | Dict          |
| - label_category          | Category of the suicide content post. User-generated contents are divided into five categories depending on whether they are harmful or illegal. It also considers how the posts will affect other users.                                                  | String        |
| - label_subcategory       | A subitem of a category is a finer classification depending on the content of user-generated content. User-generated content with different types of content can belong to the same category; therefore, they can be further subdivided into different subcategories. | String        |
| - label_rationale         | An explanation for why the expert classified the post on its label (the category and subcategory). Rationales are needed so that people without medical knowledge can clearly understand the reasons for classification. Rationales should explain medical terminology to a level that a layperson can understand, but be concise for good readability. | String        |

## Data Request and Review Process

Researchers interested in obtaining the Harmful Suicide Content Detection benchmark may submit a data request form, along with their IRB documentation, through the provided Google Form link.
All requests will be manually reviewed by the authors to ensure compliance with ethical and privacy considerations.

If you do not receive any response or follow-up within two weeks after submission, please contact Prof. JinYeong Bak (jy.bak@skku.edu) directly so that we can review your request in a timely manner.

## Citation


[google form link]: https://forms.gle/HAccC2xkzAvsS94x6
