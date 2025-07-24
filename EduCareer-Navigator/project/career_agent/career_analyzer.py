from typing import List
import numpy as np
from career_agent.career_states import CareerState, CareerRecommendation
from career_agent.career_predictor import CareerPredictor

def analyze_career_predictions(state: CareerState) -> CareerState:
    """Analyze career predictions and create detailed recommendations."""
    predictor = CareerPredictor()
    
    # Get career predictions with confidence scores
    predictions = predictor.predict_career(state)
    state["career_predictions"] = predictions
    
    # Get prediction probabilities for confidence scores
    if predictor.model is not None:
        # Prepare features for getting probabilities
        features = np.array([[
            state["math_score"],
            state["bio_score"],
            1 if state["interest_tech"] else 0,
            1 if state["interest_art"] else 0,
            1 if state["group_work"] else 0,
            1 if state["logical_thinking"] else 0,
            1 if state["likes_speaking"] else 0
        ]])
        
        try:
            probabilities = predictor.model.predict_proba(features)[0]
            classes = predictor.model.classes_
            # Create mapping of career names to probabilities
            career_probabilities = dict(zip(classes, probabilities))
        except Exception as e:
            print(f"⚠️  Error getting probabilities: {e}")
            career_probabilities = {}
    else:
        career_probabilities = {}
    
    # Create detailed recommendations for each prediction
    recommendations = []
    for career_name in predictions:
        # Get confidence score from model probabilities
        confidence_score = career_probabilities.get(career_name, 0.85)
        career_detail = predictor.get_career_details(career_name, confidence_score)
        
        # Adjust recommendation based on user preferences
        adjusted_recommendation = _adjust_for_preferences(career_detail, state)
        recommendations.append(adjusted_recommendation)
    
    state["career_recommendations"] = recommendations
    state["current_step"] = "analyzed"
    
    return state

def _adjust_for_preferences(career: CareerRecommendation, state: CareerState) -> CareerRecommendation:
    """Adjust career recommendation based on user preferences (using only CSV features)."""
    # Adjust confidence score based on the 7 features from CSV
    confidence_adjustment = 0.0
    
    # Math score adjustment (higher math = better for IT, Engineering)
    if state["math_score"] > 80:
        if "IT" in career["career_name"] or "Engineering" in career["career_name"]:
            confidence_adjustment += 0.1
    
    # Bio score adjustment (higher bio = better for Medicine, Biology-related)
    if state["bio_score"] > 80:
        if "Medicine" in career["career_name"]:
            confidence_adjustment += 0.1
    
    # Interest adjustments
    if state["interest_tech"] and "IT" in career["career_name"]:
        confidence_adjustment += 0.15
    
    if state["interest_art"] and "Design" in career["career_name"]:
        confidence_adjustment += 0.15
    
    # Work preference adjustments
    if state["group_work"] and "Business" in career["career_name"]:
        confidence_adjustment += 0.1
    
    if state["logical_thinking"] and ("IT" in career["career_name"] or "Engineering" in career["career_name"]):
        confidence_adjustment += 0.1
    
    if state["likes_speaking"] and "Education" in career["career_name"]:
        confidence_adjustment += 0.1
    
    # Update confidence score
    career["confidence_score"]= min(1.0, career["confidence_score"] + confidence_adjustment)
    
    return career

def rank_career_recommendations(state: CareerState) -> CareerState:
    """Rank career recommendations by confidence and preference alignment."""
    if not state["career_recommendations"]:
        return state
    
    # Sort by confidence score
    sorted_recommendations = sorted(
        state["career_recommendations"],
        key=lambda x: x["confidence_score"],
        reverse=True
    )
    
    state["career_recommendations"] = sorted_recommendations
    
    # Set the top recommendation as final
    if sorted_recommendations:
        state["final_recommendation"] = sorted_recommendations[0]
    
    state["current_step"] = "ranked"
    return state

def validate_user_inputs(state: CareerState) -> CareerState:
    """Validate user inputs and provide feedback."""
    validation_issues = []
    
    # Check score ranges
    if not (0 <= state["math_score"] <= 100):
        validation_issues.append("Math score should be between 0 and 100")
    
    if not (0 <= state["bio_score"] <= 100):
        validation_issues.append("Biology score should be between 0 and 100")
    
    # Check if at least one interest is selected
    if not (state["interest_tech"] or state["interest_art"]):
        validation_issues.append("Please select at least one area of interest")
    
    # Check if at least one work preference is selected
    if not (state["group_work"] or state["logical_thinking"] or state["likes_speaking"]):
        validation_issues.append("Please select at least one work preference")
    
    if validation_issues:
        state["current_step"] = "validation_error"
        # In a real implementation, you might want to store these issues in the state
    else:
        state["current_step"] = "validated"
    
    return state 