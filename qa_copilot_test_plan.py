import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
st.set_page_config(page_title="QA Copilot - Test Plan Generator", layout="wide")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from docx import Document

# Load model once and cache
@st.cache_resource
def load_model():
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(**inputs, max_new_tokens=1500)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

# Streamlit UI
st.title("QA Copilot – Test Plan Generator")
st.write("Upload a requirements document (.docx) and generate a structured test plan.")

uploaded_file = st.file_uploader("Upload .docx requirements file", type="docx")

if uploaded_file:
    context = extract_text_from_docx(uploaded_file)
    st.subheader("Document Preview")
    st.text_area("Extracted Requirements", value=context[:3000], height=250)

    user_prompt = st.text_input("Prompt (optional)", value="Generate a detailed test plan based on the uploaded requirements.")

    if user_prompt:
        with st.spinner("Generating test plan... Please wait, this may take a minute."):

            refined_prompt = f"""
You are a senior QA engineer.

TASK:
Based on the following **requirements**, generate a **concise software test plan** with exactly these four sections only:

1. **Objectives** — Identify the requirements and key goals for the new retail technology project.
2. **Scope** — Define what will be tested (functional modules, integrations) and what will not (non-critical features, out-of-scope systems).
3. **Test Types** — Include one line each for:
    - System Integration Testing (SIT): Ensures integrated modules work together correctly.
    - Regression Testing: Checks that new changes do not break existing functionality.
    - User Acceptance Testing (UAT): Confirms the system meets business and user needs.
    - Performance Testing: Evaluates system speed, scalability, and stability under load.
4. **Test Approach** — Describe:
    - Methods: Combination of manual exploratory tests and automated regression suites.
    - Environments: Dedicated SIT, UAT, and performance testing environments with representative data.
    - Tools: Use tools like Selenium for automation, JMeter for performance, and Postman for API testing.

IMPORTANT:
- Only output these four sections.
- Do NOT list individual test cases or repeat the same lines.
- Keep the language clean, clear, and professional.

REQUIREMENTS:
{context}
"""

            result = generate_response(refined_prompt)

        st.subheader("Generated Test Plan")
        st.text_area("Test Plan Output", result, height=500)

        raw_output = result.encode('utf-8')
        st.download_button("Download Test Plan", data=raw_output, file_name="generated_test_plan.txt", mime="text/plain")
