# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# load_dotenv()

# def pick_llm(level: str):
#     """Pick the appropriate LLM based on the level of the question.

#     Args:
#         level (str): The level of the question, can be "easy", "medium", or "hard".
        
#     Returns:
#         str: The name of the LLM to be used.
#     """
    
#     if level.lower() == "low":
#         llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
#     elif level.lower() == "medium":
#         llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
#     elif level.lower() == "hard":
#         llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash', temperature=0)
#     else:
#         raise ValueError("Invalid level. Chose from 'easy', 'medium', or 'hard'")
    
#     return llm

# if __name__ == "__main__":
#     llm_obj = pick_llm("low")
#     print(llm_obj.invoke("What is the capital city of France?"))


from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv

load_dotenv()


def pick_llm(level: str):
    level = level.lower()

    if level == "low":
        model = "openrouter/free"
    elif level == "medium":
        model = "openrouter/free"
    elif level == "hard":
        model = "openrouter/free"
    else:
        raise ValueError("Invalid level. Choose from 'low', 'medium', or 'hard'.")

    return ChatOpenRouter( model=model, temperature=0, max_retries=0 )


if __name__ == "__main__":
    llm = pick_llm("low")
    response = llm.invoke("What is the capital city of France?")
    print(response.content)
