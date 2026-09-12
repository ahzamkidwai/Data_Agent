from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def pick_llm(level: str):
    """Pick the appropriate LLM based on the level of the question.

    Args:
        level (str): The level of the question, can be "easy", "medium", or "hard".
        
    Returns:
        str: The name of the LLM to be used.
    """
    
    if level.lower() == "low":
        llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
    elif level.lower() == "medium":
        llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
    elif level.lower() == "hard":
        llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
    else:
        raise ValueError("Invalid level. Chose from 'easy', 'medium', or 'hard'")
    
    return llm

if __name__ == "__main__":
    llm_obj = pick_llm("low")
    print(llm_obj.invoke("What is the capital city of France?"))