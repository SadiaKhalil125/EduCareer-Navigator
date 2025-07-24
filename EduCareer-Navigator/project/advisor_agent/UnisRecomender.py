import json
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from advisor_agent.universitiesstates import ListUniversitiesResponse, University, systemState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.exceptions import OutputParserException
from langchain_openai import ChatOpenAI
from langchain_google_community.search import GoogleSearchAPIWrapper
import os
load_dotenv()
# Set up Google Search
os.environ["GOOGLE_CSE_ID"] = "your-cse-id"
os.environ["GOOGLE_API_KEY"] = "your-api-key"


def find_universities(state:systemState):
    """
    A simple agent that searches for university information and structures the output.

    Args:
        user_query: The user's request for university information.

    Returns:
        A Pydantic object containing the structured list of universities.
    """

    user_query = (
    f"Universities in {state['location']} offering {state['degree_preference']} "
    f"with fee per semester under {state['fee_budget']} PKR, "
    f"minimum inter marks requirement of {state['inter_marks']}, "
    f"matric marks {state['matric_marks']}+, "
    f"admission criteria and merit formula, "
    f"with official admission portal links."
    )

    # search_tool = TavilySearch(max_results=7)
    # search_context = search_tool.invoke(f"information on {user_query}")
    search_tool = GoogleSearchAPIWrapper()
    
    search_context = search_tool.run(f"information on {user_query}")

    # Define the prompt template.
    prompt = PromptTemplate(
        template="""You are an expert assistant. Based on the user's query and the provided context, extract the requested information.

                    User Query:
                    {query}

                    Web Search Context:
                    {context}

                    Based *only* on the provided context, extract the details for the user.
                    If a specific piece of information (like exact fees or marks) is not in the context, use a value of 0 or not available if string.
                    """,
                    input_variables=["query", "context"],
    )

    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=1.3)  

    structured_llm = llm.with_structured_output(ListUniversitiesResponse)

    # Create the final chain
    chain = prompt | structured_llm

    try:
        # Invoke the chain
        response = chain.invoke({
            "query": user_query,
            "context": search_context
        })
        print(response)
        return {"universities": response.universities}
    except OutputParserException as e:
        print(f"An error occurred while parsing the output: {e}")
       
        return {"universities": []}
