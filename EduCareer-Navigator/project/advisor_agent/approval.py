from advisor_agent.universitiesstates import systemState
from langgraph.types import Command, interrupt

# Decision node for interrupt
def approve_decision(state: systemState) -> systemState:
    """Ask user for approval to rank universities with enhanced messaging."""
    
    # Count universities found
    university_count = len(state.get('universities', []))
    
    # Create a more informative interrupt message
    if university_count > 0:
        interrupt_message = f"""
I found {university_count} universities matching your criteria!

🤔 Would you like me to:
✅ **Rank them** based on your budget, marks, and location preferences?
   - Personalized ranking algorithm
   - Best matches first
   - Detailed comparison

❌ **Show all** universities without ranking?
   - Faster results
   - Browse all options
   - Make your own decision

Your choice (yes/no)?
        """.strip()
    else:
        interrupt_message = "No universities found. Would you like me to try with broader criteria (yes/no)?"
    
    response = interrupt(interrupt_message)
    
    if response == "yes":
        state['rank_unis'] = "yes"
    else:
        state['rank_unis'] = "no"
    
    return state

def final_decision(state: systemState) -> str:
    """Final decision based on user approval."""
    if state.get('rank_unis') == "yes":
        return "rank_unis"
    return "recommend_finalized_universities"