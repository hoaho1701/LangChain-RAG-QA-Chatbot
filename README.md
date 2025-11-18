# Paper Navigator 📚 - Trợ lý Nghiên cứu AI của bạn

Paper Navigator là một hệ thống Hỏi-Đáp (Q&A) được xây dựng dựa trên kiến trúc RAG (Retrieval-Augmented Generation). Nó cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên và nhận được câu trả lời chính xác từ nội dung của một bộ sưu tập các bài báo khoa học (dạng PDF).

Dự án này chạy 100% trên máy tính cá nhân, không cần API trả phí, đảm bảo quyền riêng tư và khả năng truy cập.

---

### ✨ Tính năng chính

-   **Trả lời Tổng hợp & Thông minh:** Không chỉ trích xuất, chatbot có khả năng tổng hợp thông tin từ nhiều nguồn trong tài liệu để đưa ra câu trả lời toàn diện.
-   **Tăng cường Ngữ cảnh:** Sử dụng các chiến lược truy vấn nâng cao để cung cấp cho LLM một cái nhìn rộng hơn về vấn đề.
-   **Chạy Local 100%:** Sử dụng Ollama để chạy mô hình ngôn ngữ lớn ngay trên máy của bạn.
-   **Giao diện Tương tác:** Giao diện chatbot thân thiện, cho phép upload file, quản lý dữ liệu và xóa lịch sử trò chuyện.

---

### 🛠️ Tech Stack

| Thành phần        | Công nghệ                               |
| ----------------- | --------------------------------------- |
| **Framework**     | LlamaIndex                              |
| **LLM**           | Ollama (Model: `llama3:8b`)             |
| **Embedding Model** | Hugging Face (`BAAI/bge-small-en-v1.5`) |
| **Vector Database** | ChromaDB (Local)                        |
| **Giao diện**     | Streamlit                               |
| **Ngôn ngữ**      | Python 3.10+                            |

---

### 📂 Cấu trúc Thư mục (Project Structure)

Dự án được tổ chức theo một cấu trúc module hóa để dễ dàng quản lý và mở rộng:

```
RAG-based-AI-Paper-Analyzer/
├── documents/
└── src/
    ├── config.py
    ├── data_processing.py
    └── prompts.py
    └── rag_pipeline.py
├── vector_db/
├── .gitignore
├── app.py
├── LICENCE
├── README.md
├── requirements.txt
```

**Giải thích các thành phần chính:**

| Thư mục / File      | Mô tả                                                               |
| ------------------- | ------------------------------------------------------------------- |
| `documents/`        | Nơi chứa các file PDF bài báo khoa học làm dữ liệu đầu vào.         |
| `src/`              | Thư mục chứa toàn bộ mã nguồn xử lý logic cốt lõi của ứng dụng.     |
| `src/config.py`     | Định nghĩa các hằng số và cấu hình như tên model, đường dẫn file.    |
| `src/data_processing.py` | Chịu trách nhiệm tải và xử lý các tài liệu từ thư mục `documents`. |
| `src/prompts.py`    | Định nghĩa các prompt template tùy chỉnh để hướng dẫn LLM trả lời tốt hơn. |
| `src/rag_pipeline.py` | Bộ não của ứng dụng, kết nối các thành phần để tạo ra pipeline RAG. |
| `vector_db/`        | Nơi lưu trữ cơ sở dữ liệu vector đã được tạo ra từ tài liệu.      |
| `app.py`            | File chính để khởi chạy giao diện người dùng bằng Streamlit.         |
| `LICENSE`           | Giấy phép mã nguồn mở của dự án (MIT License).                      |
| `README.md`         | Tài liệu hướng dẫn và giới thiệu về dự án.                          |
| `requirements.txt`  | Danh sách các thư viện Python cần thiết để chạy dự án.             |

---

### 🚀 Cài đặt và Chạy

**Yêu cầu:**
-   Python 3.10+
-   [Ollama](https://ollama.com/) đã được cài đặt và đang chạy.

**Các bước thực hiện:**

1.  **Cài đặt Ollama và tải mô hình:**
    ```bash
    # Sau khi cài đặt Ollama, chạy lệnh sau trong terminal
    ollama pull llama3:8b
    ```

2.  **Clone repository này:**
    ```bash
    git clone https://github.com/ten-github-cua-ban/RAG-based-AI-Paper-Analyzer.git
    cd RAG-based-AI-Paper-Analyzer
    ```

3.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: venv\Scripts\activate
    ```

4.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Chạy ứng dụng:**
    ```bash
    streamlit run app.py
    ```
    Lần đầu tiên xử lý tài liệu, hệ thống sẽ cần một chút thời gian để xây dựng cơ sở dữ liệu vector. Các lần sau, bạn có thể tiếp tục tải thêm tài liệu để bổ sung kiến thức cho hệ thống.

---

### 🔮 Hướng phát triển trong tương lai

Đây là những tính năng tiềm năng để cải thiện và mở rộng dự án:

-   [ ] **Hỗ trợ nhiều định dạng:** Mở rộng khả năng xử lý cho các file `.docx`, `.txt`.
-   [ ] **Lưu lịch sử chat:** Lưu lại các cuộc hội thoại để người dùng có thể xem lại sau.
-   [ ] **Trích dẫn nguồn:** Hiển thị nguồn (tên tài liệu và số trang) mà câu trả lời được rút ra.

---

### 📄 Giấy phép

Dự án này được cấp phép theo **MIT License**. Xem file `LICENSE` để biết thêm chi tiết.

---

### 🙏 Lời cảm ơn

Dự án này sẽ không thể thực hiện được nếu không có các công cụ mã nguồn mở tuyệt vời từ cộng đồng:
-   [LlamaIndex](https://www.llamaindex.ai/)
-   [Ollama](https://ollama.com/)
-   [ChromaDB](https://www.trychroma.com/)
-   [Streamlit](https://streamlit.io/)
