import streamlit as st
from datetime import datetime
from meeting_helper_v2.crew import MeetingTool
import os
import sys
import io
import threading
import queue
import re
import pdfplumber
from docx import Document

st.set_page_config(page_title="Meeting Notes Tool", page_icon="📝", layout="wide")

st.markdown(f"""
    <style>
    /* Deep dark background */
    .stApp {{
        background-color: #0F0F12;
    }}

    /* Sidebar with a subtle gradient and Apricot text */
    [data-testid="stSidebar"] {{
        background-color: #1A1A21 !important;
        border-right: 2px solid #FA005F;
    }}

    /* Headers and labels in your light Apricot color */
    h1, h2, h3, label, p {{
        color: #FCD2B0 !important;
    }}

    /* Input areas with Apricot text and Fuchsia focus */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: #14141A !important;
        color: #FCD2B0 !important;
        border: 1px solid #333333 !important;
    }}
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border: 1px solid #FA005F !important;
        box-shadow: 0 0 5px #FA005F;
    }}

    /* The 'Fuchsia to Apricot' Button Transition */
    .stButton>button {{
        background-color: #FA005F !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 14px 0 rgba(250, 0, 95, 0.39);
        transition: all 0.2s ease-in-out;
    }}

    .stButton>button:hover {{
        background-color: #FCD2B0 !important;
        color: #0F0F12 !important;
        box-shadow: 0 6px 20px rgba(252, 210, 176, 0.23);
        transform: scale(1.02);
    }}

    /* Streamlit's radio buttons and checkboxes */
    .stRadio label p {{
        color: #FCD2B0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\[0m|\[92m|\[32m|\[33m|\[[0-9]+m')
    return ansi_escape.sub('', text).strip()

def extract_text_from_pdf(file) -> str:
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

st.set_page_config(page_title="Meeting Notes Tool", page_icon="📝", layout="wide")

st.title("📝 AI Meeting Document Factory")
st.markdown("Paste your transcript or upload a file to generate structured notes.")

with st.sidebar:
    st.header("Settings")
    topic = st.text_input("Meeting Topic", "Personal Project Update")

    st.divider()

    st.header("🔑 API Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    if not api_key and not os.environ.get("OPENAI_API_KEY"):
        st.warning("Enter your OpenAI API key to get started.")
    else:
        st.success("API key set ✅")

# Input method toggle
input_method = st.radio("Input Method", ["Paste Text", "Upload File"], horizontal=True)

transcript_input = ""

if input_method == "Paste Text":
    transcript_input = st.text_area(
        "Meeting Transcript",
        height=300,
        placeholder="Paste Zoom/Teams transcript here..."
    )
else:
    uploaded_file = st.file_uploader("Upload Transcript", type=["pdf", "docx"])
    if uploaded_file:
        with st.spinner("Extracting text..."):
            if uploaded_file.name.endswith(".pdf"):
                transcript_input = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                transcript_input = extract_text_from_docx(uploaded_file)

        st.success(f"Extracted {len(transcript_input.split())} words from {uploaded_file.name}")
        st.text_area("Extracted Text (Preview)", transcript_input, height=200, disabled=True)

if st.button("Generate Meeting Notes"):
    resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    if not resolved_api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not transcript_input:
        st.error("Please paste a transcript or upload a file first!")
    else:
        os.environ["OPENAI_API_KEY"] = resolved_api_key

        result_queue = queue.Queue()
        log_queue = queue.Queue()

        inputs = {
            'transcript': transcript_input,
            'current_year': str(datetime.now().year)
        }

        def run_crew():
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            class QueueWriter(io.TextIOBase):
                def write(self, text):
                    if text and text.strip():
                        log_queue.put(text)
                    return len(text) if text else 0

                def flush(self):
                    pass

            writer = QueueWriter()
            sys.stdout = writer
            sys.stderr = writer

            try:
                result = MeetingTool().crew().kickoff(inputs=inputs)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", e))
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        thread = threading.Thread(target=run_crew, daemon=True)
        thread.start()

        with st.status("Agents are working...", expanded=True) as status:
            log_placeholder = st.empty()
            log_lines = []

            while thread.is_alive() or not log_queue.empty():
                try:
                    while True:
                        line = log_queue.get_nowait()
                        log_lines.append(strip_ansi(line))
                        if len(log_lines) > 30:
                            log_lines.pop(0)
                        log_placeholder.code("".join(log_lines), language=None)
                except queue.Empty:
                    pass
                thread.join(timeout=0.3)

        log_placeholder.empty()

        outcome, payload = result_queue.get()

        if outcome == "error":
            st.error(f"An error occurred: {payload}")
        else:
            result = payload
            status.update(label="✅ Notes Generated!", state="complete", expanded=False)

            if hasattr(result, "raw"):
                clean_output = strip_ansi(result.raw)
            elif hasattr(result, "final_output"):
                clean_output = strip_ansi(result.final_output)
            else:
                clean_output = strip_ansi(str(result))

            st.subheader("Final Output")
            st.markdown(clean_output)

            st.download_button(
                label="Download as Markdown",
                data=clean_output,
                file_name=f"Meeting_Notes_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )