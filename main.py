# Import Packages
import os
import sys
import utils as u
import logging
from dotenv import load_dotenv
import streamlit as st

import openai

from structured_data import structured_data_querying
from unstructured_data import unstructured_data_querying

# Load dotenv lib to retrieve API Keys from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enable Logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

try:
    u.snowflake_sqlalchemy_20_monkey_patches()
except Exception as e:
    raise ValueError("Please run `pip install snowflake-sqlalchemy`")

# Streamlit App Definition

# Title for App
st.title("SEC 10-K Fillings Analysis.")

# Create a sidebar for navigation
st.sidebar.title("Navigation")
selected_query = st.sidebar.radio("Select a Query:", ("Structured Data Query", "Unstructured Data Query"))

# Page for Structured data query
if selected_query == "Structured Data Query":
    st.subheader("Structured Data Query")
    structured_query = st.text_area("Enter your question for structured Cybersyn SEC 10-K filings here", key="structured")
    if st.button("Ask"):
        if structured_query:
            structured_data_querying(structured_query)

# Page for Unstructured data query
elif selected_query == "Unstructured Data Query":
    st.subheader("Unstructured Data Query")
    unstructured_query = st.text_area("Enter your question for unstructured SEC 10-K filings for Pfizer and Merck here", key="unstructured")
    if st.button("Ask"):
        if unstructured_query:
            # Load Variables at Startup
            u.load_variables()
            unstructured_data_querying(unstructured_query)
