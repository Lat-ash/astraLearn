# AstraLearn 📚✨

A powerful AI-powered learning assistant built on top of **InternTA**, helping you study and understand course materials through intelligent summarization, detailed explanations, and interactive testing.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red)
![Groq](https://img.shields.io/badge/Groq-LLM%20API-green)
![InternTA](https://img.shields.io/badge/Built%20on-InternTA-purple)

**Transform your study sessions with AI-powered learning**

---

## 📋 Table of Contents

# 📑 Table of Contents

- [🌟 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#Installation)
- [Running the Application](#running-the-application)
- [📖 How to Use](#-how-to-use)
- [🏗️ Project Structure](#project-structure)
- [🛠️ Technical Architecture](#technical-architecture)
- [💡 Use Cases](#-use-cases)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔒 Privacy & Security](#-privacy--security)
- [🙏 Acknowledgments](#-acknowledgments)

---

## 🌟 Features

### 📘 RAG — Detailed Answers

- Comprehensive explanations from uploaded materials
- Specific page references and sources
- Structured answers across all files
- Multi-file intelligence for complete coverage

### 📝 Summarizer

- Clean bullet-point summaries
- Key concepts extracted automatically
- Perfect for quick revision
- Consistent formatting across all content

### 🧪 Test Generator

- Auto-generated MCQs from your materials
- Instant feedback with explanations
- Adaptive learning experience
- Progress tracking with each attempt

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - Latest Python version recommended
- **Groq API Key** - Free from [console.groq.com](https://console.groq.com)
- **Tesseract OCR** - For image text extraction

---

## 🔧 Installation

### Method 1: Conda (Recommended)

```bash
# Clone and setup
git clone https://github.com/your-username/AstraLearn.git
cd AstraLearn

# Create environment
conda create -n astralearn python=3.10
conda activate astralearn

# Install dependencies
conda install pytorch torchvision torchaudio cpuonly -c pytorch
pip install -r requirements.txt

# Install OCR
brew install tesseract                    # macOS
# sudo apt-get install tesseract-ocr     # Linux
# Download from GitHub releases         # Windows
```

### Method 2: Virtual Environment

```bash
# Create virtual environment
python -m venv astralearn_env
source astralearn_env/bin/activate

# Install packages
pip install -r requirements.txt
```

### Running the Application

```bash
conda activate astralearn
streamlit run app.py
Open http://localhost:8501 in your browser.
```

## 📖 how to use

1. Get API Key from Groq Console

2. Upload Files (PDF, PNG, JPG, JPEG)

3. Choose Mode:

   - RAG - Detailed explanations

   - Summarizer - Bullet-point summaries

   - Test Generator - Practice questions

4. Start Learning - Ask questions and get AI-powered responses

## 🏗️ Project structure

project structure
AstraLearn/
├── app.py
├── requirements.txt
├── README.md
└── agents/
├── **init**.py
├── integration.py
├── summarizer.py
├── test_generator.py
└── langchain_wrapper.py

## 🛠️ technical architecture

Architecture

- AI Backend: Groq LLaMA 3.1 8B
- Framework: LangChain
- Vector Store: FAISS
- UI: Streamlit

Enhanced Features

- Multi-file RAG processing
- Smart file detection
- Consistent formatting
- Interactive quiz interface
- OCR support
- Rate limiting

## 💡 Use Cases

🎓 Students

- Chapter summaries
- MCQs
- Concept explanations

👨‍🏫 Educators

- Quiz generation
- Lesson planning

💼 Professionals

- Documentation summarization
- Training materials
- Knowledge base building

## 🐛 Troubleshooting

1. Invalid Groq API key

   - Check dashboard
   - Remove whitespace
   - Ensure key is active

2. No content extracted

   - PDF may be scanned
   - Install Tesseract OCR

3. OCR Errors
   ```
   brew reinstall tesseract
   sudo apt-get install tesseract-ocr-eng
   ```
4. Import Errors
   ```
   pip install --force-reinstall -r requirements.txt
   ```

## 🔒 Privacy & Security

- Local file processing
- Secure HTTPS API calls
- No data storage
- Session cleanup on exit

## 🙏 Acknowledgments

InternTA - Base framework
Groq - LLM API
Streamlit - Web framework
LangChain - AI framework

# Happy Learning! 🎓✨

# Built with ❤️ using Streamlit, Groq, LangChain, and InternTA
