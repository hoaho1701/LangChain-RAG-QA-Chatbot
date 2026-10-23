<!--
This is a committed snapshot of a real `python -m eval.evaluate` run, kept so the
evaluation results are visible on GitHub without requiring a local Ollama +
model setup to reproduce. It is NOT regenerated automatically — `eval.evaluate`
always writes to `eval/last_report.md` (gitignored) instead. Update this file
by hand (copy from `eval/last_report.md`) if you want to refresh the snapshot.

This snapshot: `VECTOR_DB_PATH=data/eval_index python -m eval.evaluate --split all`, answering
model qwen3.5:9b, judge gemma4:12b, all 150 questions (49 dev + 101 test) about four documents
(1967 chunks, built with `python -m eval.build_index`). A second run with the judge phi4:14b gave
identical answers and retrieval; its numbers are in the cross-check section below.
-->

# Evaluation report (150 questions, all split)

- Retrieval — Recall@5: **96%**, MRR: **0.90** (135 questions that have evidence)
- Generation — Correctness: **96%**, Faithfulness: **97%**, median 27 s per answer


## By language

| Language | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| en | 97% | 0.91 | 97% | 97% |
| vi | 96% | 0.89 | 95% | 97% |

## By type

| Type | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| compare_list | 90% | 0.90 | 100% | 100% |
| cross_lingual | 90% | 0.90 | 90% | 80% |
| distractor | 100% | 0.90 | 100% | 100% |
| explain | 100% | 0.95 | 80% | 87% |
| factoid | 100% | 0.97 | 100% | 100% |
| follow_up | 100% | 0.92 | 100% | 100% |
| multihop | 100% | 0.92 | 93% | 100% |
| numeric | 100% | 0.96 | 100% | 100% |
| out_of_doc | - | - | 100% | 100% |
| paraphrase | 100% | 0.94 | 100% | 100% |
| table_formula_code | 100% | 0.83 | 100% | 100% |
| typo_short | 62% | 0.43 | 88% | 100% |

## By split

| Split | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| dev | 95% | 0.86 | 90% | 94% |
| test | 97% | 0.92 | 99% | 99% |

## By doc

| Doc | Recall@k | MRR | Correctness | Faithfulness |
|---|---|---|---|---|
| bien-doi-khi-hau-wikipedia | 97% | 0.97 | 94% | 100% |
| hands-on-llms | 95% | 0.86 | 100% | 100% |
| ml-co-ban | 97% | 0.85 | 93% | 95% |
| photosynthesis-wikipedia | 97% | 0.94 | 97% | 94% |

English questions are asked against the English document, Vietnamese questions against the Vietnamese
document (independent question sets, not translations of each other).

## Cross-check with a second judge

The same 150 answers were graded again by `phi4:14b` (another model family). The answers and the retrieval results were identical in both runs (150 of 150 answers word for word); only the grading differs.

| | gemma4:12b (main) | phi4:14b (cross-check) |
|---|---|---|
| Correctness, all 150 | 96% (144/150) | 95% (142/150) |
| Faithfulness, all 150 | 97% (146/150) | 97% (145/150) |
| Correctness, dev (49) | 90% (44/49) | 96% (47/49) |
| Correctness, test (101) | 99% (100/101) | 94% (95/101) |
| Faithfulness, dev (49) | 94% (46/49) | 96% (47/49) |
| Faithfulness, test (101) | 99% (100/101) | 97% (98/101) |

The two judges agree on 142 of 150 questions for correctness (95%) and on 141 of 150 for faithfulness (94%). The disagreements go both ways: for correctness `gemma4:12b` said yes and `phi4:14b` no on 5 questions, and the other way round on 3.

The `dev` and `test` rows change order with the judge (`gemma4:12b` finds `test` easier, `phi4:14b` finds `dev` easier), so the gap between the two splits in the main run is grading noise, not evidence that one split is harder.

## How much these numbers can move

With so few questions a percentage is only an estimate. The table gives a 95% confidence interval (Wilson) for the main results of the run graded by `gemma4:12b`: the range in which the true rate, over many similar questions, most likely lies.

| Metric | Result | 95% interval |
|---|---|---|
| Correctness, all 150 | 96% (144/150) | 92% to 98% |
| Faithfulness, all 150 | 97% (146/150) | 93% to 99% |
| Recall@5, 135 questions with evidence | 96% (130/135) | 92% to 98% |
| Correctness, dev (49) | 90% (44/49) | 78% to 96% |
| Correctness, test (101) | 99% (100/101) | 95% to 100% |
| Faithfulness, test (101) | 99% (100/101) | 95% to 100% |

The same intervals for the `phi4:14b` grading are 90% to 97% for correctness and 92% to 99% for faithfulness on all 150 questions. Two results whose intervals overlap, such as 96% and 95% here, cannot be told apart on this many questions.

## Where the pipeline is weak

- `typo_short` (8 questions): Recall@5 is 62% and MRR 0.43. The three misses are two Vietnamese questions typed without diacritics and one English question with misspelled words; short, misspelled queries match the right passage less reliably.
- `explain` (15): Correctness is 80% (3 questions judged wrong by `gemma4:12b`).
- `cross_lingual` (10): Faithfulness is 80% (2 answers judged to go beyond the context).
- When no passage is relevant the pipeline rewrites the question once and tries again; the rewritten question is sometimes longer and invents details, and it did not rescue the one in-document question that needed it (`typo-short-08`).
- Each group has 6 to 25 questions, so a difference between groups is a hint, not a result.

## How to read these numbers

- The questions and reference answers were written with an AI assistant, not by independent human annotators, and the judges are language models.
- The set is small: 150 questions, of which 101 form the `test` split. One question is worth about 0.7 points overall and 1 point on `test`; a group of 10 questions moves 10 points per question.
- The `dev` questions were used to choose which changes to keep; the `test` questions were run once, at the end, and nothing was tuned after seeing them.
- Faithfulness counts an answer that says the information cannot be found as faithful.
- The questions are about four documents: two complete books and two Wikipedia articles (fixed copies). Earlier snapshots used 72 questions about the first 80 book pages and cannot be compared with this one.

| # | Id | Question | Retrieved | Rank | Correct | Faithful | Seconds |
|---|---|---|---|---|---|---|---|
| 1 | factoid-01 | What vocabulary sizes are commonly used for an LLM tokenizer, according to the book? | yes | 1 | yes | yes | 17.7 |
| 2 | factoid-02 | Which embedding model does the book's clustering example use instead of all-mpnet-base-v2, and why? | yes | 1 | yes | yes | 22.6 |
| 3 | factoid-03 | In the book's word2vec example, what window size is used and what does it mean? | yes | 1 | yes | yes | 24.8 |
| 4 | factoid-04 | When a named entity is split into several tokens, which label does the first token get and which label do the following tokens get? | yes | 1 | yes | yes | 30.7 |
| 5 | factoid-05 | What does text clustering aim to do, according to the book? | yes | 1 | yes | yes | 26.2 |
| 6 | factoid-06 | What is the most common way to tokenize text in the bag-of-words model? | yes | 1 | yes | yes | 21.7 |
| 7 | factoid-07 | How does full fine-tuning differ from pretraining in the data it uses? | yes | 1 | yes | yes | 23.5 |
| 8 | factoid-08 | Vì sao kernel SVM dùng các hàm kernel thay vì tính trực tiếp hàm biến đổi Φ(x)? | yes | 1 | yes | yes | 44.2 |
| 9 | factoid-09 | Trong ví dụ logistic regression với dữ liệu hai chiều, màu nền trong hình kết quả thể hiện điều gì? | yes | 1 | yes | yes | 28.2 |
| 10 | factoid-10 | Định thức của một ma trận trực giao bằng bao nhiêu? | yes | 1 | yes | yes | 29.1 |
| 11 | factoid-11 | MAP estimation khác MLE ở điểm nào? | yes | 5 | yes | yes | 39.6 |
| 12 | factoid-12 | Trong bộ dữ liệu email của chương Naive Bayes, mỗi dòng của file features.txt có ba số, ý nghĩa của từng số là gì? | yes | 1 | yes | yes | 32.7 |
| 13 | factoid-13 | Trong SVM, bài toán gốc và bài toán đối ngẫu Lagrange mỗi bên phải tìm bao nhiêu tham số? | yes | 1 | yes | yes | 32.5 |
| 14 | factoid-14 | Vì sao các feature vector của mọi điểm dữ liệu trong cùng một bài toán thường phải có kích thước như nhau? | yes | 1 | yes | yes | 25.5 |
| 15 | factoid-15 | What does the photosynthetic action spectrum depend on, and what does it resemble in green plants? | yes | 1 | yes | yes | 20.8 |
| 16 | factoid-16 | What do the carboxysomes of cyanobacteria do, and which enzyme inside them releases CO2? | yes | 1 | yes | yes | 21.6 |
| 17 | factoid-17 | What are the four main factors influencing photosynthesis according to the article? | yes | 1 | yes | yes | 21.1 |
| 18 | factoid-18 | How does CAM metabolism separate CO2 fixation from the Calvin cycle, compared with C4 metabolism? | yes | 1 | yes | yes | 23.2 |
| 19 | factoid-19 | How many water molecules does photosystem II oxidize to yield one molecule of oxygen, and how many hydrogen ions result? | yes | 1 | yes | yes | 22.6 |
| 20 | factoid-20 | Who used radioactive isotopes to show that the oxygen released in photosynthesis comes from water? | yes | 1 | yes | yes | 20.7 |
| 21 | factoid-21 | Theo bài viết, một loạt hành động trong nông nghiệp và lâm nghiệp có thể giảm khí thải nhà kính bao nhiêu phần trăm so với năm 2010? | yes | 1 | yes | yes | 23.0 |
| 22 | factoid-22 | Nghị định thư Kyoto 1997 bổ sung điều gì so với UNFCCC? | yes | 1 | yes | yes | 21.9 |
| 23 | factoid-23 | Hiện nay đất nông nghiệp chiếm bao nhiêu phần trăm diện tích đất của Trái Đất? | yes | 1 | yes | yes | 20.7 |
| 24 | factoid-24 | Đến năm 2018, nồng độ CO2 và methane trong khí quyển đã tăng khoảng bao nhiêu phần trăm so với năm 1750? | yes | 1 | yes | yes | 22.0 |
| 25 | factoid-25 | Tổ chức Y tế Thế giới ước tính biến đổi khí hậu khiến thêm khoảng bao nhiêu người già tử vong mỗi năm do nắng nóng trong giai đoạn 2030 đến 2050? | yes | 1 | yes | yes | 22.2 |
| 26 | explain-01 | How does word2vec use a neural network to generate word embeddings, according to the book? | yes | 1 | yes | yes | 34.6 |
| 27 | explain-02 | How can you test the quality of the silver data used to augment the training of an embedding model? | yes | 1 | yes | yes | 26.6 |
| 28 | explain-03 | What is instruction-based prompting and what is it used for? | yes | 1 | yes | yes | 24.7 |
| 29 | explain-04 | Why does the book's supervised classification example separate feature extraction from classification, and what classifier does it train? | yes | 1 | yes | yes | 24.0 |
| 30 | explain-05 | Agglomerative hierarchical clustering hoạt động như thế nào? | yes | 1 | no | yes | 28.6 |
| 31 | explain-06 | Trong ví dụ minh họa K-means của chương 10, thuật toán hội tụ sau bao nhiêu vòng lặp và kết quả phân cụm ra sao? | yes | 1 | yes | yes | 40.9 |
| 32 | explain-07 | Vì sao việc biến dữ liệu thô như ảnh và văn bản thành đầu vào cho mô hình machine learning gặp khó khăn? | yes | 5 | yes | no | 37.8 |
| 33 | explain-08 | Một hàm kernel cần có những tính chất nào? | yes | 1 | yes | yes | 37.7 |
| 34 | explain-09 | How does photosynthesis relate to cellular respiration? | yes | 1 | yes | yes | 27.9 |
| 35 | explain-10 | What role did cyanobacteria and green algae play in producing oxygen over geological time? | yes | 1 | yes | yes | 30.5 |
| 36 | explain-11 | What does the article say about the first photosynthetic organisms and about the oxygen that cyanobacteria produced? | yes | 1 | no | no | 24.9 |
| 37 | explain-12 | How efficient is photosynthesis in plants, what happens to the light that is not converted, and how does it compare with solar panels? | yes | 1 | yes | yes | 24.1 |
| 38 | explain-13 | Giữa thích nghi và giảm thiểu biến đổi khí hậu có những sự đánh đổi nào? | yes | 1 | yes | yes | 30.0 |
| 39 | explain-14 | Theo bài viết, những phương pháp giảm thiểu biến đổi khí hậu nào đi kèm rủi ro cao hơn, và vì sao? | yes | 1 | no | yes | 31.2 |
| 40 | explain-15 | Vì sao hoạt động của Mặt trời và núi lửa không giải thích được sự ấm lên gần đây? | yes | 1 | yes | yes | 31.0 |
| 41 | multihop-01 | Why does lowering the number of bits used for an LLM's weights reduce memory, and by how much does an 8-bit variant of Phi-3 cut the memory needed compared with the original 16-bit variant? | yes | 1 | yes | yes | 28.0 |
| 42 | multihop-02 | Which decoding strategy corresponds to setting the temperature of an LLM to zero, and what do the temperature and top_p parameters control? | yes | 1 | yes | yes | 32.6 |
| 43 | multihop-03 | In the book's search example built on the Interstellar text, who wrote the screenplay, and which sentence got the highest BM25 score for the query 'how precise was the science'? | yes | 1 | yes | yes | 31.2 |
| 44 | multihop-04 | What are positional embeddings for, and how do rotary embeddings differ from the static absolute embeddings added at the beginning of the forward pass? | yes | 1 | yes | yes | 27.2 |
| 45 | multihop-05 | Softmax regression mở rộng mô hình nào cho bài toán phân lớp nhiều lớp, và khi số lớp C bằng 2 thì nó trở thành gì? | yes | 3 | yes | yes | 27.3 |
| 46 | multihop-06 | MAP dựa trên những thông tin nào ngoài tập huấn luyện, và MLE liên hệ với MAP như thế nào khi prior là một phân phối đều? | yes | 2 | yes | yes | 38.7 |
| 47 | multihop-07 | Tập huấn luyện và tập kiểm thử dùng để làm gì, và validation set giúp chọn mô hình như thế nào? | yes | 1 | yes | yes | 40.1 |
| 48 | multihop-08 | Trong bài toán canh tác, các đường nét đứt trong hình minh họa nghiệm thể hiện điều gì, và level set được định nghĩa như thế nào? | yes | 1 | no | yes | 31.9 |
| 49 | multihop-09 | Which important crop plants are C4 plants, and how many plant species use CAM? | yes | 1 | yes | yes | 26.1 |
| 50 | multihop-10 | Which scientists worked out the path of carbon assimilation, and what prize did Melvin Calvin receive for this work, and when? | yes | 1 | yes | yes | 22.4 |
| 51 | multihop-11 | Who first proposed the general equation of photosynthesis, and who proposed the term 'photosynthesis' itself, and in which year? | yes | 1 | yes | yes | 25.7 |
| 52 | multihop-12 | Which molecules made by the light-dependent reactions drive the Calvin cycle, and what are the simple carbon sugars it produces used for afterwards? | yes | 1 | yes | yes | 23.6 |
| 53 | multihop-13 | Những tác động nào của biến đổi khí hậu sẽ còn kéo dài hàng thế kỷ ngay cả khi hạn chế được sự ấm lên, và vì sao đại dương bị acid hóa? | yes | 1 | yes | yes | 29.8 |
| 54 | multihop-14 | Nguyên nhân chính của biến đổi khí hậu hiện nay là gì, và khoảng bao nhiêu phần lượng CO2 con người phát thải đã được thực vật mặt đất và đại dương hấp thụ? | yes | 1 | yes | yes | 26.6 |
| 55 | multihop-15 | Những khu vực nào chịu rủi ro lớn nhất từ biến đổi khí hậu, và những phương án thích nghi nào được nêu cho nông nghiệp? | yes | 1 | yes | yes | 28.8 |
| 56 | numeric-01 | How many parameters does Phi-3-mini have, and how much VRAM does the book say is enough to run it? | yes | 1 | yes | yes | 25.6 |
| 57 | numeric-02 | On how many books was GPT-1 trained, and how many parameters did the resulting model have? | yes | 1 | yes | yes | 24.3 |
| 58 | numeric-03 | According to the book, about how many parameters can a single weight matrix of an LLM have? | yes | 1 | yes | yes | 24.5 |
| 59 | numeric-04 | Bộ cơ sở dữ liệu CIFAR10 gồm bao nhiêu ảnh, bao nhiêu lớp, và mỗi ảnh có kích thước bao nhiêu? | yes | 1 | yes | yes | 32.2 |
| 60 | numeric-05 | Trong ví dụ gradient descent cho bài toán linear regression với learning rate bằng 1, thuật toán hội tụ sau bao nhiêu vòng lặp? | yes | 2 | yes | yes | 25.8 |
| 61 | numeric-06 | Ma trận dữ liệu mnist.data trong ví dụ K-means có kích thước bao nhiêu, tức bao nhiêu mẫu và mỗi mẫu có kích thước bao nhiêu? | yes | 1 | yes | yes | 30.4 |
| 62 | numeric-07 | At what CO2 concentration did C3 and C4 plants show similar leaf photosynthetic rates, and about what rate was it? | yes | 1 | yes | yes | 24.6 |
| 63 | numeric-08 | How old are the fossils thought to be filamentous photosynthetic organisms, and how old are the thylakoid membranes that give the first direct evidence of photosynthesis? | yes | 1 | yes | yes | 22.2 |
| 64 | numeric-09 | How many organisms using oxygenic photosynthesis are known to rely on shortwave infrared or far-red radiation for the light-dependent reactions? | yes | 1 | yes | yes | 20.4 |
| 65 | numeric-10 | James Hansen điều trần trước Quốc hội năm nào, và Ủy ban Liên chính phủ về Biến đổi Khí hậu được thành lập năm nào? | yes | 1 | yes | yes | 23.2 |
| 66 | numeric-11 | Bể chứa bề mặt đất ước tính loại bỏ khoảng bao nhiêu phần trăm khí thải CO2 toàn cầu mỗi năm, và các đại dương đã hấp thu bao nhiêu trong hai thập kỷ qua? | yes | 1 | yes | yes | 24.0 |
| 67 | numeric-12 | Nếu đạt được các mục tiêu của Hiệp định Paris, hạn chế ấm lên ở mức 2 °C có thể cứu khoảng bao nhiêu sinh mạng mỗi năm đến năm 2050? | yes | 1 | yes | yes | 21.9 |
| 68 | compare-list-01 | What two masking methods does the book mention for masked language modeling, and how do they differ? | no | - | yes | yes | 25.3 |
| 69 | compare-list-02 | How do ConversationBufferMemory and ConversationBufferWindowMemory differ in how they deal with a growing chat history? | yes | 1 | yes | yes | 35.0 |
| 70 | compare-list-03 | How is a confusion matrix built from correct and incorrect predictions? | yes | 1 | yes | yes | 27.0 |
| 71 | compare-list-04 | Vì sao cách tính đạo hàm numerical không được dùng để tính đạo hàm, dù cho giá trị khá chính xác? | yes | 1 | yes | yes | 32.3 |
| 72 | compare-list-05 | Trong bộ dữ liệu MovieLens của ví dụ, file u.data chứa gì và các file ua.base, ua.test, ub.base, ub.test dùng để làm gì? | yes | 1 | yes | yes | 37.6 |
| 73 | compare-list-06 | Việc tính giá trị hàm mất mát và đạo hàm của nó gồm những bước nào theo thứ tự? | yes | 1 | yes | yes | 36.8 |
| 74 | compare-list-07 | What are the steps of the light-dependent reactions, from the electron lost by chlorophyll to the formation of NADPH and ATP? | yes | 1 | yes | yes | 35.7 |
| 75 | compare-list-08 | How does the movement of the electron toward the photo center combine quantum and classical motion, and why is the quantum part limited? | yes | 1 | yes | yes | 27.0 |
| 76 | compare-list-09 | Các chiến lược giảm nhu cầu năng lượng khác nhau thế nào giữa vận tải, công nghiệp và xây dựng? | yes | 1 | yes | yes | 26.8 |
| 77 | compare-list-10 | Nhiệt độ tăng gây ra những hiện tượng nào trên đất liền và ở vùng Bắc cực? | yes | 1 | yes | yes | 27.6 |
| 78 | paraphrase-01 | What property of the early sequence-to-sequence translation networks makes every new word depend on all the words generated before it? | yes | 4 | yes | yes | 22.1 |
| 79 | paraphrase-02 | Why does the book advise starting from an already trained embedding model instead of building one from nothing when you want embeddings tuned to your own data? | yes | 1 | yes | yes | 23.1 |
| 80 | paraphrase-03 | What is the purpose of connecting a text-generating model to a search component? | yes | 1 | yes | yes | 23.3 |
| 81 | paraphrase-04 | Theo định nghĩa không chính thức, một tập hợp thỏa mãn điều kiện gì về đoạn thẳng nối hai điểm thì được coi là lồi? | yes | 1 | yes | yes | 30.3 |
| 82 | paraphrase-05 | Vì sao tính đạo hàm xấp xỉ bằng cách lấy chênh lệch ở cả hai phía của điểm lại tốt hơn chỉ lấy một phía? | yes | 1 | yes | yes | 32.4 |
| 83 | paraphrase-06 | Tên gọi của hiện tượng trong đó một phần nhỏ sản phẩm tạo ra phần lớn doanh số còn rất nhiều sản phẩm ít phổ biến chỉ đóng góp một chút là gì? | yes | 1 | yes | yes | 27.7 |
| 84 | paraphrase-07 | When did the ability to split water for photosynthesis arise, and in which group of organisms? | yes | 1 | yes | yes | 24.3 |
| 85 | paraphrase-08 | After an electron has entered photosystem I, what is the energy that it hands over along the chain of acceptors used for, and where does the electron end up? | yes | 1 | yes | yes | 22.2 |
| 86 | paraphrase-09 | Which five-carbon sugar takes up carbon dioxide during carbon fixation, and what does it turn into? | yes | 1 | yes | yes | 22.1 |
| 87 | paraphrase-10 | Việc thay đổi lớp phủ thực vật của một khu vực ảnh hưởng đến nhiệt độ khu vực đó qua những yếu tố nào? | yes | 1 | yes | yes | 31.5 |
| 88 | paraphrase-11 | Con người có thể giúp các hệ sinh thái thích ứng với khí hậu thay đổi bằng cách nào? | yes | 1 | yes | yes | 32.0 |
| 89 | paraphrase-12 | Việc dùng năng lượng sạch đem lại lợi ích nào cho sức khỏe con người thấy ngay, không phải đợi tương lai? | yes | 1 | yes | yes | 22.5 |
| 90 | distractor-01 | In the book's zero-shot classification with embeddings, how is a label assigned to a document? | yes | 2 | yes | yes | 27.3 |
| 91 | distractor-02 | What do you have to specify for the model to apply a JSON grammar so that its output adheres to the JSON format? | yes | 1 | yes | yes | 23.3 |
| 92 | distractor-03 | How is the representation learned by the Q-Former used by the LLM in BLIP-2? | yes | 2 | yes | yes | 30.5 |
| 93 | distractor-04 | Trong bài toán canh tác giải bằng CVXOPT, vì sao hàm mục tiêu được đổi sang dạng −5x−3y? | yes | 1 | yes | yes | 37.9 |
| 94 | distractor-05 | Trong ví dụ KNN với Iris flower dataset, bao nhiêu mẫu được chọn làm test set và bao nhiêu mẫu làm training set? | yes | 1 | yes | yes | 28.0 |
| 95 | distractor-06 | Laplace smoothing giải quyết hạn chế nào của cách tính xác suất trong Naive Bayes, và hệ số α thường bằng bao nhiêu? | yes | 1 | yes | yes | 34.7 |
| 96 | distractor-07 | How many chloroplasts does a typical plant cell contain, and what is the aqueous fluid enclosed by the chloroplast membrane called? | yes | 1 | yes | yes | 21.0 |
| 97 | distractor-08 | What catalyzes the oxidation of water in photosystem II, and which ions does it contain? | yes | 1 | yes | yes | 21.4 |
| 98 | distractor-09 | Ví dụ nào được nêu cho điểm tới hạn trong hệ thống khí hậu, và mức ấm lên nào có thể làm phiến băng tan chảy? | yes | 1 | yes | yes | 25.7 |
| 99 | distractor-10 | Các phản hồi củng cố chính và phản hồi cân bằng chính đối với sự gia tăng nhiệt độ bề mặt là gì? | yes | 1 | yes | yes | 24.5 |
| 100 | follow-up-01 | Does that approach have any downsides? | yes | 1 | yes | yes | 25.4 |
| 101 | follow-up-02 | What does it take as input and what does it produce? | yes | 1 | yes | yes | 27.4 |
| 102 | follow-up-03 | How many problems does it contain? | yes | 1 | yes | yes | 27.1 |
| 103 | follow-up-04 | Còn hàm lõm thì được định nghĩa thế nào? | yes | 1 | yes | yes | 32.3 |
| 104 | follow-up-05 | Nếu dữ liệu chỉ gần linearly separable thì nó gặp vấn đề gì? | yes | 1 | yes | yes | 30.8 |
| 105 | follow-up-06 | Còn khi dự đoán cho chiều cao 160cm thì kết quả ra sao? | yes | 1 | yes | yes | 31.8 |
| 106 | follow-up-07 | What happens when the carbon dioxide concentration is low? | yes | 1 | yes | yes | 29.5 |
| 107 | follow-up-08 | How does it travel to the reaction center? | yes | 2 | yes | yes | 24.2 |
| 108 | follow-up-09 | Which pigments do plants use for that? | yes | 2 | yes | yes | 28.0 |
| 109 | follow-up-10 | Ông công bố vào năm nào và tính ra điều gì khi lượng CO2 tăng gấp đôi? | yes | 1 | yes | yes | 26.3 |
| 110 | follow-up-11 | Trong giai đoạn 1993 đến 2017 nó dâng trung bình bao nhiêu mỗi năm? | yes | 1 | yes | yes | 23.8 |
| 111 | follow-up-12 | Các mô hình quá khứ đánh giá thấp những gì? | yes | 1 | yes | yes | 25.6 |
| 112 | cross-lingual-01 | Hàm chatgpt_generation trong sách dùng để làm gì? | no | - | yes | yes | 21.3 |
| 113 | cross-lingual-02 | Những yếu tố chính nào quyết định các token xuất hiện trong một tokenizer? | yes | 1 | yes | yes | 32.9 |
| 114 | cross-lingual-03 | In the matrix factorization collaborative filtering chapter, what is the first thing implemented in Python? | yes | 1 | no | no | 32.0 |
| 115 | cross-lingual-04 | Which two issues have to be considered in KNN because it decides based on the nearest points? | yes | 1 | yes | yes | 28.8 |
| 116 | cross-lingual-05 | Archaea như Halobacterium thực hiện loại quang hợp nào và dùng sắc tố nào để hấp thụ ánh sáng? | yes | 1 | yes | yes | 23.7 |
| 117 | cross-lingual-06 | Thực vật C4 cố định carbon dioxide trong tế bào mô giậu bằng cách nào và enzyme nào xúc tác phản ứng đó? | yes | 1 | yes | yes | 27.7 |
| 118 | cross-lingual-07 | Tại Đại học Cornell, ngô trồng ngoài đồng được báo cáo có tốc độ quang hợp ở lá như thế nào so với các loài khác? | yes | 1 | yes | no | 32.3 |
| 119 | cross-lingual-08 | According to the IPCC projections cited in the article, how much could the global surface temperature rise during the 21st century in the moderate scenario and in the extreme scenario? | yes | 1 | yes | yes | 25.8 |
| 120 | cross-lingual-09 | How many more people could climate change push into poverty by 2030, according to the World Bank estimate in the article? | yes | 1 | yes | yes | 21.6 |
| 121 | cross-lingual-10 | Which Sustainable Development Goal links climate action to sustainable development, and how is it worded? | yes | 1 | yes | yes | 23.7 |
| 122 | typo-short-01 | bag of wrds meaning? | yes | 5 | yes | yes | 38.2 |
| 123 | typo-short-02 | zero shot chain of thot phrase | yes | 1 | yes | yes | 21.9 |
| 124 | typo-short-03 | sieu phang hyperplane la gi | no | - | yes | yes | 32.8 |
| 125 | typo-short-04 | transfer learning la gi | yes | 1 | yes | yes | 28.7 |
| 126 | typo-short-05 | co bao nhieu support vector trong vi du svm | yes | 5 | yes | yes | 24.2 |
| 127 | typo-short-06 | wich pigment do some archea use insted of chlorophyll | no | - | yes | yes | 21.3 |
| 128 | typo-short-07 | thep va xi mang tao ra bao nhieu khi thai co2 cong nghiep | yes | 1 | yes | yes | 20.4 |
| 129 | typo-short-08 | khi nha kinh lam khong khi gan be mat am hon bao nhieu do | no | - | no | yes | 33.0 |
| 130 | out-of-doc-01 | Who founded Hugging Face? | - | - | yes | yes | 34.2 |
| 131 | out-of-doc-02 | How does the Switch Transformer route tokens to experts in a mixture-of-experts model? | - | - | yes | yes | 31.3 |
| 132 | out-of-doc-03 | What is the context window of GPT-5? | - | - | yes | yes | 35.2 |
| 133 | out-of-doc-04 | What is the price of the Hugging Face Pro plan? | - | - | yes | yes | 34.9 |
| 134 | out-of-doc-05 | Thuật toán Apriori hoạt động như thế nào? | - | - | yes | yes | 40.5 |
| 135 | out-of-doc-06 | XGBoost khác gì với Gradient Boosting thông thường? | - | - | yes | yes | 42.0 |
| 136 | out-of-doc-07 | Hàm kích hoạt GELU được định nghĩa thế nào? | - | - | yes | yes | 40.3 |
| 137 | out-of-doc-08 | Mạng LSTM có những cổng nào và mỗi cổng làm gì? | - | - | yes | yes | 36.5 |
| 138 | out-of-doc-09 | What is the Q-cycle in the cytochrome b6f complex? | - | - | yes | yes | 34.2 |
| 139 | out-of-doc-10 | Which pigment makes carrots orange and what is its chemical formula? | - | - | yes | yes | 29.5 |
| 140 | out-of-doc-11 | Who won the Nobel Prize in Physics in 2019? | - | - | yes | yes | 32.3 |
| 141 | out-of-doc-12 | What is the boiling point of water at sea level? | - | - | yes | yes | 32.2 |
| 142 | out-of-doc-13 | Hiệp định Escazú quy định điều gì về môi trường? | - | - | yes | yes | 33.0 |
| 143 | out-of-doc-14 | Phở bò được nấu như thế nào? | - | - | yes | yes | 42.9 |
| 144 | out-of-doc-15 | Ai là tổng thống Hoa Kỳ năm 2020? | - | - | yes | yes | 32.8 |
| 145 | table-formula-code-01 | In the printed structure of the Phi-3 model, how many decoder layers does it have, and what are the dimensions of its embedding layer? | yes | 2 | yes | yes | 27.9 |
| 146 | table-formula-code-02 | Which model name does the book pass to AutoModelForCausalLM.from_pretrained when loading the text generation model? | yes | 1 | yes | yes | 23.2 |
| 147 | table-formula-code-03 | What is the 'pearson_cosine' score of the embedding model after training, and what does that metric measure? | yes | 1 | yes | yes | 41.7 |
| 148 | table-formula-code-04 | Một ma trận đối xứng A được gọi là xác định dương khi nào, và nửa xác định dương khác ở điểm nào? | yes | 2 | yes | yes | 37.2 |
| 149 | table-formula-code-05 | Trong bảng thuật ngữ của bài toán tối ưu, optimization variable được gọi là gì trong tiếng Việt và được ký hiệu thế nào? | yes | 1 | yes | yes | 26.7 |
| 150 | table-formula-code-06 | Trong ví dụ content-based recommendation, RMSE trên tập huấn luyện và trên tập kiểm thử là bao nhiêu? | yes | 1 | yes | yes | 27.2 |
