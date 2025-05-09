import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
st.set_page_config(page_title="QA Copilot", layout="wide")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load model once
@st.cache_resource
def load_model():
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Hardcoded requirements
requirements_text = """
Requirements:
1) US1_R1 - As a Product Manager, I want to identify products with high customer satisfaction ratings so that we can prioritize them for development.
Description: Focuses on developing and selecting products that deliver exceptional value, with the goal of maximizing customer satisfaction and building long-term loyalty.
2) US2_R2 - As a Product Manager, I want to assess the feasibility of product development and selection as complicated or challenging so that we can allocate resources effectively.
Description: The system should allow the Product Manager to input new product ideas for complexity evaluation.
3) US3_R3 - As a Product Manager, I want to compare product value measures against competitors so that we can enhance our offerings.
Description: Focuses on assessing whether product development efforts are feasible, particularly when categorized as complicated or challenging, so the team can decide how to best assign resources.
4) US4_R4 - As a Store Manager, I want to monitor store activity with IoT to achieve high business value through outstanding productivity.
Description: Setting up IoT-based monitoring in the store to achieve high productivity and maximize business value.
5) US5_R5 - As a Data Analyst, I want to assess the feasibility of customer behavior modeling as very challenging so that we can allocate resources appropriately.
Description: The system should allow the Data Analyst to input parameters for customer behavior models.
"""

def generate_response(prompt, max_tokens=1500):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Streamlit App
st.title("QA Copilot: Test Plan Generator")

st.subheader("Project Requirements")
with st.expander("Show Requirements"):
    st.write(requirements_text)

st.header("Generate Test Plan")

set_prompt = st.text_input("Prompt (optional)", value="Generate a detailed test plan based on the uploaded requirements.")
user_trigger = st.button("Generate Test Plan")

if user_trigger:
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
{requirements_text}
"""

    with st.spinner("Generating test plan... Please wait, this may take a minute."):
        result = generate_response(refined_prompt)

    st.subheader("Generated Test Plan")
    st.text_area("Test Plan Output", result, height=500)

    raw_output = result.encode('utf-8')
    st.download_button("Download Test Plan", data=raw_output, file_name="generated_test_plan.txt", mime="text/plain")
