import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from docx import Document

REPO_ID = "microsoft/Phi-3-mini-4k-instruct"

client = InferenceClient(
    model=REPO_ID,
    token=st.secrets["hf_token"],  # Add your HF token in Streamlit secrets.
    timeout=120,
)

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

def generate_questions(content):
    prompt = (
        "Generate 5 quiz questions in a mix of MCQ, true/false, and short answer formats. "
        "Include answers for each question. Base questions only on this content:\n\n"
        f"{content.strip()}"
    )
    messages = [
        {"role": "system", "content": "You are a quiz generator that outputs only quiz questions and their answers."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.conversational(
            messages=messages,
            max_new_tokens=500,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            stop_sequences=["</s>"],
        )
        return response.strip()
    except Exception as e:
        st.error(f"❌ Error calling model: {e}")
        return ""

st.title("AI Quiz Generator (Phi-3 Powered)")
st.markdown("Upload your school notes (PDF, DOCX, or TXT) to generate quiz questions with answers using AI.")

uploaded_file = st.file_uploader("Upload your notes", type=["pdf", "docx", "txt"])

if uploaded_file:
    content = extract_text(uploaded_file)
    if not content.strip():
        st.error("❌ No readable text found in the uploaded file.")
    else:
        st.subheader("Extracted Content Preview")
        st.write(content[:1000] + (" ..." if len(content) > 1000 else ""))
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz using AI... please wait."):
                questions = generate_questions(content)
            st.markdown("### Generated Quiz Questions")
            st.markdown(questions)

