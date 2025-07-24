from pydantic import BaseModel, Field
from typing import Optional, TypedDict
# 1. Define your desired output structure using Pydantic

# --- Step 1: Define the desired output structure using Pydantic ---
class University(BaseModel):
    name: str = Field(description="The name of the university.")
    city: str = Field(description="The city where the university is located.")
    admission_portal:str = Field(description="The URL of the university's admission portal.")
    fee_per_semester: int = Field(description="The estimated fee per semester for the specified program.")
    min_inter_marks: int = Field(description="The minimum intermediate marks required for admission.")
    merit_formula: str = Field(description="The merit formula used for admission, if available.")

class ListUniversitiesResponse(BaseModel):
    universities: list[University] = Field(description="A list of universities that match the user's criteria.")

    
class systemState(TypedDict):
    """Student details and structured list of universities with their admission details."""
    matric_marks: int = Field(description="Matric marks out of 1100")
    inter_marks: int = Field(description="Inter marks out of 1100")
    degree_preference: str = Field(description="Preferred degree program")
    city: str = Field(description="Preferred city for university")
    location: str = Field(description="Preferred location for university")
    fee_budget: str = Field(description="Maximum fee budget per semester")
    rank_unis:str = Field(description="User wants to rank or not (yes or no)")
    universities: Optional[list[University]] = Field(description="List of universities with their admission details")
    ranked_universities: Optional[list[University]]= Field(description="List of universities ranked based on user budget and inter marks")
