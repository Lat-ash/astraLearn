# AstraLearn – AI Learning Assistant

### _Built with Streamlit, Groq, LangChain & InternTA_

AstraLearn is an intelligent AI-powered study companion designed to help students understand their course material through **summaries**, **RAG-based detailed explanations**, and **auto-generated MCQs**.

It extends the InternTA framework with a cleaner UI, enhanced file processing, and a more powerful hybrid retrieval pipeline.

---

## 🚀 Features

### 📘 RAG: Detailed Answers

- Answers generated directly from your uploaded PDFs & images
- Page-aware, source-referenced responses
- Multi-file joint retrieval
- Clean structured outputs

### 📝 Summarizer

- Concise bullet-point summaries
- File-aware separation
- Consistent formatting

### 🧪 MCQ Generator

- Auto-generates questions from your documents
- Instant feedback
- Supports adaptive testing
- Built-in scoring logic & explanations

### 🖼️ Multi-File Support (PDF + Images)

- OCR support via Tesseract
- Unified indexing across all files
- Handles textbook scans, notes, screenshots

---

## 🏗️ Project Structure

```
AstraLearn/
│
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
│
└── agents/                   # AI Logic Modules
    ├── __init__.py
    ├── integration.py        # Orchestrates all agents
    ├── summarizer.py         # Bullet summary engine
    ├── test_generator.py     # MCQ generator
    └── langchain_wrapper.py  # RAG pipeline wrapper
```

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AstraLearn.git
cd AstraLearn
```

### 2. Create Virtual Environment

```bash
python -m venv astralearn_env
source astralearn_env/bin/activate    # Windows: astralearn_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**macOS**

```bash
brew install tesseract
```

**Ubuntu**

```bash
sudo apt-get install tesseract-ocr
```

**Windows**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

---

## ▶️ Running AstraLearn

```bash
streamlit run app.py
```

The app will open at:
➡️ http://localhost:8501

---

## 📖 How to Use

### 1️⃣ Add Your Groq API Key

- Create an account at https://console.groq.com
- Copy your API key
- Paste it inside the sidebar input field

### 2️⃣ Upload Your Study Material

Supported formats:

- PDF
- PNG / JPG / JPEG

### 3️⃣ Choose Your Mode

- **RAG** → Detailed, source-backed answers
- **Summarizer** → Bullet-point summaries
- **MCQ Generator** → Practice questions

### 4️⃣ Start Learning

Ask any question, read summaries, or generate quizzes instantly.

---

## 🧠 Tech Stack

- Groq LLaMA 3.1 8B
- LangChain
- FAISS
- Streamlit
- Tesseract OCR
- InternTA (extended)

---

## 🔧 Enhancements Over InternTA

- Multi-file parallel processing
- Clean UI + persistent input bar
- Improved MCQ generator
- Cleaner RAG answers
- Bullet summary improvements
- Robust file handling
- Hybrid keyword + vector retrieval

---

## 🐛 Troubleshooting

### Invalid Groq API Key

- Regenerate key
- Remove whitespace
- Ensure you have API quota

### “No text extracted”

- PDF may be scanned
- Ensure Tesseract is installed
- Increase image DPI

### Import Errors

```bash
pip install --force-reinstall -r requirements.txt
```

### OCR Issues

```bash
brew reinstall tesseract           # macOS
sudo apt-get install tesseract-ocr # Ubuntu
```

---

## 🤝 Contributing

PRs welcome!

1. Fork the repo
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit

```bash
git commit -m "Add new feature"
```

4. Push & open a Pull Request

---

## 📄 License

MIT License — free to reuse and modify.

---

## ❤️ Acknowledgments

- InternTA
- Groq
- LangChain
- Streamlit
- Open-source contributors

---

# 🎓 Happy Learning with AstraLearn!

Built with ❤️ using Streamlit, Groq, LangChain, and InternTA.
