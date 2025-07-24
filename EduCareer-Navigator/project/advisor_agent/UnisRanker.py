from langchain_openai import ChatOpenAI
from advisor_agent.universitiesstates import ListUniversitiesResponse, systemState
import re

def rank_unis(state: systemState):
    """
    A function that ranks universities based on the user's criteria.

    Args:
        state: A systemState object containing user preferences and university details.

    Returns:
        A Pydantic object containing the structured list of ranked universities.
    """
    list_universities = state["universities"]
    ranked_universities = []
    
    # Extract numeric value from fee budget
    fee_budget_str = str(state.get("fee_budget", "0"))
    fee_budget_numeric = 0
    
    # Try to extract numeric value from fee budget string
    try:
        # Remove common currency symbols and extract numbers
        fee_match = re.search(r'[\d,]+', fee_budget_str)
        if fee_match:
            fee_budget_numeric = int(fee_match.group().replace(',', ''))
    except:
        fee_budget_numeric = 0
    
    print(f"Debug - Fee budget: {fee_budget_str} -> {fee_budget_numeric}")
    
    for uni in list_universities:
        try:
            # Extract numeric value from university fee
            uni_fee_str = str(uni.fee_per_semester)
            uni_fee_numeric = 0
            
            fee_match = re.search(r'[\d,]+', uni_fee_str)
            if fee_match:
                uni_fee_numeric = int(fee_match.group().replace(',', ''))
            
            print(f"Debug - University {uni.name}: {uni_fee_str} -> {uni_fee_numeric}")
            
            # Check if university meets criteria
            fee_ok = fee_budget_numeric == 0 or uni_fee_numeric <= fee_budget_numeric
            city_ok = not state.get("city") or uni.city.lower() == state["city"].lower()
            
            if fee_ok and city_ok:
                ranked_universities.append(uni)
                print(f"Debug - Added {uni.name} to ranked list")
            
        except Exception as e:
            print(f"Debug - Error processing university {uni.name}: {e}")
            # If there's an error, still include the university
            ranked_universities.append(uni)
    
    print(f"Debug - Total universities: {len(list_universities)}, Ranked: {len(ranked_universities)}")
    return {"ranked_universities": ranked_universities}