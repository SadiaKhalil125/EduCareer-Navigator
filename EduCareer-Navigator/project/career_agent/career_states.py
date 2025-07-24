from typing import List, Optional, Dict, Any, TypedDict
# from dataclasses import dataclass

# @dataclass
class CareerRecommendation(TypedDict):
    career_name: str
    confidence_score: float
    description: str
    required_skills: List[str]
    salary_range: str
    job_outlook: str
    education_requirements: str
    companies: List[str]

# @dataclass
class CareerState(TypedDict):
    # User input features (exactly matching CSV columns)
    math_score: int
    bio_score: int
    interest_tech: bool
    interest_art: bool
    group_work: bool
    logical_thinking: bool
    likes_speaking: bool
    
    # Processing state
    career_predictions: List[str]
    career_recommendations: List[CareerRecommendation]
    final_recommendation: Optional[CareerRecommendation]
    confidence_threshold: float
    user_approval: Optional[str]
    
    # Graph state
    current_step: str
    processing_complete: bool 