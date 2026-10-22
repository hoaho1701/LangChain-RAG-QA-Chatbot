<!--
This is a committed snapshot of a real `python evaluate.py` run, kept so the
evaluation results are visible on GitHub without requiring a local Ollama +
model setup to reproduce. It is NOT regenerated automatically — `evaluate.py`
always writes to `eval/last_report.md` (gitignored) instead. Update this file
by hand (copy from `eval/last_report.md`) if you want to refresh the snapshot.

This snapshot: `evaluate.py --split all`, answering model qwen3.5:9b, judge
gemma4:12b, all 72 questions (52 dev + 20 test). A second run with the judge
phi4:14b gave identical answers and retrieval; its numbers are in the
cross-check section below.
-->

# Evaluation report (72 questions, all split)

- Retrieval — Recall@5: **97%**, MRR: **0.89** (60 questions that have evidence)
- Generation — Correctness: **97%**, Faithfulness: **96%**, median 31 s per answer


## By language

| Language | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| en | 97% | 0.94 | 97% | 97% |
| vi | 97% | 0.84 | 97% | 94% |

## By type

| Type | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| distractor | 83% | 1.00 | 100% | 83% |
| factoid | 95% | 0.90 | 95% | 95% |
| follow_up | 100% | 0.78 | 100% | 100% |
| hard | 100% | 0.86 | 92% | 92% |
| out_of_doc | - | - | 100% | 100% |
| paraphrase | 100% | 0.83 | 100% | 100% |
| synthesis | 100% | 0.95 | 100% | 100% |

## By split

| Split | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| dev | 98% | 0.89 | 98% | 96% |
| test | 94% | 0.90 | 95% | 95% |

English questions are asked against the English document, Vietnamese questions against the Vietnamese
document (independent question sets, not translations of each other).

## Cross-check with a second judge

The same 72 answers were graded again by `phi4:14b` (another model family). The answers and the retrieval results were identical in both runs; only the grading differs.

| | gemma4:12b (main) | phi4:14b (cross-check) |
|---|---|---|
| Correctness, all 72 | 97% (70/72) | 96% (69/72) |
| Faithfulness, all 72 | 96% (69/72) | 97% (70/72) |
| Correctness, test (20) | 95% (19/20) | 90% (18/20) |
| Faithfulness, test (20) | 95% (19/20) | 100% (20/20) |

The two judges agree on 71 of 72 questions for correctness and on 69 of 72 for faithfulness (the disagreements are one question for correctness and three for faithfulness).

## How to read these numbers

- The questions and reference answers were written with an AI assistant, not by independent human annotators, and the judges are language models.
- The set is small: 72 questions, of which 20 form the `test` split. One question is worth about 1.4 points overall and 5 points on `test`, so differences of a point or two are noise.
- The `dev` questions were used to choose which changes to keep; the `test` questions were run once, at the end, and nothing was tuned after seeing them.
- Faithfulness counts an answer that says the information cannot be found as faithful.

| # | Id | Question | Retrieved | Rank | Correct | Faithful | Seconds |
|---|---|---|---|---|---|---|---|
| 1 | factoid-en-01 | According to Hands-On Large Language Models, which AI model was the first system able to write articles indistinguishable from those written by humans? | yes | 1 | yes | yes | 19.2 |
| 2 | factoid-en-02 | According to Hands-On Large Language Models, what term does the book use to encompass technologies that may not technically be LLMs but still significantly impact the field? | yes | 1 | yes | yes | 24.8 |
| 3 | factoid-en-03 | According to Hands-On Large Language Models, what was the first technique in the history of Language AI used to represent unstructured text, and around what decade was it first mentioned? | yes | 1 | yes | yes | 24.8 |
| 4 | factoid-en-04 | According to Hands-On Large Language Models, which 2013 model was one of the first successful attempts at capturing the meaning of text in embeddings? | yes | 1 | yes | yes | 24.1 |
| 5 | factoid-en-05 | According to Hands-On Large Language Models, why is the word "bank" used as an example of a limitation of word2vec's static embeddings? | yes | 1 | yes | yes | 23.9 |
| 6 | factoid-en-06 | According to Hands-On Large Language Models, what term describes an architecture where generating the next word requires consuming all previously generated words? | yes | 1 | yes | yes | 23.6 |
| 7 | factoid-en-07 | According to Hands-On Large Language Models, in what year was the solution called "attention" introduced to address the difficulty of handling longer sentences with a single context embedding? | yes | 1 | yes | yes | 23.5 |
| 8 | factoid-en-08 | According to Hands-On Large Language Models, which 2017 paper introduced the Transformer architecture? | yes | 1 | yes | yes | 24.2 |
| 9 | factoid-en-09 | According to Hands-On Large Language Models, why does the self-attention layer in the Transformer's decoder mask future positions? | yes | 1 | yes | yes | 22.9 |
| 10 | factoid-en-10 | According to Hands-On Large Language Models, in what year was BERT introduced? | yes | 1 | yes | yes | 23.2 |
| 11 | factoid-vi-01 | Theo sách Machine Learning cơ bản, Phần I của cuốn sách có tiêu đề là gì? | no | - | no | yes | 28.9 |
| 12 | factoid-vi-02 | Theo sách Machine Learning cơ bản, ký hiệu nào được dùng để biểu diễn phép chuyển vị (transpose) của một vector hoặc ma trận? | yes | 2 | yes | yes | 35.6 |
| 13 | factoid-vi-03 | Theo sách Machine Learning cơ bản, phép nhân ma trận có tính chất giao hoán hay không? | yes | 1 | yes | yes | 32.1 |
| 14 | factoid-vi-04 | Theo sách Machine Learning cơ bản, tập hợp tất cả các vector biểu diễn được dưới dạng tổ hợp tuyến tính của các cột một ma trận được gọi là gì? | yes | 1 | yes | yes | 31.6 |
| 15 | factoid-vi-05 | Theo sách Machine Learning cơ bản, một hệ vector được gọi là "cơ sở" (basis) của một không gian vector khi thoả mãn những điều kiện nào? | yes | 1 | yes | yes | 34.2 |
| 16 | factoid-vi-06 | Theo sách Machine Learning cơ bản, hạng (rank) của một ma trận có bằng với hạng của ma trận chuyển vị của nó không? | yes | 1 | yes | yes | 30.8 |
| 17 | factoid-vi-07 | Theo sách Machine Learning cơ bản, một ma trận U thoả mãn UU^T = U^T U = I được gọi là ma trận gì? | yes | 1 | yes | no | 31.1 |
| 18 | factoid-vi-08 | Theo sách Machine Learning cơ bản, cách biểu diễn một ma trận A dưới dạng A = XΛX^-1 được gọi là gì? | yes | 1 | yes | yes | 30.3 |
| 19 | factoid-vi-09 | Theo sách Machine Learning cơ bản, mọi ma trận Hermitian nửa xác định dương có thể biểu diễn duy nhất dưới dạng A = LL^H — đây là phép khai triển gì? | yes | 1 | yes | yes | 33.9 |
| 20 | factoid-vi-10 | Theo sách Machine Learning cơ bản, chuẩn l1 (l1 norm) của một vector x được tính như thế nào? | yes | 2 | yes | yes | 39.8 |
| 21 | synthesis-en-01 | How does a bag-of-words model turn sentences into numerical representations, according to the book? | yes | 1 | yes | yes | 31.6 |
| 22 | synthesis-en-02 | What is the difference between the embeddings that bag-of-words and word2vec create? | yes | 1 | yes | yes | 24.2 |
| 23 | synthesis-en-03 | What are the two parts of a Transformer encoder block, and how does self-attention differ from the earlier attention? | yes | 1 | yes | yes | 26.1 |
| 24 | synthesis-en-04 | What is the [CLS] token in BERT and how is it used? | yes | 1 | yes | yes | 23.7 |
| 25 | synthesis-en-05 | What happened in 2022 and 2023 that changed Language AI, according to the book? | yes | 1 | yes | yes | 28.2 |
| 26 | synthesis-vi-01 | Tích của hai ma trận vuông khả nghịch có khả nghịch không, và nghịch đảo của tích được tính thế nào? | yes | 2 | yes | yes | 31.1 |
| 27 | synthesis-vi-02 | Điều kiện nào về định thức cho biết một ma trận là khả nghịch, và định thức của ma trận nghịch đảo bằng bao nhiêu? | yes | 1 | yes | yes | 33.2 |
| 28 | synthesis-vi-03 | Trị riêng của ma trận vuông liên hệ với đa thức đặc trưng như thế nào, và tập hợp các trị riêng được gọi là gì? | yes | 1 | yes | yes | 30.4 |
| 29 | synthesis-vi-04 | Trị riêng của ma trận đối xứng (Hermitian) có đặc điểm gì và vì sao? | yes | 1 | yes | yes | 40.4 |
| 30 | synthesis-vi-05 | Ma trận A = [[1, -1], [-1, 1]] có xác định dương không? Giải thích. | yes | 1 | yes | yes | 43.7 |
| 31 | follow-up-en-01 | How does it learn those embeddings? | yes | 4 | yes | yes | 28.4 |
| 32 | follow-up-en-02 | And how do its embeddings differ from those of word2vec? | yes | 1 | yes | yes | 27.0 |
| 33 | follow-up-en-03 | What are the two parts of its encoder block? | yes | 1 | yes | yes | 22.0 |
| 34 | follow-up-en-04 | What does its [CLS] token do? | yes | 1 | yes | yes | 24.0 |
| 35 | follow-up-vi-01 | Nó thường được dùng để làm gì? | yes | 1 | yes | yes | 40.1 |
| 36 | follow-up-vi-02 | Ma trận đơn vị có phải là ma trận đường chéo không? | yes | 2 | yes | yes | 40.1 |
| 37 | follow-up-vi-03 | Còn tổng của tất cả các trị riêng thì sao? | yes | 2 | yes | yes | 31.0 |
| 38 | follow-up-vi-04 | Vậy định thức của ma trận nghịch đảo của nó bằng bao nhiêu? | yes | 1 | yes | yes | 34.0 |
| 39 | out-of-doc-en-01 | According to the book, how many encoder blocks does the BERT large model have? | - | - | yes | yes | 43.0 |
| 40 | out-of-doc-en-02 | What is the capital of France? | - | - | yes | yes | 40.3 |
| 41 | out-of-doc-en-03 | What dropout rate does the book use when training a Transformer? | - | - | yes | yes | 33.3 |
| 42 | out-of-doc-en-04 | In which year was GPT-4 released, according to the book? | - | - | yes | yes | 37.6 |
| 43 | out-of-doc-en-05 | Which optimizer does the book use to train neural networks, such as SGD? | - | - | yes | yes | 26.7 |
| 44 | out-of-doc-en-06 | How many parameters does GPT-2 have? | - | - | yes | yes | 35.5 |
| 45 | out-of-doc-vi-01 | Thủ đô của nước Pháp là gì? | - | - | yes | yes | 38.0 |
| 46 | out-of-doc-vi-02 | Định lý Cayley-Hamilton phát biểu điều gì? | - | - | yes | yes | 47.8 |
| 47 | out-of-doc-vi-03 | Dropout được dùng để làm gì trong mạng neural? | - | - | yes | yes | 40.8 |
| 48 | out-of-doc-vi-04 | Ma trận Jordan là gì? | - | - | yes | yes | 47.1 |
| 49 | out-of-doc-vi-05 | Thuật toán k-means hoạt động như thế nào? | - | - | yes | yes | 47.2 |
| 50 | out-of-doc-vi-06 | Phương pháp bình phương tối thiểu dùng để làm gì? | - | - | yes | yes | 43.5 |
| 51 | hard-en-01 | Why does the book say bag-of-words is not completely obsolete, and what flaw of it did word2vec address? | yes | 1 | yes | yes | 28.6 |
| 52 | hard-en-02 | In the book's description of word2vec training, how many values does each word's initial embedding have in the example, how are they initialised, and what prediction task is the network trained on? | yes | 1 | yes | yes | 25.5 |
| 53 | hard-en-03 | Which use cases of embeddings does the book mention, and in which chapters are they covered? | yes | 1 | no | yes | 24.9 |
| 54 | hard-en-04 | In the book's Dutch translation example, why is the attention between 'lama's' and 'llamas' high while the attention between 'lama's' and 'I' is lower? | yes | 1 | yes | yes | 24.4 |
| 55 | hard-en-05 | Why does the book say smaller models are still relevant even though LLMs got almost all the attention? | yes | 1 | yes | yes | 26.0 |
| 56 | hard-en-06 | A colleague says the Transformer processes tokens strictly one at a time, like an RNN. According to the book, is that right? | yes | 2 | yes | yes | 29.4 |
| 57 | hard-vi-01 | Nếu ma trận hệ số A không khả nghịch, thậm chí không vuông, thì phương trình Ax = b có thể có những khả năng nào về nghiệm? | yes | 1 | yes | yes | 32.8 |
| 58 | hard-vi-02 | Định thức bằng 0 trong trường hợp nào theo cuốn sách, và điều đó cho biết gì về tính khả nghịch của ma trận? | yes | 2 | yes | yes | 30.3 |
| 59 | hard-vi-03 | Range của ma trận A là gì và số chiều của nó bằng bao nhiêu? | yes | 1 | yes | yes | 32.1 |
| 60 | hard-vi-04 | Nêu các tính chất của nghịch đảo và định thức của ma trận trực giao. | yes | 1 | yes | yes | 33.6 |
| 61 | hard-vi-05 | Nếu (λ, x) là một cặp trị riêng, vector riêng của ma trận khả nghịch A thì A^-1 có cặp trị riêng, vector riêng nào? | yes | 1 | yes | no | 76.7 |
| 62 | hard-vi-06 | Một bạn nói rằng định thức của một ma trận khả nghịch có thể bằng 0. Theo cuốn sách, điều đó có đúng không? | yes | 3 | yes | yes | 31.7 |
| 63 | paraphrase-en-01 | What kind of numeric vector does a model assign to a word so that words appearing in similar surroundings end up close together? | yes | 3 | yes | yes | 28.4 |
| 64 | paraphrase-en-02 | What single fixed summary of the whole input sentence caused trouble for long sentences in the early encoder-decoder networks? | yes | 1 | yes | yes | 23.4 |
| 65 | distractor-en-01 | Around which decade did bag-of-words become popular, as opposed to when it was first mentioned? | yes | 1 | yes | yes | 21.8 |
| 66 | distractor-en-02 | In which chapter does the book say retrieval-augmented generation is covered, and in which chapters are classification and clustering covered? | yes | 1 | yes | yes | 28.7 |
| 67 | distractor-en-03 | Where does the book say it will go in depth about tokenization, and where does it say it will take its first deep dive into token embeddings? | no | 1 | yes | no | 27.4 |
| 68 | paraphrase-vi-01 | Có cách nào giải hệ phương trình có ma trận hệ số dạng tam giác mà không cần tính ma trận nghịch đảo không? | yes | 1 | yes | yes | 37.7 |
| 69 | paraphrase-vi-02 | Với ma trận vuông A, khi nào phương trình Ax = b chắc chắn có nghiệm duy nhất với mọi b, và nghiệm đó viết thế nào? | yes | 1 | yes | yes | 32.7 |
| 70 | distractor-vi-01 | Trị riêng của ma trận xác định dương khác gì so với trị riêng của ma trận đối xứng nói chung? | yes | 1 | yes | yes | 34.1 |
| 71 | distractor-vi-02 | Chuẩn ℓ2 khác chuẩn ℓ1 thế nào về công thức và cách diễn giải khoảng cách? | yes | 1 | yes | yes | 43.2 |
| 72 | distractor-vi-03 | Theo mục về chuẩn, để xác định khoảng cách giữa hai vector y và z người ta làm thế nào? | yes | 1 | yes | yes | 33.1 |
