import streamlit as st
import requests
import PyPDF2
from docx import Document

# Change to another model if desired

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

def generate_questions(content):
    prompt = (
        "Create 5 quiz questions (a mix of MCQ, true/false, and short answer) "
        "with answers, based on the following content:\n"
        f"{content}\n"
        "Return only the questions and answers in clear display format."
    )
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 512, "temperature": 0.7}
    }
    HF_MODEL ="tiiuae/falcon-7b-instruct"
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "").replace(prompt, "").strip()
        elif isinstance(result, dict):
            return result.get("generated_text", "").replace(prompt, "").strip()
        else:
            return "⚠️ Unexpected response format."
    elif response.status_code == 503:
        return "⏳ Model is loading or busy, please try again in a minute."
    else:
        return f"❌ Error {response.status_code}: {response.text}"

st.title("Quiz Generator (with Hugging Face)")
st.write("Upload your notes (PDF, DOCX, or TXT) and get instant quiz questions powered by a free AI model.")

uploaded_file = st.file_uploader("Upload your notes", type=["pdf", "docx", "txt"])
if uploaded_file:
    content = extract_text(uploaded_file)
    st.subheader("Extracted Content Preview")
    st.write(content[:1000] + ("..." if len(content) > 1000 else ""))
    if st.button("Generate Quiz"):
        with st.spinner('Generating quiz... please wait'):
            questions = generate_questions(content)
        st.markdown("### Generated Quiz Questions:")
        st.write(questions)
