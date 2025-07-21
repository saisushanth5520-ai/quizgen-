import streamlit as st
import openai
import PyPDF2
from docx import Document

# Store your API key securely (on Streamlit, use st.secrets)
openai.api_key = st.secrets["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"]

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

def generate_questions(content):
    prompt = f'''
    Generate 5 quiz questions (mixed: MCQs, True/False, Short Answer) from this content:
    \"\"\"{content}\"\"\"
    Format:
    - Type: ...
    - Question: ...
    - Options (for MCQ only): ...
    - Answer: ...
    '''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

st.title("Quiz Generator")
uploaded_file = st.file_uploader("Upload your notes", type=["pdf", "docx", "txt"])
if uploaded_file:
    content = extract_text(uploaded_file)
    st.text("Extracted Content:")
    st.write(content[:1000] + "...")
    if st.button("Generate Quiz"):
        questions = generate_questions(content)
        st.markdown("### Generated Quiz Questions:")
        st.write(questions)
