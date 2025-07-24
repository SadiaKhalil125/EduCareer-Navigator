#!/usr/bin/env python3
"""
Training script for career prediction model.
Uses the exact same parameters that will be used for prediction.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_and_prepare_data(csv_path: str = "career_mock_data_1000.csv"):
    """Load and prepare data for training."""
    print(f"Loading data from {csv_path}...")
    
    # Load the CSV data
    df = pd.read_csv(csv_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Career distribution:\n{df['Career'].value_counts()}")
    
    # Prepare features (exactly matching the prediction format)
    feature_columns = ['Math', 'Bio', 'Interest_Tech', 'Interest_Art', 'Group_Work', 'Logical_Thinking', 'Likes_Speaking']
    
    X = df[feature_columns].values
    y = df['Career'].values
    
    print(f"Feature columns: {feature_columns}")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    
    return X, y, feature_columns

def train_model(X, y, feature_columns):
    """Train the career prediction model."""
    print("\nTraining Random Forest model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Create and train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nFeature Importance:")
    print(feature_importance)
    
    return model, feature_columns

def save_model(model, feature_columns, model_path: str = "career_predictor_model.pkl"):
    """Save the trained model and metadata."""
    print(f"\nSaving model to {model_path}...")
    
    # Save model
    joblib.dump(model, model_path)
    
    # Save feature columns for reference
    metadata = {
        'feature_columns': feature_columns,
        'model_type': 'RandomForestClassifier',
        'training_date': pd.Timestamp.now().isoformat()
    }
    
    metadata_path = model_path.replace('.pkl', '_metadata.pkl')
    joblib.dump(metadata, metadata_path)
    
    print(f"Model saved successfully!")
    print(f"Model file: {model_path}")
    print(f"Metadata file: {metadata_path}")
    
    return model_path

def test_prediction_consistency(model, feature_columns):
    """Test that prediction format matches training format."""
    print("\nTesting prediction consistency...")
    
    # Create a test case (same format as CareerState)
    test_case = {
        'math_score': 85,
        'bio_score': 70,
        'interest_tech': True,
        'interest_art': False,
        'group_work': True,
        'logical_thinking': True,
        'likes_speaking': False
    }
    
    # Convert to feature array (same as predict_career method)
    features = np.array([[
        test_case['math_score'],
        test_case['bio_score'],
        1 if test_case['interest_tech'] else 0,
        1 if test_case['interest_art'] else 0,
        1 if test_case['group_work'] else 0,
        1 if test_case['logical_thinking'] else 0,
        1 if test_case['likes_speaking'] else 0
    ]])
    
    print(f"Test case: {test_case}")
    print(f"Feature array: {features[0]}")
    print(f"Feature columns: {feature_columns}")
    
    # Make prediction
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    print(f"Prediction: {prediction}")
    print(f"Probabilities: {dict(zip(model.classes_, probabilities))}")
    
    return True

def main():
    """Main training function."""
    print("🚀 Career Prediction Model Training")
    print("=" * 50)
    
    try:
        # Load and prepare data
        X, y, feature_columns = load_and_prepare_data()
        
        # Train model
        model, feature_columns = train_model(X, y, feature_columns)
        
        # Save model
        model_path = save_model(model, feature_columns)
        
        # Test consistency
        test_prediction_consistency(model, feature_columns)
        
        print("\n✅ Training completed successfully!")
        print("\n📋 Summary:")
        print(f"- Model trained on {len(X)} samples")
        print(f"- Features used: {feature_columns}")
        print(f"- Model saved to: {model_path}")
        print(f"- Prediction format matches training format")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 