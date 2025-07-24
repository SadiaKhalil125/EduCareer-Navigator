#!/usr/bin/env python3
"""
Supervisor Agent for University and Career Guidance Systems
Routes user queries to appropriate guidance systems and handles input parsing
"""
import re
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, Union
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from career_agent.career_states import CareerState
from career_agent.career_graph import create_career_graph
from advisor_agent.universitiesstates import systemState
from advisor_agent.graphsetup import create_advisor_graph
# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent))

# Import the existing agent functions
# from mainagent import get_career_suggestion, get_university_recommendations

load_dotenv()

# --- Input Parsing Functions ---


career_graph = create_career_graph()
advisor_graph = create_advisor_graph()


def parse_career_user_info(text: str):
    """
    Parses a string to extract user information, ensuring no null values in the output.
    Integers default to 0, and booleans default to False.

    Args:
        text: The input string from the user.

    Returns:
        A CareerState object containing the extracted information.
    """
    # Initialize the dictionary with default values.
    data = {
        "math_score": 75,
        "bio_score": 75,
        "interest_tech": False,
        "interest_art": False,
        "group_work": False,
        "logical_thinking": False,
        "likes_speaking": False,
        "career_predictions": [],
        "career_recommendations": [],
        "final_recommendation": None,
        "confidence_threshold": 0.7,
        "user_approval": None,
        "current_step": "",
        "processing_complete": False
    }

    # Extract scores using regular expressions. If found, they overwrite the default 0.
    math_score_match = re.search(r"math score of (\d+)", text, re.IGNORECASE)
    if math_score_match:
        data["math_score"] = int(math_score_match.group(1))

    bio_score_match = re.search(r"biology score of (\d+)", text, re.IGNORECASE)
    if bio_score_match:
        data["bio_score"] = int(bio_score_match.group(1))

    # Check for boolean interests. If a keyword is found, the value is switched to True.
    if "tech" in text.lower() or "technology" in text.lower():
        data["interest_tech"] = True

    if "art" in text.lower() or "artistic" in text.lower():
        data["interest_art"] = True

    if "group work" in text.lower() or "teamwork" in text.lower():
        data["group_work"] = True

    if "logical thinking" in text.lower() or "problem-solving" in text.lower():
        data["logical_thinking"] = True

    if "speaking" in text.lower() or "presentations" in text.lower():
        data["likes_speaking"] = True

    return career_graph.invoke(data)

def parse_student_unidata(text: str) -> systemState:
    """
    Parses a string to extract a student's profile information, ensuring no null values.
    - Integers default to 0.
    - Booleans default to False.
    - Strings default to an empty string.

    Args:
        text: The input string from the user.

    Returns:
        A dictionary containing the extracted student profile information.
    """
    # Initialize the dictionary with all required fields and their default values.
    profile = {
        
        # New fields
        "matric_marks": 0,
        "inter_marks" :0,
        "degree_preference":"",
        "city": "",
        "location":"",
        "fee_budget":"",
        "universities":[],
        "ranked_universities":[],
        "rank_unis":"no"
    }

    # --- Marks and Scores (Integers) ---
    matric_match = re.search(r"(?:matric|matriculation)\s.*?(\d{3,4})", text, re.IGNORECASE)
    if matric_match:
        profile["matric_marks"] = int(matric_match.group(1))

    inter_match = re.search(r"(?:inter|intermediate)\s.*?(\d{3,4})", text, re.IGNORECASE)
    if inter_match:
        profile["inter_marks"] = int(inter_match.group(1))

    # --- Profile Details (Strings) ---
    degree_match = re.search(r"(?:study|degree in|major in|interested in)\s+([A-Za-z\s]+?)(?:in|,|at|with|$)", text, re.IGNORECASE)
    if degree_match:
        profile["degree_preference"] = degree_match.group(1).strip().replace("a degree in", "").strip()

    known_cities = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Quetta", "Multan", "Sialkot"]
    for city in known_cities:
        if re.search(r'\b' + city + r'\b', text, re.IGNORECASE):
            profile["city"] = city
            break

    location_match = re.search(r"(?:location|campus is in|located in)\s+([A-Za-z\s]+?)(?:,|\.|$)", text, re.IGNORECASE)
    if location_match:
        profile["location"] = location_match.group(1).strip()
    elif profile["city"]:
        profile["location"] = profile["city"]

    # --- Fee Budget Parsing (IMPROVED LOGIC) ---
    fee_budget_str = ""
    
    fee_patterns = [
        r"((?:Rs\.?|PKR)\s*[\d,]+\.?\d*)",      # Catches "Rs. 150,000" or "PKR 200000"
        r"([\d,]+\.?\d*\s*(?:k|lac|lakh|PKR))", # Catches "150k", "2.5 lac", "250,000 PKR"
    ]

    # First, try to find a high-confidence match.
    for pattern in fee_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fee_budget_str = match.group(1).strip()
            break  # Found a good match, so we can stop.

    if not fee_budget_str:
        fallback_match = re.search(r"(?:fee|budget|afford|cost)\D*?(\d[\d,.]*)", text, re.IGNORECASE)
        if fallback_match:
            fee_budget_str = fallback_match.group(1).strip()

    profile["fee_budget"] = fee_budget_str

    return advisor_graph.invoke(profile)

career_suggestion_tool = Tool(
    name="CareerSuggestionAgent",
    description="""

    Use this tool when the user wants career guidance or career recommendations.
    
    Input is string containing all info and result will be returned from tool

    Output: Career recommendations based on the user's profile.
    """,
    func=lambda x: career_graph.invoke(parse_career_user_info(x))
)

university_recommendations_tool = Tool(
    name="UniversityRecommendationsAgent",
    description="""
    Use this tool when the user wants university recommendations or admission guidance.
    
    Input will be string containing all info and result will be returned from tool
    
    Output: University recommendations based on the user's academic profile and preferences.
    """,
    func=lambda x: advisor_graph.invoke(parse_student_unidata(x))
)

# --- Tools List ---
tools = [
    career_suggestion_tool,
    university_recommendations_tool
]

# --- System Prompt ---
system_prompt = """
You are a SupervisorAgent responsible for helping users with educational and career guidance.

You have access to the following tools:
1. **CareerSuggestionAgent** - Provides career recommendations based on academic scores, interests, and work preferences.
2. **UniversityRecommendationsAgent** - Provides university recommendations based on academic marks, degree preferences, and budget.

Your responsibilities:
- Understand the user's query and decide which tool(s) should be called.
- Handle both career guidance and university admission queries appropriately.

-IMPORTANT GUIDELINE
-Whatever user sends as query pass to corresponding tool without asking further

-career guidance query will be including parameters like math score, biology score,etc
-universities recommendation one will be receiving like fee budget, matric and inter marks, etc
-just pass prompt to the respective tool call

Reply to the user in a helpful and conversational tone, and always provide clear guidance on what information you need
and shows everything tool returns.

"""
# --- Agent Setup ---
llm = ChatOpenAI()

# Create a checkpointer for the supervisor agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# SQLite checkpointer for supervisor agent
supervisor_db = sqlite3.connect("supervisor_graph.db", check_same_thread=False)
supervisor_memorybox = SqliteSaver(supervisor_db)

supervisor_agent = create_react_agent(
    tools=tools,
    model=llm,
    checkpointer=supervisor_memorybox
) 