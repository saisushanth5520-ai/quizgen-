import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from docx import Document
import json

# Choose your model; "microsoft/Phi-3-mini-4k-instruct" is public & high quality.
REPO_ID = "microsoft/Phi-3-mini-4k-instruct"

# Hugging Face token (in Streamlit secrets—see below)
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
        "Create 5 quiz questions (mix of MCQ, true/false, and short answer), each with an answer, based only on the following content:\n"
        f"{content}\n"
        "Format the quiz in a clean way."
    )
    response = client.post(
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 300, "temperature": 0.7},
            "task": "text-generation",
        }
    )
    try:
        # If response is bytes, decode to string first
        if isinstance(response, bytes):
            result = json.loads(response.decode())
        else:
            result = json.loads(response)
        return result[0]["generated_text"].replace(prompt, "").strip()
    except Exception:
        return "⚠️ Model call failed or response format changed."

st.title("AI Quiz Generator (Hugging Face Hosted Model)")
st.write("Upload notes (PDF, DOCX, or TXT) to get quiz questions powered by free AI.")

uploaded_file = st.file_uploader("Upload your notes", type=["pdf", "docx", "txt"])
if uploaded_file:
    content = extract_text(uploaded_file)
    if not content:
        st.error("❌ Could not extract any text from the file.")
    else:
        st.subheader("Extracted Content Preview")
        st.write(content[:1000] + (" ..." if len(content) > 1000 else ""))
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz... This may take a moment."):
                questions = generate_questions(content)
            st.markdown("### Generated Quiz Questions:")
            st.write(questions)
