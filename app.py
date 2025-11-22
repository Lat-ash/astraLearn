import streamlit as st
import tempfile
from pypdf import PdfReader
from PIL import Image
import pytesseract
import time
from groq import Groq

from agents.integration import InternTAAgentsManager

# -------------------------------
# CUSTOM AURORA THEME
# -------------------------------
CUSTOM_CSS = """
<style>
html, body, .stApp {
    background: radial-gradient(circle at top, #1a1f47, #0d0f26);
    background-size: cover;
    color: #ffffff !important;
    height: 100%;
}

.sidebar .sidebar-content {
    background: linear-gradient(180deg, #14162b, #0d0f26);
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #e8e9ff !important;
}

.stCard {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 0 25px rgba(82, 110, 255, 0.25);
    margin-bottom: 18px;
}

.mcq-button {
    background: linear-gradient(90deg, #6a5acd, #00bfff);
    padding: 15px 20px;
    color: white;
    border-radius: 25px;
    border: none;
    font-weight: 600;
    font-size: 16px;
    margin: 10px 0;
    width: 100%;
    transition: all 0.3s ease;
    text-align: left;
}

.mcq-button:hover {
    opacity: 0.85;
    box-shadow: 0px 0px 15px #6a5acd;
    transform: translateY(-2px);
}

.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(26, 31, 71, 0.95);
    backdrop-filter: blur(20px);
    padding: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
    z-index: 1000;
}

.chat-input-inner {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    gap: 10px;
}

.main-content {
    padding-bottom: 120px;
}

.feedback-correct {
    background: linear-gradient(90deg, #00c853, #00bfff);
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
}

.feedback-incorrect {
    background: linear-gradient(90deg, #ff5252, #ff4081);
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
}

.next-button {
    background: linear-gradient(90deg, #8a7df0, #00d4ff);
    padding: 12px 30px;
    color: white;
    border-radius: 25px;
    border: none;
    font-weight: 600;
    font-size: 16px;
    margin: 10px 0;
}

.welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 20px;
    margin: 20px 0;
}

.bullet-points {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
    border-left: 4px solid #6a5acd;
}

.bullet-points ul {
    margin: 0;
    padding-left: 20px;
}

.bullet-points li {
    margin: 8px 0;
    line-height: 1.5;
}

@media (max-width: 768px) {
    .chat-input-inner {
        flex-direction: column;
    }
    .main-content {
        padding-bottom: 180px;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def validate_groq_key(api_key):
    """Validate the Groq API key"""
    try:
        client = Groq(api_key=api_key)
        # Test with a minimal request
        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        print(f"API key validation error: {e}")
        return False


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file with comprehensive extraction"""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                # Clean the text and add page markers
                clean_text = page_text.strip()
                text += f"Page {i+1}:\n{clean_text}\n\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_file.name}: {str(e)}")
        return ""


def extract_text_from_image(img_file):
    """Extract text from image using OCR"""
    try:
        img = Image.open(img_file)
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error processing image {img_file.name}: {str(e)}")
        return ""


def extract_all_files_content(files):
    """Extract text from all files with clear file identification"""
    all_files_content = []

    for file in files:
        file_name = file.name
        print(f"Processing: {file_name}")

        if file.name.lower().endswith(".pdf"):
            content = extract_text_from_pdf(file)
        else:
            content = extract_text_from_image(file)

        if content and content.strip():
            # Use clear, consistent file markers
            formatted_content = f"📚 FILE: {file_name}\n{content}"
            all_files_content.append(
                {
                    "file_name": file_name,
                    "content": formatted_content,
                    "raw_content": content,
                }
            )
            print(f"Successfully processed: {file_name} - {len(content)} characters")
        else:
            print(f"Failed to extract content from: {file_name}")

    return all_files_content


# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style='padding: 15px; text-align: center; color: #ffffff;
        font-size: 32px; font-weight: 700;
        background: linear-gradient(90deg, #8a7df0, #00d4ff);
        border-radius: 16px; margin-bottom: 20px;'>
            AstraLearn ✨
        </div>
    """,
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "Choose a Mode:",
        ["📘 RAG — Detailed Answers", "📝 Summarizer", "🧪 Test Generator"],
    )

    st.markdown("---")
    st.markdown("### Upload Course Material Below")

    uploaded_files = st.file_uploader(
        "Upload PDFs or Images (Max 200MB total)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Supported formats: PDF, PNG, JPG, JPEG",
    )

    # File size validation
    if uploaded_files:
        total_size = sum([f.size for f in uploaded_files])
        if total_size > 200 * 1024 * 1024:  # 200MB limit
            st.error("❌ Total file size exceeds 200MB limit")
            st.stop()

    api_key = st.text_input(
        "Groq API Key:",
        type="password",
        help="Get your API key from https://console.groq.com",
    )

# -------------------------------
# API KEY VALIDATION
# -------------------------------
if not api_key:
    st.warning("🔑 Please enter your Groq API key in the sidebar to continue.")
    st.stop()

if api_key and not validate_groq_key(api_key):
    st.sidebar.error("❌ Invalid Groq API key. Please check and try again.")
    st.stop()

# -------------------------------
# INIT SESSION STATE
# -------------------------------
if "agent_manager" not in st.session_state:
    st.session_state.agent_manager = InternTAAgentsManager(api_key)

if "all_files_data" not in st.session_state:
    st.session_state.all_files_data = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "test_state" not in st.session_state:
    st.session_state.test_state = {
        "question": None,
        "choices": [],
        "correct": None,
        "explanation": None,
        "answered": False,
        "user_choice": None,
        "feedback": None,
    }

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

# -------------------------------
# LOAD MATERIAL - PROCESS ALL FILES
# -------------------------------
if uploaded_files:
    # Check if we have new files to process
    current_file_names = set([f.name for f in uploaded_files])
    if (
        not st.session_state.all_files_data
        or current_file_names != st.session_state.processed_files
    ):

        with st.sidebar:
            with st.spinner("📚 Processing all uploaded files..."):
                all_files_data = extract_all_files_content(uploaded_files)

                if all_files_data:
                    st.session_state.all_files_data = all_files_data
                    st.session_state.processed_files = current_file_names

                    # Combine all content for the agent manager with clear separation
                    combined_text = ""
                    for file_data in all_files_data:
                        combined_text += file_data["content"] + "\n\n"

                    # Load the combined text into the agent manager
                    st.session_state.agent_manager.load_material(combined_text)

                    # Show success message with file details
                    file_names = [data["file_name"] for data in all_files_data]
                    st.success(f"✅ Successfully loaded {len(all_files_data)} files:")
                    for name in file_names:
                        st.success(f"   • {name}")
                else:
                    st.error(
                        "❌ Could not extract text from any files. Please try different files."
                    )

# -------------------------------
# MAIN CONTENT AREA
# -------------------------------
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown("## AstraLearn Learning Assistant")
st.markdown(f"### **Current Mode: {mode}**")

# Welcome message for empty state
if (
    not st.session_state.conversation
    and mode != "🧪 Test Generator"
    and st.session_state.all_files_data
):
    file_names = [data["file_name"] for data in st.session_state.all_files_data]
    st.markdown(
        f"""
    <div class='welcome-card'>
    <h3>👋 Ready to Learn!</h3>
    <p>Your course materials have been loaded. Start asking questions or use the options below:</p>
    <ul>
    <li><b>📘 RAG Mode:</b> Get detailed answers from your materials</li>
    <li><b>📝 Summarizer:</b> Create concise bullet-point summaries</li>
    <li><b>🧪 Test Generator:</b> Generate practice questions</li>
    </ul>
    <p><b>📁 Loaded Files ({len(file_names)}):</b> {", ".join(file_names)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Display conversation history
for i, msg in enumerate(st.session_state.conversation):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        # Format the response based on mode
        content = msg["content"]
        if mode == "📝 Summarizer" and ("•" in content or "-" in content):
            # Format as bullet points for summarizer
            st.markdown(
                f"<div class='bullet-points'>{content}</div>", unsafe_allow_html=True
            )
        else:
            st.markdown(f"<div class='stCard'>{content}</div>", unsafe_allow_html=True)

# -------------------------------
# TEST GENERATOR UI
# -------------------------------
if mode == "🧪 Test Generator":
    test_state = st.session_state.test_state

    if not test_state["question"]:
        st.info(
            "👆 Enter a topic or question request in the input below to generate your first test question!"
        )

    elif test_state["question"] and test_state["choices"]:
        st.markdown("### 🧠 Test Your Knowledge")
        st.markdown(
            f"<div class='stCard'><h3>{test_state['question']}</h3></div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Choose your answer:")

        # Create buttons for choices
        for idx, choice in enumerate(test_state["choices"]):
            choice_letter = chr(65 + idx)

            if (
                st.button(
                    f"{choice_letter}) {choice}",
                    key=f"choice_{idx}",
                    use_container_width=True,
                    type="secondary",
                )
                and not test_state["answered"]
            ):
                # User made a selection
                user_choice = choice_letter
                correct_choice = test_state["correct"]

                # Evaluate answer
                if user_choice == correct_choice:
                    feedback = f"🎉 **Correct!** {test_state['explanation']}"
                else:
                    feedback = f"❌ **Incorrect.** The correct answer is {correct_choice}. {test_state['explanation']}"

                st.session_state.test_state.update(
                    {"answered": True, "user_choice": user_choice, "feedback": feedback}
                )
                st.rerun()

        # Show feedback if answered
        if test_state["answered"] and test_state["feedback"]:
            st.markdown("---")
            if "🎉" in test_state["feedback"]:
                st.markdown(
                    f'<div class="feedback-correct">{test_state["feedback"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="feedback-incorrect">{test_state["feedback"]}</div>',
                    unsafe_allow_html=True,
                )

            # Next Question button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "Next Question →",
                    key="next_question",
                    use_container_width=True,
                    type="primary",
                ):
                    with st.spinner("Generating new question..."):
                        q, ch, correct, expl = (
                            st.session_state.agent_manager.generate_mcq()
                        )
                        st.session_state.test_state = {
                            "question": q,
                            "choices": ch,
                            "correct": correct,
                            "explanation": expl,
                            "answered": False,
                            "user_choice": None,
                            "feedback": None,
                        }
                    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# BOTTOM CHAT INPUT (ALWAYS VISIBLE - ChatGPT Style)
# -------------------------------
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
st.markdown('<div class="chat-input-inner">', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Your message:",
        placeholder="Ask a question or request a test...",
        key="chat_input",
        label_visibility="collapsed",
    )

with col2:
    send_button = st.button("Send", use_container_width=True, key="send_button")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# PROCESS USER INPUT
# -------------------------------
if send_button and user_input:
    # Input validation
    if not user_input.strip():
        st.warning("Please enter a message")
        st.stop()

    # Prevent duplicate processing of the same input
    if user_input == st.session_state.last_user_input:
        st.warning("⏳ Please wait for the current request to complete")
        st.stop()

    # Rate limiting (2 second cooldown)
    if time.time() - st.session_state.last_request_time < 2:
        st.warning("⏳ Please wait a moment before sending another request")
        st.stop()

    if not st.session_state.all_files_data:
        st.error("📁 Please upload course material first.")
        st.stop()

    try:
        # Store the current input to prevent duplicates
        st.session_state.last_user_input = user_input

        # Add user message to conversation
        st.session_state.conversation.append({"role": "user", "content": user_input})
        st.session_state.last_request_time = time.time()

        if mode == "📘 RAG — Detailed Answers":
            with st.spinner(
                "🔍 Generating comprehensive explanation from all files..."
            ):
                answer = st.session_state.agent_manager.run_rag(user_input)
            st.session_state.conversation.append(
                {"role": "assistant", "content": answer}
            )

        elif mode == "📝 Summarizer":
            with st.spinner("📋 Creating comprehensive summary from all files..."):
                answer = st.session_state.agent_manager.run_summary(user_input)
            st.session_state.conversation.append(
                {"role": "assistant", "content": answer}
            )

        elif mode == "🧪 Test Generator":
            with st.spinner("🎯 Generating test question from all files..."):
                q, ch, correct, expl = st.session_state.agent_manager.generate_mcq()

            st.session_state.test_state = {
                "question": q,
                "choices": ch,
                "correct": correct,
                "explanation": expl,
                "answered": False,
                "user_choice": None,
                "feedback": None,
            }

        st.rerun()

    except Exception as e:
        st.error(f"❌ Error processing request: {str(e)}")
        st.session_state.last_user_input = ""
        st.stop()

# -------------------------------
# SIDEBAR STATUS
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Material Status")

if st.session_state.all_files_data:
    st.sidebar.success(f"✅ {len(st.session_state.all_files_data)} file(s) loaded")

    # Show file list with sizes
    st.sidebar.markdown("**Loaded Files:**")
    total_words = 0
    for file_data in st.session_state.all_files_data:
        file_name = file_data["file_name"]
        word_count = len(file_data["raw_content"].split())
        total_words += word_count
        st.sidebar.markdown(f"• {file_name} ({word_count:,} words)")

    st.sidebar.metric("Total Words", f"{total_words:,}")

    # Show file content preview
    if st.sidebar.checkbox("Show file content preview"):
        for file_data in st.session_state.all_files_data:
            with st.sidebar.expander(f"📄 {file_data['file_name']}"):
                preview = (
                    file_data["raw_content"][:500] + "..."
                    if len(file_data["raw_content"]) > 500
                    else file_data["raw_content"]
                )
                st.text(preview)
else:
    st.sidebar.warning("📁 No material loaded")
