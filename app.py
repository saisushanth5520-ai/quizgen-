import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from docx import Document

# Hugging Face model repo – instruction-tuned, chat-style
REPO_ID = "microsoft/Phi-3-mini-4k-instruct"

# Create client with Hugging Face access token securely stored in Streamlit secrets
client = InferenceClient(token=st.secrets["hf_token"])

# Extract text from uploaded files
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text.strip()

# Generate quiz questions using Hugging Face chat model
def generate_questions(content):
    prompt = (
        "You are an AI quiz assistant. Based on the following study content, generate 5 quiz questions "
        "(a mix of multiple-choice, true/false, and short answer), and include the correct answers.\n\n"
        f"{content}"
    )
    messages = [
        {"role": "system", "content": "You are a helpful quiz generator."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=REPO_ID,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"❌ Error calling model: {e}")
        return ""

# Streamlit UI
st.title("📘 AI Quiz Generator with Hugging Face (Phi-3)")
st.markdown("Upload your notes (PDF, DOCX, or TXT), and we'll generate quiz questions using AI.")

# File uploader
uploaded_file = st.file_uploader("📄 Upload your notes", type=["pdf", "docx", "txt"])

if uploaded_file:
    content = extract_text(uploaded_file)

    if not content:
        st.error("❗ No usable text found in the uploaded file.")
    else:
        st.subheader("📄 Extracted Content Preview")
        st.write(content[:1000] + ("..." if len(content) > 1000 else ""))

        if st.button("Generate Quiz"):
            with st.spinner("⏳ Generating quiz... please wait."):
                output = generate_questions(content)
            st.subheader("✅ Generated Quiz")
            st.markdown(output)


