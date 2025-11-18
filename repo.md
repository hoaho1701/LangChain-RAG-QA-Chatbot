# Domain-Specific Q&A (Text / Docs)

| #     | Repo                           | Link                                                                            | Mô tả ngắn                                                              | 📘 Bạn học được gì                                                                                                                                    |
| ----- | ------------------------------ | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **LightRAG** (by HKUDS)        | 🔗 [github.com/HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)               | Minimal RAG pipeline cho text docs; embedding + retrieval + generation. | 🔹 Cách xây pipeline RAG nhẹ nhàng từ text raw.  🔹 Cách chia chunk theo semantic và tối ưu context window.  🔹 Reranker simple để tăng độ chính xác. |
| **2** | **FlashRAG** (by RUC-NLPIR)    | 🔗 [github.com/RUC-NLPIR/FlashRAG](https://github.com/RUC-NLPIR/FlashRAG)       | Toolkit đa thuật toán RAG (dùng nhiều retrieval model và re-ranking).   | 🔹 So sánh nhiều chiến lược retrieval (k-NN, BM25, dense).  🔹 Cách benchmark và đánh giá RAG model.                                                  |
| **3** | **PaperQA2** (by Future-House) | 🔗 [github.com/Future-House/paper-qa](https://github.com/Future-House/paper-qa) | RAG cho file PDF nghiên cứu, hỏi-đáp chính xác với nguồn cụ thể.        | 🔹 Cách trích text từ PDF và lưu metadata nguồn.  🔹 Cách hiển thị câu trả lời kèm citation.                                                          |
| **4** | **RAGFlow** (by Infiniflow)    | 🔗 [github.com/infiniflow/ragflow](https://github.com/infiniflow/ragflow)       | “Enterprise RAG engine” với UI, multi-source ingestion, và workflow.    | 🔹 Kiến trúc production scale cho RAG.  🔹 Cách xây UI quản lý vector store và truy vấn.                                                              |
| **5** | **Kotaemon** (by Cinnamon AI)  | 🔗 [github.com/Cinnamon/kotaemon](https://github.com/Cinnamon/kotaemon)         | App QA text-only với UI (Gradio/Streamlit), tích hợp LlamaIndex.        | 🔹 Cách kết hợp frontend (Gradio) với backend RAG.  🔹 Prompt template cho Q&A domain.                                                                |

**Gợi ý bắt đầu:**
* Clone **LightRAG** để làm baseline RAG cơ bản.
* Sau đó thử **PaperQA2** nếu dữ liệu bạn là PDF hoặc báo cáo văn bản.

## Đề xuất hành động

1. **Bước 1:** Clone LightRAG và Multi-Modal-RAG-Pipeline để chạy demo local.
2. **Bước 2:** Thay dữ liệu bằng data domain của bạn (ví dụ ảnh + văn bản công ty hoặc medical reports).
3. **Bước 3:** So sánh hiệu quả retrieval (text vs image query).
4. **Bước 4:** Tích hợp vào frontend Streamlit hoặc Flutter web UI để test.
5. **Bước 5:** Khi ổn, chuyển sang Llama3 hoặc Phi3 để fine-tune retrieval + generation cho domain riêng.

---

### **Dự án 1: Paper Navigator (RAG với Văn bản)**

Mục tiêu của bạn là xây dựng một hệ thống Q&A trên các bài báo AI. Dưới đây là các repo từ cơ bản đến nâng cao để bạn tham khảo.

#### **1. Repo "Kinh điển": `privateGPT`**

*   **Link:** [https://github.com/imartinez/privateGPT](https://github.com/imartinez/privateGPT)
*   **Tại sao nó hữu ích:**
    *   **Local 100%:** Đây là dự án tiên phong trong việc xây dựng một hệ thống RAG hoàn chỉnh chạy hoàn toàn trên máy tính của bạn, không cần kết nối internet hay API trả phí. Nó sử dụng các mô hình embedding và LLM mã nguồn mở.
    *   **Hoàn chỉnh:** Dự án này có đủ mọi thành phần: nạp tài liệu, tạo CSDL vector (sử dụng ChromaDB), và một giao diện dòng lệnh (CLI) cũng như giao diện web để tương tác.
    *   **Cấu trúc tốt:** Cấu trúc file của dự án này khá rõ ràng, là một ví dụ tốt để bạn học theo.
*   **Điểm cần lưu ý:** Dự án này khá lớn và có thể hơi phức tạp cho người mới bắt đầu. Hãy đọc code để hiểu luồng hoạt động chính thay vì cố gắng hiểu từng dòng code ngay lập tức.

#### **2. Repo "Tối giản & Dễ hiểu": `llm-rag-chatbot`**

*   **Link:** [https://github.com/learn-langchain/llm-rag-chatbot](https://github.com/learn-langchain/llm-rag-chatbot)
*   **Tại sao nó hữu ích:**
    *   **Tập trung vào cốt lõi:** Repo này là code đi kèm một khóa học, vì vậy nó được viết rất rõ ràng và tập trung vào việc giải thích các khái niệm RAG cơ bản nhất với LangChain.
    *   **Dễ đọc:** Mã nguồn được chia thành các file nhỏ, dễ hiểu, không có nhiều logic phức tạp thừa thãi. Đây là điểm khởi đầu tuyệt vời để bạn hiểu cách LangChain kết nối các thành phần.
    *   **Có giao diện:** Dự án này sử dụng Chainlit để tạo giao diện, một lựa chọn khác ngoài Streamlit mà bạn có thể tham khảo.
*   **Điểm cần lưu ý:** Code có thể được viết theo phong cách hướng dẫn (tutorial) hơn là một ứng dụng hoàn chỉnh.

#### **3. Repo "Từ đầu" (From Scratch): `RAG_from_scratch`**

*   **Link:** [https://github.com/pinecone-io/examples/tree/master/learn/generation/rag/rag-from-scratch](https://github.com/pinecone-io/examples/tree/master/learn/generation/rag/rag-from-scratch)
*   **Tại sao nó hữu ích:**
    *   **Không phụ thuộc framework:** Repo này (thực chất là một notebook) xây dựng RAG mà không cần đến LangChain hay LlamaIndex. Nó giúp bạn hiểu sâu sắc những gì thực sự diễn ra phía sau: cách bạn tự mình phân mảnh văn bản, tạo embedding, thực hiện tìm kiếm tương đồng, và xây dựng prompt.
    *   **Nền tảng vững chắc:** Sau khi làm theo notebook này, bạn sẽ thực sự "sở hữu" kiến thức về RAG và biết tại sao các framework như LangChain lại hữu ích.
*   **Điểm cần lưu ý:** Mặc dù đến từ Pinecone, bạn có thể dễ dàng thay thế phần CSDL vector bằng FAISS hoặc ChromaDB.

### Lời khuyên vàng khi tham khảo:

1.  **Đừng sao chép, hãy học hỏi:** Mục tiêu là để hiểu "tại sao" họ lại viết code như vậy, chứ không phải để sao chép toàn bộ dự án.
2.  **Đọc `README.md` trước tiên:** Hiểu tổng quan về dự án, cách cài đặt và cách chạy nó.
3.  **Tập trung vào cấu trúc:** Chú ý cách họ tổ chức các file và thư mục. Đây là điều bạn có thể áp dụng trực tiếp vào dự án của mình.
4.  **Bắt đầu từ file chính:** Tìm file chạy chính (như `app.py` hoặc `main.py`) và đi theo luồng thực thi của chương trình để hiểu cách các module tương tác với nhau.

Chúc bạn học được nhiều điều bổ ích từ các dự án này