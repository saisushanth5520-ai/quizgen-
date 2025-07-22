import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from docx import Document

# Hugging Face model and client setup
REPO_ID = "microsoft/Phi-3-mini-4k-instruct"

client = InferenceClient(token=st.secrets["hf_token"])

# Extract content from uploaded files
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

# Generate quiz questions via Phi-3 hosted model
def generate_questions(content):
    prompt = (
        "You are an AI quiz assistant. Based on the following study content, generate 5 quiz questions "
        "(mixed types: multiple choice, true/false, and short answer) with their correct answers.\n\n"
        f"{content.strip()}"
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

        # ✅ Validate response
        if response is None:
            return "⚠️ No response received from the model."

        if not hasattr(response, "choices") or not response.choices:
            return "⚠️ Model returned an empty response. Try again."

        return response.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"❌ Error calling model: {e}")
        return "⚠️ Unable to generate questions. Please try again later."

# Streamlit App UI
st.set_page_config(page_title="AI Quiz Generator", page_icon="🧠")
st.title("📘 AI Quiz Generator")
st.markdown("Upload your study notes (PDF, DOCX, or TXT) and get AI-generated quiz questions with answers using Hugging Face 💡")

uploaded_file = st.file_uploader("📄 Upload your notes here", type=["pdf", "docx", "txt"])

if uploaded_file:
    content = extract_text(uploaded_file)

    if not content:
        st.error("❌ No text could be extracted from the uploaded file.")
    else:
        st.subheader("📝 Preview Extracted Content")
        st.write(content[:1000] + (" ..." if len(content) > 1000 else ""))

        if st.button("⚡ Generate Quiz"):
            with st.spinner("Generating quiz... please wait."):
                result = generate_questions(content)

            st.subheader("✅ Generated Quiz Questions")
            st.markdown(result or "❌ No output received.")

