import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema
from langchain_core.messages import HumanMessage

# --------------------------------------------------- AI AGENT CODE --------------------------------------------------------------------------

def curate_question(state: AgentSchema) -> AgentSchema:
    """
    Curates the user's question using an LLM to improve its clarity,
    structure, and overall quality.

    The function extracts the user's original question from the agent state,
    sends it to a low-reasoning LLM for refinement, stores the curated
    question back into the state, and returns the updated state.

    Args:
        state (AgentSchema): The current agent state containing the user's
            original question.

    Returns:
        AgentSchema: The updated agent state containing the curated question
            in the `curated_ques` field.
    """

    user_question = state.user_question

    llm = pick_llm("low")

    response = llm.invoke(f"Curate the following question: {user_question}")

    state.curated_ques = response
    state.messages = state.messages + [HumanMessage(content=f"{response}")]
    
    return state


def prompt_query_context(state: AgentSchema) -> AgentSchema:
    curated_question = state.curated_ques
    
    conn_details = {
        "host": os.environ["DB_HOST"],
        "port": os.environ.get("DB_PORT", "5432"),
        "database": os.environ["DB_DATABASE"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }
    
    obj = DatabaseUtil(conn_details)
    
    schema_info = obj.schema_details("public")
    
    prompt = f"""
    You are an SQL Analyst agent. Your task is to convert the user's natural language query into Postgres SQL query that can be executed
    on the database. You are provided with the user's original query and the schema details of the database, including table names, 
    column names, data types and sample data for each table so that you can understand the structure of the database and generate an
    accurate SQL query. Unless user explicitly asks for specific number of rows, always limit the output to 10 rows. Note - Just generate 
    the SQL query will without any explaination or additional text because this query will be executed directly on the database. So, 
    the output should SQL ready to be executed without any modifications.
    
    User Original Query: {curated_question}
    
    Database Schema Details: 
    {schema_info}
    """
    
    state.prompt_query_context = prompt
    
    llm = pick_llm("medium")
    generated_sql_query = llm.invoke(prompt)
    state.generated_sql_query = generated_sql_query
    
    return state