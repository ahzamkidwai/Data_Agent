import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from Models.schema import ETLAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from langchain_openrouter import ChatOpenRouter


@tool
def extract_load_tool(url: str, output_folder:str, format: str) -> str:
    """
    This tool extracts the data from the API (url) and loads it into the desired location (output_folder)

    Args:
        url (str): The API Endpoint fromm which to extract the data.
        output_folder (str): The folder data where the extracted data will be saved.
        format (str): The format in which to save the extracted data (csv, json, parquet).

    Returns:
        str: A message indicating the success or failure of the operation.
    """
    etl_tools = ETLTools()
    return etl_tools.extract_load(url, output_folder, format)

@tool
def transform_load_tool(input_file_path: str, output_folder: str, output_format: str, user_question: str) -> str:
    """This tool transforms the data from the specified file and loads it into the desired location (output_folder)

    Args:
        input_file_path (str): The path to the file containing the data to be transformed.
        output_folder (str): The folder where the transformed data will be saved.
        output_format (str): The format in which to save the transformed data(csv, json, parquet).

    Returns:
        str: A message indicating the success or failure of the operation.
    """
    etl_tools = ETLTools()
    top_3_rows = etl_tools.transform_load_context(input_file_path, output_folder, output_format)
    
    llm = pick_llm("claude")
    
    prompt = f"""
        You are a python data analyst who uses Pandas to analyze the data. You need to provide only the Pandas code that will help to perform
        the right ETL operations as per the user's question. Do not provide any explainations or comments, only the code should be provided.T
        The code should be in a format that can be executed in a python environment with Pandas installed.
        Don't write anything else that Pandas code.
    
        Create a Pandas dataframe from the data stored in the file: {input_file_path} and then write the code to transform and save the data at {output_folder}.
        Here's the user's question: {user_question}\n
        Here's the context of the data you will be analyzing: {top_3_rows} \n
    """
        
    response = llm.invoke(prompt)
    
    # Optional Cleaning
    pandas_code = response.strip().strip('```').strip().lstrip('python').strip()
    
    # Execute the pandas code in a safe environmnts
    result_code = etl_tools.execute_code(pandas_code)
    
    return f"The data is transformed and saved at {output_folder} in {output_format} format.\n\n Pandas Code Executed : {pandas_code} \n\n Execution Result : {result_code}"


tools = [extract_load_tool, transform_load_tool]
llm = pick_llm('claude')
llm_bind = llm.bind_tools(tools)