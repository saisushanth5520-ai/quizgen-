import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from docx import Document

# ✅ Replace with your preferred Hugging Face model
REPO_ID = "microsoft/Phi-3-mini-4k-instruct"

# ✅ Token stored securely in Streamlit secrets
client = InferenceClient(
    model=REPO_ID,
    token=st.secrets["hf_token"],
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
        "Create 5 quiz questions in a mix of MCQ, true/false, and short answer formats. "
        "Include answers for each question. Based on the following content:\n\n"
        f"{content.strip()}"
    )

    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=500,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            stop_sequences=["</s>"],
        )
        return response.strip()
    except Exception as e:
        return f"❌ Error calling model: {e}"

st.title("AI Quiz Generator (Hugging Face Model)")
st.markdown("Upload any school notes (PDF, DOCX, TXT) to get a quiz powered by AI.")

uploaded_file = st.file_uploader("📄 Upload your classroom notes", type=["pdf", "docx", "txt"])

if uploaded_file:
    content = extract_text(uploaded_file)
    if not content.strip():
        st.error("❌ No readable text found in the file.")
    else:
        st.subheader("📚 Extracted Content Preview")
        st.write(content[:1000] + (" ..." if len(content) > 1000 else ""))
        if st.button("⚡ Generate Quiz"):
            with st.spinner("Generating quiz using AI... please wait."):
                questions = generate_questions(content)
            st.success("✅ Quiz generated!")
            st.markdown("### 🎯 Generated Quiz")
            st.markdown(questions)

