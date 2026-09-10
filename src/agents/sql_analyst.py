import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from models.schema import AgentSchema



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

    return state


def prompt_query_context(state: AgentSchema) -> AgentSchema:
    curated_question = state.curated_ques
    