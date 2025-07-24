# Career Advisor Agent

A machine learning-powered career recommendation system that analyzes user profiles and suggests suitable career paths using LangGraph workflow.

## Features

- 🤖 **ML-Powered Predictions**: Uses trained Random Forest model for career predictions
- 📊 **Comprehensive Analysis**: Considers academic performance, interests, and preferences
- 🎯 **Personalized Recommendations**: Tailored suggestions based on user profile
- 🔄 **Graph-Based Workflow**: LangGraph-powered processing pipeline
- 💼 **Detailed Career Info**: Salary ranges, required skills, job outlook, and top companies
- 🎨 **Modern UI**: Beautiful Streamlit interface with interactive elements

## Supported Careers

The system can recommend careers in the following fields:
- **IT** (Information Technology)
- **Engineering**
- **Medicine**
- **Business**
- **Design**
- **Social Sciences**
- **Education**

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Model File**: Make sure `career_predictor_model.pkl` is in the parent directory or update the path in `career_predictor.py`.

3. **Run the Application**:
   ```bash
   streamlit run main.py
   ```

## Usage

### 1. Input Your Profile
- **Academic Performance**: Enter your Math and Biology scores (0-100)
- **Interests**: Select your interest in Technology and/or Arts
- **Work Preferences**: Choose your preferences for group work, logical thinking, and public speaking
- **Personal Preferences**: Set your preferred location, salary expectations, work environment, and education level

### 2. Get Recommendations
- Click "Get Career Recommendations" to process your profile
- The system will analyze your inputs using the trained ML model
- Receive personalized career suggestions with confidence scores

### 3. Review Results
- **Top Recommendation**: The best-matched career with detailed information
- **All Recommendations**: Complete list of suggested careers with explanations
- **Career Details**: Salary ranges, required skills, job outlook, and top companies

## System Architecture

### Components

1. **Career States** (`career_states.py`): Data structures for user inputs and recommendations
2. **Career Predictor** (`career_predictor.py`): ML model interface and career database
3. **Career Analyzer** (`career_analyzer.py`): Analysis and ranking logic
4. **Career Approval** (`career_approval.py`): User approval workflow (for advanced version)
5. **Career Graph** (`career_graph.py`): LangGraph workflow definition
6. **Main Interface** (`main.py`): Streamlit user interface

### Workflow

```
User Input → Validation → ML Prediction → Analysis → Ranking → Recommendations
```

## Model Information

- **Algorithm**: Random Forest Classifier
- **Features**: Math score, Biology score, interests, work preferences
- **Training Data**: 1000+ career profiles with various combinations
- **Accuracy**: Varies based on data quality and feature relevance

## Customization

### Adding New Careers
1. Update the career database in `career_predictor.py`
2. Retrain the model with new data
3. Update the supported careers list in the UI

### Modifying Features
1. Update the `CareerState` dataclass in `career_states.py`
2. Modify the prediction logic in `career_predictor.py`
3. Update the UI form in `main.py`

### Adjusting Recommendations
1. Modify the preference adjustment logic in `career_analyzer.py`
2. Update confidence thresholds and scoring algorithms
3. Customize the ranking criteria

## Troubleshooting

### Common Issues

1. **Model Not Found**: Ensure `career_predictor_model.pkl` exists in the correct path
2. **Import Errors**: Check that all dependencies are installed correctly
3. **Graph Initialization**: Verify LangGraph version compatibility

### Debug Mode
Enable debug information by setting environment variable:
```bash
export STREAMLIT_DEBUG=true
streamlit run main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue in the repository or contact the development team. 