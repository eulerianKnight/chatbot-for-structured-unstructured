# Import Packages
import os
import pandas as pd
from dotenv import load_dotenv
import template

import streamlit as st

from llama_index import SQLDatabase, LLMPredictor
from llama_index.indices.service_context import ServiceContext
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine
from llama_index.prompts.base import Prompt
from llama_index.prompts.prompt_type import PromptType

from langchain.chat_models import ChatOpenAI

from sqlalchemy import create_engine

import utils as u

# Load Environment Variables for Snowflake connection
load_dotenv()
username = os.environ['SNOWFLAKE_USERNAME']
password = os.environ['SNOWFLAKE_PASSWORD']
account = os.environ['SNOWFLAKE_ORG_ACCOUNT']
db_name = os.environ['SNOWFLAKE_DB_NAME']
schema = os.environ['SNOWFLAKE_SCHEMA_NAME']
warehouse = os.environ['SNOWFLAKE_WAREHOUSE_NAME']
role = os.environ['SNOWFLAKE_ROLE']


# Function to query Structured data
def structured_data_querying(structured_question: str):
    """

    :param structured_question:
    :return:
    """
    snowflake_uri = f"snowflake://{username}:{password}@{account}/{db_name}/{schema}?warehouse={warehouse}&role={role}"

    # Define Model Parser and LLM
    chunk_size = 1024
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0,
                                                model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(chunk_size=chunk_size,
                                                   llm_predictor=llm_predictor)
    engine = create_engine(snowflake_uri)

    sql_database = SQLDatabase(engine)

    TEXT_TO_SQL_PROMPT = Prompt(
        template.TEXT_TO_SQL_TMPL,
        prompt_type=PromptType.TEXT_TO_SQL
    )

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=['sec_cik_index', 'sec_report_attributes'],
        service_context=service_context,
        text_to_sql_prompt=TEXT_TO_SQL_PROMPT
    )

    response = query_engine.query(structured_question)
    sql_query = response.metadata['sql_query']
    print(f">>> sql query: {sql_query}")

    con = engine.connect()
    df = pd.read_sql(sql_query, con)
    st.write(df)
    st.area_chart(df, x="company_name", y="revenue")
    return df
