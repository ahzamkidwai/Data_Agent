import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

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

    # state.curated_ques = response.content
    # state.messages = state.messages + [HumanMessage(content=f"{response}")]
    if isinstance(response.content, list):
        curated_question = "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
        )
    else:
        curated_question = response.content

    print("\n\nCurated Question : ", curated_question)

    state.curated_ques = curated_question
    state.messages = state.messages + [AIMessage(content=curated_question)]

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
    
    print("\n\nPrompt Query Context : ", prompt)
    
    state.prompt_query_context = prompt    
    return state


# def generate_sql(state: AgentSchema) -> AgentSchema:
    
#     prompt = state.prompt_query_context
#     llm = pick_llm("medium")
#     generated_sql_query = llm.invoke(prompt).content
#     state.generated_sql_query = generated_sql_query
#     return state


def generate_sql(state: AgentSchema) -> AgentSchema:

    prompt = state.prompt_query_context
    llm = pick_llm("medium")

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        generated_sql_query = "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
        )
    else:
        generated_sql_query = response.content

    generated_sql_query = generated_sql_query.strip()
    if generated_sql_query.startswith("```") and generated_sql_query.endswith("```"):
        generated_sql_query = generated_sql_query[3:-3].strip()
        if generated_sql_query.lower().startswith("sql"):
            generated_sql_query = generated_sql_query[3:].lstrip()
        
    print("\n\nGenerated SQL Query : ", generated_sql_query)
    state.generated_sql_query = generated_sql_query
    return state




def is_safe_sql(state: AgentSchema) -> AgentSchema:
    sql_query = state.generated_sql_query
    
    llm = pick_llm("medium")
    llm_judge = llm.with_structured_output(JudgeSchema)
    
    prompt = f"""You are a SQL judge for data security. Your task is to determine whether the SQL query is safe or not. The SQL 
    query is safe or not. The SQL query should only be used for data retrieval and should not modify the database in any way. Neither the SQL query
    nor the prompt should contain the SQL commands that can modify the database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, 
    CREATE or any other commands that can change the structure or content of the database. If the SQL query is safe, respond with 'YES', otherwise 
    respond with 'NO'. Additionally, provide comments explaining your decision.
    Here's the SQL query to evaluate
    {sql_query}
    """

    response = llm_judge.invoke(prompt).model_dump()
    state.is_safe = response['answer']
    state.comments = response['comments']
    print("\n\nResponse is (is_safe): ", response)
    return state
    


def cancelled_sql(state: AgentSchema) -> AgentSchema:
    comments = state.comments
    
    state.final_answer = f"The Generated SQL query was deemed unsafe to execute. The reason provided by the judge is: {comments}"
    state.messages = state.messages + [AIMessage(content=f"{state.final_answer}")]
    return state


def execute_sql(state: AgentSchema) -> AgentSchema:
    
    sql_query = state.generated_sql_query
    
    conn_details = {
        "host": os.environ["DB_HOST"],
        "port": os.environ.get("DB_PORT", "5432"),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "dbname": os.environ["DB_DATABASE"],
    }
    
    obj = DatabaseUtil(conn_details)
    
    execution_result = obj.execute_sql(sql_query)
    
    print("\n\nExecution Result : ", execution_result)
    
    state.sql_query_execution_result = execution_result
    
    return state


def represent_final_answer(state: AgentSchema) -> AgentSchema:
    
    execution_result = state.sql_query_execution_result
    curated_question = state.curated_ques
    
    llm = pick_llm("low")
    
    prompt = f"""
    You are an SQL analyst agent. Your task is to provide a final answer to the user based on the 
    execution result of the SQL query and the user's original question. The final answer should be
    concise, clear and directly address to the user's query. Avoid including any SQL code or technical
    details in the final answer. The final answer should be in a user-friendly format that is easy to
    understand. If the execution result is empty or does not provide a clear answer to the user's question, explain this in final answer.
    
    Here is the execution result: {execution_result} \n
    Here is the user's original question: {curated_question} \n
    """
    
    llm_response = llm.invoke(prompt).content
    
    state.final_answer = llm_response
    print("\n\nFinal Answer : ", llm_response)
    state.messages = state.messages + [AIMessage(content=f"{llm_response}")]
    
    return state


# ---------------------------------------------------------------------------- GRAPH BUILDING ----------------------------------------------------------------------------------

sql_agent_graph = StateGraph(AgentSchema)

# Nodes 

sql_agent_graph.add_node(curate_question, name="curate_question")
sql_agent_graph.add_node(prompt_query_context, name="prompt_query_context")
sql_agent_graph.add_node(generate_sql, name="generate_sql")
sql_agent_graph.add_node(is_safe_sql, name="is_safe_sql")
sql_agent_graph.add_node(cancelled_sql, name="cancelled_sql")
sql_agent_graph.add_node(execute_sql, name="execute_sql")
sql_agent_graph.add_node(represent_final_answer, name="represent_final_answer")


# Edges

sql_agent_graph.add_edge(START, "curate_question")
sql_agent_graph.add_edge("curate_question", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql")
sql_agent_graph.add_edge("generate_sql", "is_safe_sql")

# Conditional Edge Function

def is_safe_sql_edge(state: AgentSchema) -> str:
    is_safe = state.is_safe
    
    if is_safe.lower() == "yes":
        return "execute_sql"
    else:
        return "cancelled_sql"
    
sql_agent_graph.add_conditional_edges("is_safe_sql", is_safe_sql_edge, { "execute_sql": "execute_sql", "cancelled_sql": "cancelled_sql" })

sql_agent_graph.add_edge("cancelled_sql", END)
sql_agent_graph.add_edge("execute_sql", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer", END)

sql_analyst = sql_agent_graph.compile()

if __name__ == "__main__":
    # Graph Compilation

    from IPython.display import display, Image
    img = Image(sql_analyst.get_graph().draw_mermaid_png())
    with open("sql_analyst_graph.png", "wb") as f:
        f.write(img.data)
        
    input_schema = {
        "messages": [],
        "user_question": "What are the different types of payment methods we have in our database? ",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }
    
    # Execute the graph
    sql_analyst_response = sql_analyst.invoke(input_schema)
    print("\n\nSQL Analyst Response : ", sql_analyst_response)