# Import Packages
import logging
import os
import pandas as pd
from dotenv import load_dotenv
import utils as u
import template

import streamlit as st
import openai

from llama_index import SQLDatabase, LLMPredictor, SimpleDirectoryReader, VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index.indices.service_context import ServiceContext
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.indices.loading import load_index_from_storage
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.prompts.base import Prompt
from llama_index.prompts.prompt_type import PromptType

from langchain.chat_models import ChatOpenAI

from sqlalchemy import create_engine


# Function to query unstructured data
def unstructured_data_querying(unstructured_question: str):
    """

    :param unstructured_question:
    :return:
    """
    global pfizer_index_id, merck_index_id

    chunk_size = 1024
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0,
                                                model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(chunk_size=chunk_size,
                                                   llm_predictor=llm_predictor)
    try:
        # Retrieve existing storage context and load pfizer_index and merck_index
        pfizer_storage_context = StorageContext.from_defaults(persist_dir='./storage_pfizer')
        pfizer_index = load_index_from_storage(storage_context=pfizer_storage_context, index_id=pfizer_index_id)

        merck_storage_context = StorageContext.from_defaults(persist_dir='./storage_merck')
        merck_index = load_index_from_storage(storage_context=merck_storage_context, index_id=merck_index_id)

        logging.info('pfizer_index and merck_index loaded')
    except FileNotFoundError:
        # If Index not found, create a new one.
        logging.info('Indexes not found. Creating new ones...')

        # Load Data
        logging.info("Indexes not found. Creating new ones...")

        # Load Data for pfizer
        pfizer_report = SimpleDirectoryReader(input_files=['data/pfizer_sec_filings_10k_2022.pdf'], filename_as_id=True).load_data()
        print(f'Loaded Pfizer SEC Filings 10k with {len(pfizer_report)} pages')
        # Load Data for Merck
        merck_report = SimpleDirectoryReader(input_files=['data/merck_sec_filings_10k_2022.pdf'], filename_as_id=True).load_data()
        print(f'Loaded Merck SEC Filings 10k with {len(merck_report)} pages')
        # Build Indices for Pfizer
        pfizer_index = VectorStoreIndex.from_documents(pfizer_report, service_context=service_context)
        print(f"Built Index for pfizer report with {len(pfizer_index.docstore.docs)} nodes.")
        # Build Indices for Merck
        merck_index = VectorStoreIndex.from_documents(merck_report, service_context=service_context)
        print(f"Built Index for Merck report with {len(merck_index.docstore.docs)} nodes.")

        # Persist Indexes to Disk
        pfizer_index.storage_context.persist(persist_dir="./storage_pfizer")
        merck_index.storage_context.persist(persist_dir="./storage_merck")

        # Update the global variables
        pfizer_index_id = pfizer_index.index_id
        merck_index_id = merck_index.index_id

        # Save Variables to file
        u.save_variables(pfizer_index_id, merck_index_id)

    # Build Query Engine
    pfizer_report_engine = pfizer_index.as_query_engine(similarity_top_k=3)
    merck_report_engine = merck_index.as_query_engine(similarity_top_k=3)

    # Build Query Engine tool
    query_engine_tools = [
        QueryEngineTool(
            query_engine=pfizer_report_engine,
            metadata=ToolMetadata(name='pfizer_report_2022',
                                  description='Provides information on Pfizer SEC 10K filings for 2022')
        ),
        QueryEngineTool(
            query_engine=merck_report_engine,
            metadata=ToolMetadata(name='merck_report_2022',
                                  description='Provides information on Merck SEC 10K filings for 2022')
        )
    ]
    # Define SubQuestionQueryEngine
    sub_question_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools,
                                                               service_context=service_context)
    # Query unstructured question
    response = sub_question_engine.query(unstructured_question)
    st.write(str(response))
