import streamlit as st
from openai import OpenAI
import PyPDF2
from docx import Document

client = OpenAI(api_key=st.secrets["api_key"])

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
    Generate 5 quiz questions (mixed types: MCQ, True/False, Short Answer) from this content:
    \"\"\"{content}\"\"\"
    Return only questions and answers in a neat format.
    '''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

st.title("📘 Quiz Generator from Notes")
uploaded_file = st.file_uploader("Upload your notes", type=["pdf", "docx", "txt"])
if uploaded_file:
    content = extract_text(uploaded_file)
    st.text("Extracted Content:")
    st.write(content[:700] + "...")
    if st.button("Generate Quiz"):
        questions = generate_questions(content)
        st.markdown("### Generated Quiz Questions:")
        st.write(questions)
