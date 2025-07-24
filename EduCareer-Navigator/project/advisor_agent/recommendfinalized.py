from advisor_agent.universitiesstates import systemState

def returnfinalized(state: systemState):
    """
    A simple agent that returns the finalized universities based on user preferences.
    """
    try:
        # Check if ranking was requested
        if state.get("rank_unis") == "yes":
            # Return ranked universities
            return {
                "universities": state.get("ranked_universities", []),
                "ranked": True
            }
        else:
            # Return unranked universities
            return {
                "universities": state.get("universities", []),
                "ranked": False
            }
        
    except Exception as e:
        print(f"An error occurred while finalizing universities: {e}")
        return {
            "universities": [],
            "ranked": False
        }