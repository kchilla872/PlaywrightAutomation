import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
st.set_page_config(page_title="QA Copilot", layout="wide")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pandas as pd
from docx import Document
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

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(**inputs, max_new_tokens=1500)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_test_cases(output, max_cases=20):
    test_cases = []
    chunks = re.split(r'(?=TC\d{3})', output)
    pattern = re.compile(r'^(TC\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*)$')
    for chunk in chunks:
        line = chunk.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            test_cases.append([
                match.group(1).strip(),
                match.group(2).strip(),
                match.group(3).strip(),
                match.group(4).strip(),
                match.group(5).strip()
            ])
            if len(test_cases) == max_cases:
                break  # Stop at 20
    return test_cases

def generate_and_parse(prompt):
    result = generate_response(prompt)
    test_cases = parse_test_cases(result, max_cases=20)
    return result, test_cases

# Streamlit UI
st.title("QA Copilot – Test Case Generator")
st.write("Upload a requirements document (.docx) and enter a prompt like 'Generate 20 test cases'.")

uploaded_file = st.file_uploader("Upload .docx requirements file", type="docx")

if uploaded_file:
    context = extract_text_from_docx(uploaded_file)
    st.subheader("Document Preview")
    st.text_area("Extracted Requirements", value=context[:3000], height=250)

    user_prompt = st.text_input("Prompt (e.g., 'Generate 20 test cases')")

    if user_prompt:
        with st.spinner("Generating response... Please wait, this may take a minute."):

            refined_prompt = f"""
You are a QA assistant.

**TASK**: Based on the following requirements, generate **exactly 20 unique software test cases**.

**STRICT OUTPUT RULES**:
- Output exactly 20 lines — no more, no less.
- Each line is **one test case only**.
- Each test case must **start** with 'TC' + 3-digit number (TC001, TC002, ..., TC020).
- Each test case must have exactly 5 fields, separated by the '|' (pipe) character.
- No introductory text, no explanations, no headings, no extra numbering.

**OUTPUT FORMAT EXAMPLE**:
TC001 | Validate associate hiring process | Ensure associate can be added with required details | Navigate to hiring module and add associate info | Associate successfully added
TC002 | Recommend best-fit apparel | Ensure system recommends apparel based on profile | Enter customer profile and preferences | Relevant apparel recommendations displayed
TC003 | Conversational chat interface works | Verify chat responds to customer queries | Start chat and ask product availability | Chat returns accurate availability info
TC004 | Customer behavior modeling accuracy | Check system predicts buying patterns | Analyze past purchases and view prediction | Prediction aligns with known patterns
TC005 | Subscription service activation | Ensure customers can subscribe to service | Select a subscription plan and activate | Subscription confirmed and active
TC006 | Merchandising layout optimization | Verify optimal product placement | Load merchandising tool and simulate layout | Layout optimized based on sales data
TC007 | Demand forecasting accuracy | Check forecast for next quarter sales | Run demand forecast report | Forecast generated with trend insights
TC008 | Real-time pricing updates | Ensure prices update dynamically | Change competitor price inputs | System updates product price in real-time
TC009 | Enhanced search results | Validate improved search functionality | Search for a product keyword | Search returns relevant + upsell options
TC010 | Guided merchandising analysis | Test merchandising insights tool | Run analysis on current merchandise | System provides actionable insights
TC011 | Immersive experience functionality | Verify AR fitting room works | Launch AR fitting on product page | Virtual fitting displays correctly
TC012 | Live commerce interaction | Ensure live shopping session runs | Join a live shopping event | Stream plays and purchase links work
TC013 | IoT store activity monitoring | Check in-store device data feeds | Review IoT dashboard activity | Live data updates accurately
TC014 | Sustainability monitoring accuracy | Verify tracking of sustainable materials | View sustainability report | Report reflects correct material usage
TC015 | Customer personalization | Check tailored offers and messages | Log in as customer with history | Personalized recommendations shown
TC016 | Price and promotion optimization | Ensure promo offers are optimized | Apply multiple discounts | Best price + promo calculated
TC017 | Product development input tracking | Verify feedback integration | Submit product feedback | Feedback logged in development system
TC018 | Risk/fraud detection alerts | Ensure fraud system triggers alert | Simulate suspicious transaction | Alert generated and logged
TC019 | Social monitoring and commerce | Check social media product tagging | Tag product on social platform | Product appears linked in system
TC020 | Visual product search accuracy | Search using product image | Upload image to visual search | Matching products displayed

**REQUIREMENTS TO BASE ON**:
{context}
"""

            result, test_cases = generate_and_parse(refined_prompt)

        st.subheader("Copilot Raw Output")
        st.text_area("Raw Output", result, height=300)

        if test_cases:
            df = pd.DataFrame(test_cases, columns=["Test Case ID", "Description", "Scenario", "Step Action", "Step Expected"])
            st.subheader("Parsed Test Case Table (first 20 only)")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="generated_test_cases.csv", mime="text/csv")
        else:
            st.warning("⚠️ No test cases were parsed. Please check the prompt or the model output format.")
