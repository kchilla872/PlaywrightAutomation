import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
st.set_page_config(page_title="QA Copilot", layout="wide")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pandas as pd
import re

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

# Requirements and scenarios
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

test_scenarios = """
Test Scenarios:
1) Verify that the Product Manager can filter products based on customer satisfaction ratings on the product dashboard.
2) Ensure that products with customer satisfaction ratings above 4.5 are highlighted for prioritization on the product dashboard for the Product Manager.
3) Check that the system displays the message 'No products meet the satisfaction criteria.' when no products have ratings above the specified threshold for the Product Manager.
4) Check that an error message 'Alert system currently unavailable.' is displayed if the alert system fails.
5) Check Product Manager inputs new product ideas into the system for complexity evaluation, ensuring the input interface is user-friendly and intuitive.
"""

def generate_response(prompt, max_tokens=500):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def build_prompt(requirements, scenarios, case_count=10):
    prompt_template = f"""
You are a QA assistant.

TASK:
- Generate exactly {case_count} software test cases.
- STRICT FORMAT:
    * Output exactly {case_count} lines.
    * Each line **must start** with TC + 3-digit number (e.g., TC001).
    * Fields **must be separated** by a single '|' character.
    * Format: [Test Case ID] | [Title] | [Description] | [Steps] | [Expected Result]
    * DO NOT include summaries, extra explanations, markdown, or anything else.
    * JUST the {case_count} lines.

REQUIREMENTS:
{requirements}

TEST SCENARIOS:
{scenarios}

Example:
TC001 | Verify filtering | Check filtering feature | Go to dashboard, apply filter | Products filtered correctly
TC002 | Highlight top products | Check highlight function | Open dashboard, observe highlights | Top products emphasized

Now generate:
"""
    return prompt_template


def parse_test_cases(output, max_cases=2):
    test_cases = []
    # Match lines starting with TCxxx and capturing until next TC or end
    matches = re.findall(r"(TC\d{3}\s*\|.*?)(?=TC\d{3}\s*\||$)", output, re.DOTALL)
    for match in matches:
        parts = [p.strip() for p in match.strip().split("|")]
        if len(parts) == 5:
            test_cases.append(parts)
        if len(test_cases) >= max_cases:
            break
    return test_cases

# Streamlit App
st.title("QA Copilot Requirements Test Case Generator")

st.subheader("Requirements and Scenarios")
with st.expander("Show Requirements"):
    st.write(requirements_text)
with st.expander("Show Test Scenarios"):
    st.write(test_scenarios)

case_count = 2
user_trigger = st.button(f"Generate {case_count} Test Cases")

if user_trigger:
    prompt = build_prompt(requirements_text, test_scenarios, case_count)
    with st.spinner("Generating test cases... Please wait."):
        result = generate_response(prompt)

    st.subheader("Model Raw Output")
    # st.write(f"Length of raw output: {len(result)} characters")
    st.code(result, language="text")

    parsed_cases = parse_test_cases(result, max_cases=case_count)

    if parsed_cases:
        df = pd.DataFrame(parsed_cases, columns=["Test Case ID", "Title", "Description", "Steps", "Expected Result"])
        st.subheader(f"Parsed Test Cases (showing {len(parsed_cases)} cases)")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", data=csv_data, file_name="generated_test_cases.csv", mime="text/csv")
    else:
        st.warning("No test cases were parsed. Please check the model output format or adjust your prompt.")
else:
    st.info("Click the button above to generate test cases based on the fixed requirements.")
