<!--
This is a committed snapshot of a real `python evaluate.py` run, kept so the
evaluation results are visible on GitHub without requiring a local Ollama +
model setup to reproduce. It is NOT regenerated automatically — `evaluate.py`
always writes to `eval/last_report.md` (gitignored) instead. Update this file
by hand (copy from `eval/last_report.md`) if you want to refresh the snapshot.
-->

# Evaluation report (20 questions)

- Retrieval — Recall@5: **95%**, MRR: **0.90**
- Generation — Correctness: **80%**, Faithfulness: **80%**

## Breakdown by language

English questions are asked against the English document, Vietnamese questions against the Vietnamese document (independent question sets, not translations of each other) — this compares how well the pipeline performs end-to-end when working entirely in one language vs. the other.

| Language | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| en | 100% | 1.00 | 90% | 90% |
| vi | 90% | 0.80 | 70% | 70% |

| # | Language | Question | Retrieved | Rank | Correct | Faithful |
|---|---|---|---|---|---|---|
| 1 | en | According to Hands-On Large Language Models, which AI model was the first system able to write articles indistinguishable from those written by humans? | yes | 1 | yes | yes |
| 2 | en | According to Hands-On Large Language Models, what term does the book use to encompass technologies that may not technically be LLMs but still significantly impact the field? | yes | 1 | yes | yes |
| 3 | en | According to Hands-On Large Language Models, what was the first technique in the history of Language AI used to represent unstructured text, and around what decade was it first mentioned? | yes | 1 | no | no |
| 4 | en | According to Hands-On Large Language Models, which 2013 model was one of the first successful attempts at capturing the meaning of text in embeddings? | yes | 1 | yes | yes |
| 5 | en | According to Hands-On Large Language Models, why is the word "bank" used as an example of a limitation of word2vec's static embeddings? | yes | 1 | yes | yes |
| 6 | en | According to Hands-On Large Language Models, what term describes an architecture where generating the next word requires consuming all previously generated words? | yes | 1 | yes | yes |
| 7 | en | According to Hands-On Large Language Models, in what year was the solution called "attention" introduced to address the difficulty of handling longer sentences with a single context embedding? | yes | 1 | yes | yes |
| 8 | en | According to Hands-On Large Language Models, which 2017 paper introduced the Transformer architecture? | yes | 1 | yes | yes |
| 9 | en | According to Hands-On Large Language Models, why does the self-attention layer in the Transformer's decoder mask future positions? | yes | 1 | yes | yes |
| 10 | en | According to Hands-On Large Language Models, in what year was BERT introduced? | yes | 1 | yes | yes |
| 11 | vi | Theo sách Machine Learning cơ bản, Phần I của cuốn sách có tiêu đề là gì? | no | - | no | no |
| 12 | vi | Theo sách Machine Learning cơ bản, ký hiệu nào được dùng để biểu diễn phép chuyển vị (transpose) của một vector hoặc ma trận? | yes | 2 | yes | yes |
| 13 | vi | Theo sách Machine Learning cơ bản, phép nhân ma trận có tính chất giao hoán hay không? | yes | 1 | yes | yes |
| 14 | vi | Theo sách Machine Learning cơ bản, tập hợp tất cả các vector biểu diễn được dưới dạng tổ hợp tuyến tính của các cột một ma trận được gọi là gì? | yes | 1 | no | no |
| 15 | vi | Theo sách Machine Learning cơ bản, một hệ vector được gọi là "cơ sở" (basis) của một không gian vector khi thoả mãn những điều kiện nào? | yes | 1 | yes | yes |
| 16 | vi | Theo sách Machine Learning cơ bản, hạng (rank) của một ma trận có bằng với hạng của ma trận chuyển vị của nó không? | yes | 1 | yes | yes |
| 17 | vi | Theo sách Machine Learning cơ bản, một ma trận U thoả mãn UU^T = U^T U = I được gọi là ma trận gì? | yes | 1 | yes | yes |
| 18 | vi | Theo sách Machine Learning cơ bản, cách biểu diễn một ma trận A dưới dạng A = XΛX^-1 được gọi là gì? | yes | 1 | yes | yes |
| 19 | vi | Theo sách Machine Learning cơ bản, mọi ma trận Hermitian nửa xác định dương có thể biểu diễn duy nhất dưới dạng A = LL^H — đây là phép khai triển gì? | yes | 1 | no | no |
| 20 | vi | Theo sách Machine Learning cơ bản, chuẩn l1 (l1 norm) của một vector x được tính như thế nào? | yes | 2 | yes | yes |
