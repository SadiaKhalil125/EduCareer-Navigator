import joblib
import pandas as pd
import numpy as np
import os
from typing import List, Tuple
from career_agent.career_states import CareerState, CareerRecommendation

class CareerPredictor:
    def __init__(self, model_path: str = None):
        """Initialize the career predictor with the trained model."""
        if model_path is None:
            # Try multiple possible paths for the model file
            possible_paths = [
                "career_predictor_model.pkl",  # Current directory
                "../career_predictor_model.pkl",  # Parent directory
                "../../career_predictor_model.pkl",  # Grandparent directory
                os.path.join(os.path.dirname(__file__), "..", "..", "career_predictor_model.pkl"),  # Absolute path from this file
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    print(f"✅ Found model at: {path}")
                    break
            else:
                model_path = "career_predictor_model.pkl"  # Default fallback
                print(f"⚠️  Model not found in any expected location, using default: {model_path}")
        """Initialize the career predictor with the trained model."""
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Model loaded successfully from {model_path}")
            
            # Load metadata if available
            metadata_path = model_path.replace('.pkl', '_metadata.pkl')
            try:
                self.metadata = joblib.load(metadata_path)
                print(f"✅ Model metadata loaded: {self.metadata}")
            except FileNotFoundError:
                print(f"⚠️  Metadata file not found, using default feature columns")
                self.metadata = {
                    'feature_columns': ['Math', 'Bio', 'Interest_Tech', 'Interest_Art', 'Group_Work', 'Logical_Thinking', 'Likes_Speaking']
                }
                
        except FileNotFoundError:
            print(f"❌ Model file {model_path} not found. Please train the model first.")
            self.model = None
            self.metadata = None
    
    def predict_career(self, state: CareerState) -> List[str]:
        """Predict career based on user inputs (exactly matching CSV features)."""
        if self.model is None:
            print("⚠️  Using fallback prediction - model not loaded")
            return ["IT"]  # Default fallback
        
        # Verify feature columns match training data
        expected_features = self.metadata.get('feature_columns', [
            'Math', 'Bio', 'Interest_Tech', 'Interest_Art', 'Group_Work', 'Logical_Thinking', 'Likes_Speaking'
        ])
        
        print(f"🔍 Expected features: {expected_features}")
        
        # Prepare features for prediction (exactly matching CSV columns)
        features = np.array([[
            state["math_score"],        # Math
            state["bio_score"],         # Bio
            1 if state["interest_tech"] else 0,      # Interest_Tech
            1 if state["interest_art"]else 0,       # Interest_Art
            1 if state["group_work"] else 0,         # Group_Work
            1 if state["logical_thinking"] else 0,   # Logical_Thinking
            1 if state["likes_speaking"] else 0      # Likes_Speaking
        ]])
        
        # print(f"🔍 Input features: {features[0]}")
        # print(f"🔍 Feature mapping: Math={state["math_score"]}, Bio={state["bio_score"]}, Tech={state["interest_tech"]}, Art={state["interest_art"]}, Group={state["group_work"]}, Logical={state["logical_thinking"]}, Speaking={state["likes_speaking"]}")
        
        try:
            # Get prediction probabilities
            probabilities = self.model.predict_proba(features)[0]
            classes = self.model.classes_
            
            print(f"🔍 Model classes: {classes}")
            print(f"🔍 Raw probabilities: {probabilities}")
            
            # Get top 3 predictions with confidence scores
            top_indices = np.argsort(probabilities)[::-1][:3]
            predictions = []
            
            for idx in top_indices:
                if probabilities[idx] > 0.1:  # Only include predictions with >10% confidence
                    predictions.append(classes[idx])
                    print(f"🔍 Selected: {classes[idx]} (confidence: {probabilities[idx]:.3f})")
            
            print(f"🔍 Final predictions: {predictions}")
            return predictions[:3]  # Return top 3 predictions
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return ["IT"]  # Fallback
    
    def get_career_details(self, career_name: str, confidence_score: float = None) -> CareerRecommendation:
        """Get detailed information about a specific career."""
        career_info = self._get_career_database().get(career_name, {})
        
        # Use provided confidence score or default
        if confidence_score is None:
            confidence_score = 0.85  # Default fallback
        
        return CareerRecommendation(
            career_name=career_name,
            confidence_score=confidence_score,
            description=career_info.get("description", f"Career in {career_name}"),
            required_skills=career_info.get("required_skills", ["Problem solving", "Communication"]),
            salary_range=career_info.get("salary_range", "$50,000 - $100,000"),
            job_outlook=career_info.get("job_outlook", "Growing"),
            education_requirements=career_info.get("education_requirements", "Bachelor's degree"),
            companies=career_info.get("companies", ["Top companies in the field"])
        )
    
    def _get_career_database(self) -> dict:
        """Database of career information."""
        return {
            "IT": {
                "description": "Information Technology professionals work with computer systems, software, and networks to solve business problems.",
                "required_skills": ["Programming", "Problem solving", "Analytical thinking", "Communication"],
                "salary_range": "$60,000 - $150,000",
                "job_outlook": "Excellent growth",
                "education_requirements": "Bachelor's in Computer Science or related field",
                "companies": ["Google", "Microsoft", "Apple", "Amazon", "Meta"]
            },
            "Engineering": {
                "description": "Engineers apply scientific and mathematical principles to design and build solutions for real-world problems.",
                "required_skills": ["Mathematics", "Physics", "Design thinking", "Project management"],
                "salary_range": "$70,000 - $130,000",
                "job_outlook": "Strong growth",
                "education_requirements": "Bachelor's in Engineering",
                "companies": ["Tesla", "Boeing", "General Electric", "Intel", "Samsung"]
            },
            "Medicine": {
                "description": "Medical professionals diagnose, treat, and prevent illnesses and injuries in patients.",
                "required_skills": ["Biology", "Chemistry", "Patient care", "Critical thinking"],
                "salary_range": "$200,000 - $400,000",
                "job_outlook": "Excellent growth",
                "education_requirements": "Medical degree (MD/DO)",
                "companies": ["Hospitals", "Clinics", "Research institutions", "Pharmaceutical companies"]
            },
            "Business": {
                "description": "Business professionals manage organizations, develop strategies, and drive growth and profitability.",
                "required_skills": ["Leadership", "Communication", "Analytics", "Strategic thinking"],
                "salary_range": "$50,000 - $200,000",
                "job_outlook": "Good growth",
                "education_requirements": "Bachelor's in Business Administration or related field",
                "companies": ["McKinsey", "Deloitte", "Goldman Sachs", "Amazon", "Apple"]
            },
            "Design": {
                "description": "Designers create visual and user experiences that solve problems and communicate ideas effectively.",
                "required_skills": ["Creativity", "Visual design", "User research", "Prototyping"],
                "salary_range": "$45,000 - $120,000",
                "job_outlook": "Growing",
                "education_requirements": "Bachelor's in Design or related field",
                "companies": ["Adobe", "Figma", "IDEO", "Pentagram", "Frog Design"]
            },
            "Social Sciences": {
                "description": "Social scientists study human behavior, societies, and social relationships to understand and improve society.",
                "required_skills": ["Research", "Analysis", "Writing", "Critical thinking"],
                "salary_range": "$40,000 - $100,000",
                "job_outlook": "Moderate growth",
                "education_requirements": "Bachelor's in Social Sciences or related field",
                "companies": ["Research institutions", "Government agencies", "Non-profits", "Universities"]
            },
            "Education": {
                "description": "Educators teach and inspire students, develop curriculum, and contribute to the learning and development of others.",
                "required_skills": ["Teaching", "Communication", "Patience", "Organization"],
                "salary_range": "$35,000 - $80,000",
                "job_outlook": "Stable",
                "education_requirements": "Bachelor's in Education or related field",
                "companies": ["Schools", "Universities", "Training centers", "Online platforms"]
            }
        } 