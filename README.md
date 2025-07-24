# 🎓💼 University Admission & Career Guidance Assistant

**Idea Credits** (Core Idea credit goes to Fassih Shah) 
https://github.com/FassihShah


A comprehensive AI-powered guidance system that provides personalized university admissions advice and career recommendations using LangGraph workflows, machine learning, and MongoDB for persistent chat history.


## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Components](#components)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This project is an intelligent guidance assistant that combines university admissions counseling with career planning. It uses advanced AI workflows to provide personalized recommendations based on academic performance, interests, and preferences.

### Key Capabilities

- **🎓 University Guidance**: Personalized university recommendations with admission requirements, fee structures, and merit calculations
- **💼 Career Guidance**: ML-powered career suggestions with salary ranges, required skills, and job outlook
- **🤖 AI-Powered**: LangGraph workflows for intelligent conversation and decision-making
- **💾 Persistent Storage**: MongoDB integration for chat history and session management
- **🎨 Modern UI**: Beautiful Streamlit interface with interactive elements

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Chat Interface │  │   Sidebar Tools │  │ Session Mgmt │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Supervisor Agent                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  LangGraph Flow │  │  Tool Routing   │  │  Response    │ │
│  │                 │  │                 │  │  Formatting  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│    University Agent     │  │     Career Agent        │
│  ┌─────────────────────┐│  │  ┌─────────────────────┐│
│  │  Uni Recommender    ││  │  │  Career Predictor   ││
│  │  Uni Ranker         ││  │  │  Career Analyzer    ││
│  │  Approval System    ││  │  │  ML Model (RF)      ││
│  └─────────────────────┘│  │  └─────────────────────┘│
└─────────────────────────┘  └─────────────────────────┘
                    │                   │
                    ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    MongoDB Database                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Chat History   │  │  User Sessions  │  │  Analytics   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🎓 University Guidance
- **Personalized Recommendations**: Based on academic scores, preferences, and budget
- **Real-time Data**: **Google Search API integration** for current university information
- **Admission Requirements**: Detailed entry criteria and merit formulas
- **Fee Structures**: Comprehensive cost analysis and budget planning
- **Location Filtering**: City and region-based university suggestions
- **Merit Calculations**: Automatic merit calculation for different universities
- **Dynamic Content**: Live search results parsed into structured university data

### 💼 Career Guidance
- **ML-Powered Predictions**: **Random Forest model** (scikit-learn) for career recommendations
- **Advanced ML Framework**: Uses **scikit-learn** with optimized hyperparameters
- **Comprehensive Analysis**: Academic performance, interests, and work preferences
- **Salary Information**: Industry-standard salary ranges and growth potential
- **Skills Assessment**: Required skills and education paths
- **Work Environment**: Office vs remote, team vs individual preferences
- **Model Persistence**: Joblib serialization for efficient model loading

### 🤖 AI Capabilities
- **Intelligent Conversations**: Natural language processing for user queries
- **Context Awareness**: Maintains conversation context across sessions
- **Tool Integration**: Seamless switching between university and career guidance
- **Response Formatting**: Beautiful, structured responses with markdown

### 💾 Data Management
- **Persistent Chat History**: MongoDB storage for all conversations
- **Session Management**: Save and load previous chat sessions
- **User Tracking**: Individual user history and preferences
- **Search Functionality**: Search through past conversations
- **Analytics**: Usage statistics and insights

## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **MongoDB**: 4.4 or higher (local or cloud)
- **Git**: For cloning the repository
- **Google API Key**: For university search functionality (Google Custom Search Engine)
- **OpenAI API Key**: For AI-powered responses and structured parsing

### Step 1: Clone the Repository

```bash
git clone https://github.com/SadiaKhalil125/EduCareer-Navigator.git
cd EduCareer-Navigator
```

### Step 2: Install Dependencies

```bash
# Install main dependencies
pip install -r project/requirements.txt

# Install career agent dependencies
pip install -r project/career_agent/requirements.txt

# Install database dependencies
pip install -r project/database/requirements.txt
```

### Step 3: Set Up MongoDB

#### Option A: Local MongoDB
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community
```

#### Option B: Docker MongoDB
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### Option C: MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster and get connection string
3. Update environment variables

### Step 4: Environment Configuration

Create a `.env` file in the backend directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=guidance_assistant
MONGODB_COLLECTION=chat_history

# OpenAI API (for AI-powered responses and structured parsing)
OPENAI_API_KEY=your_openai_api_key_here

# Google Search API (for university data retrieval)
GOOGLE_CSE_ID=your_google_cse_id_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional Settings
MONGODB_CONNECT_TIMEOUT_MS=5000
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
MONGODB_SOCKET_TIMEOUT_MS=10000
CREATE_INDEXES=true
MONGODB_LOGGING=false
```

## 🏃 Quick Start

### Launch the Application

```bash
cd project
streamlit run supervisor_main.py
```

The application will open in your browser at `http://localhost:8501`

### First Steps

1. **Welcome Screen**: You'll see the main interface with university and career guidance options
2. **Start Chat**: Type your query in the chat interface
3. **Choose Guidance**: The system will automatically route to university or career guidance based on your query
4. **Get Recommendations**: Receive personalized recommendations with detailed information
5. **Save Sessions**: Use the sidebar to save and load chat sessions

## 🧩 Components

### 1. Supervisor Agent (`project/supervisor_main.py`)

**Purpose**: Main application orchestrator and user interface

**Key Features**:
- Streamlit web interface
- + Both Separate main (interfaces for career + universities recommendation)
- Session state management
- Tool routing and response formatting
- MongoDB integration
- Chat history management

**Key Functions**:
- `supervisor_agent`: Main LangGraph workflow
- `save_chat_message()`: Save individual messages
- `auto_load_last_session()`: Load previous sessions
- `format_career_response()`: Format career recommendations
- `format_university_response()`: Format university recommendations

### 2. University Agent (`project/advisor_agent/`)

**Purpose**: University admissions guidance and recommendations

**Components**:
- **`main.py`**: University agent workflow and interface
- **`UnisRecomender.py`**: University recommendation logic with **SerpAPI integration**
- **`UnisRanker.py`**: University ranking and filtering
- **`approval.py`**: User approval workflow
- **`universitiesstates.py`**: Data structures and state management
- **`graphsetup.py`**: LangGraph workflow setup

**Features**:
- **Real-time Web Search**: Uses **Google Search API** (SerpAPI alternative) for live university data
- **Dynamic Content**: Searches for current admission information, fees, and requirements
- **Structured Output**: AI-powered parsing of search results into structured university data
- **University database with 100+ institutions**
- **Admission requirements and merit formulas**
- **Fee structures and budget analysis**
- **Location-based filtering**
- **Personalized recommendations**

**Implementation Details**:
- **Search Integration**: Uses `GoogleSearchAPIWrapper` from `langchain_google_community.search`
- **API Configuration**: Google Custom Search Engine (CSE) with API key for university data retrieval
- **Structured Parsing**: GPT-4 powered extraction of university information from search results
- **Fallback System**: Handles cases where specific information is not available in search results

### 3. Career Agent (`project/career_agent/`)

**Purpose**: Career guidance and ML-powered recommendations

**Components**:
- **`main.py`**: Career agent workflow and interface
- **`career_predictor.py`**: ML model interface and career database
- **`career_analyzer.py`**: Analysis and ranking logic
- **`career_states.py`**: Data structures
- **`train_model.py`**: Model training script
- **`career_graph.py`**: LangGraph workflow

**Features**:
- **Random Forest ML model** with scikit-learn
- **7 career categories** (IT, Engineering, Medicine, Business, Design, Social Sciences, Education)
- **Salary ranges and job outlook**
- **Skills assessment**
- **Work environment preferences**

**Implementation Details**:
- **Machine Learning Framework**: Uses **scikit-learn** for career prediction
- **Algorithm**: **Random Forest Classifier** with optimized hyperparameters
- **Model Configuration**:
  - `n_estimators=100`: 100 decision trees for robust predictions
  - `max_depth=10`: Controlled tree depth to prevent overfitting
  - `random_state=42`: Reproducible results
  - `class_weight='balanced'`: Handles imbalanced career categories
- **Feature Engineering**: 7 input features (Math score, Biology score, interests, work preferences)
- **Training Data**: 1000+ career profiles with balanced representation
- **Model Persistence**: Uses `joblib` for model serialization and loading
- **Prediction Pipeline**: Returns top 3 career recommendations with confidence scores
- **Fallback System**: Default recommendations when model is unavailable

### 4. Database Layer (`project/database/`)

**Purpose**: MongoDB integration for persistent storage

**Components**:
- **`mongodb_client.py`**: Core database client
- **`config.py`**: Configuration management
- **`example_usage.py`**: Usage examples
- **`test_mongodb.py`**: Testing utilities

**Features**:
- Chat message storage
- Session management
- User history tracking
- Search functionality
- Analytics and statistics

## 📖 Usage

### University Guidance

**Example Queries**:
- "I need university recommendations for computer science"
- "What are the admission requirements for engineering programs?"
- "Show me universities in Karachi with fee under 200,000"
- "Calculate my merit for medical colleges"

**Input Requirements**:
- Academic scores (Matric & Intermediate)
- Degree preferences
- Location preferences
- Budget constraints

**Output**:
- Ranked university list
- Admission requirements
- Fee structures
- Merit calculations
- Application deadlines

### Career Guidance

**Example Queries**:
- "I need career advice based on my skills"
- "What careers match my interests in technology?"
- "Recommend careers for someone with strong math skills"

**Input Requirements**:
- Math and Biology scores (0-100)
- Interest in Technology/Arts
- Work preferences (team work, logical thinking, speaking)
- Personal preferences (location, salary, work environment)

**Output**:
- Top career recommendations
- Confidence scores
- Salary ranges
- Required skills
- Job outlook
- Top companies

### Chat History Management

**Features**:
- **Auto-load**: Previous sessions load automatically on refresh
- **Manual Load**: "📚 Load All Chat History" button
- **Save Sessions**: "💾 Save Session" button
- **Search**: Search through past conversations
- **Analytics**: View usage statistics

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `MONGODB_DATABASE` | Database name | `guidance_assistant` |
| `MONGODB_COLLECTION` | Collection name | `chat_history` |
| `OPENAI_API_KEY` | OpenAI API key for AI responses | None |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID | None |
| `GOOGLE_API_KEY` | Google API key for university search | None |
| `MONGODB_CONNECT_TIMEOUT_MS` | Connection timeout | `5000` |
| `CREATE_INDEXES` | Auto-create indexes | `true` |

### Model Configuration

**Career Predictor Model**:
- **Location**: `career_predictor_model.pkl`
- **Algorithm**: **Random Forest Classifier** (scikit-learn)
- **Framework**: **scikit-learn** with optimized hyperparameters
- **Features**: Math score, Biology score, interests, work preferences
- **Training data**: 1000+ career profiles
- **Model Parameters**:
  - `n_estimators=100`: Ensemble of 100 decision trees
  - `max_depth=10`: Prevents overfitting
  - `class_weight='balanced'`: Handles class imbalance
  - `random_state=42`: Reproducible training

**University Search Integration**:
- **Search API**: **Google Custom Search Engine** (SerpAPI alternative)
- **Implementation**: `GoogleSearchAPIWrapper` from langchain
- **Configuration**: Custom Search Engine ID and API key
- **Features**: Real-time university data retrieval and structured parsing

**University Database**:
- Location: `project/advisor_agent/universitiesstates.py`
- Universities: 100+ institutions
- Data: Admission requirements, fees, locations


## 📊 Project Structure

```
UniversityAdmissionAdvisor-Agent/
├── README.md                           # This file
├── career_predictor_model.pkl          # ML model for career predictions
├── career_mock_data_1000.csv           # Training data for career model
├── google_result.html                  # External data source
├── graph.db                           # LangGraph database
├── career_graph.db                    # Career agent database
└── backend/
    ├── supervisor_main.py             # Main application
    ├── supervisor_agent.py            # Supervisor agent logic
    ├── test_chat_retrieval.py         # Chat retrieval tests
    ├── README.md                      # Backend documentation
    ├── supervisor_graph.db            # Supervisor database
    ├── advisor_agent/                 # University guidance
    │   ├── main.py
    │   ├── UnisRecomender.py
    │   ├── UnisRanker.py
    │   ├── approval.py
    │   ├── graphsetup.py
    │   ├── universitiesstates.py
    │   ├── recommendfinalized.py
    │   └── __init__.py
    ├── career_agent/                  # Career guidance
    │   ├── main.py
    │   ├── career_predictor.py
    │   ├── career_analyzer.py
    │   ├── career_states.py
    │   ├── career_graph.py
    │   ├── train_model.py
    │   ├── career_graph.db
    │   ├── requirements.txt
    │   ├── README.md
    │   └── __init__.py
    └── database/                      # MongoDB integration
        ├── mongodb_client.py
        ├── config.py
        ├── requirements.txt
        ├── README.md
        └── __init__.py
```


**Test thoroughly**:
   ```bash
   # Test university agent
   cd project/advisor_agent
   streamlit run main.py
   
   # Test career agent
   cd project/career_agent
   streamlit run main.py
   
   # Test supervisor-agent
   cd project
   streamlit run supervisor_main.py
   ```


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review component-specific README files
2. **Search Issues**: Look for similar problems in the issue tracker
3. **Create Issue**: Open a new issue with detailed information
4. **Contact Team**: Reach out to the development team

### Issue Reporting

When reporting issues, please include:
- **Environment**: OS, Python version, dependencies
- **Steps to Reproduce**: Detailed steps to recreate the issue
- **Expected vs Actual**: What you expected vs what happened
- **Logs**: Relevant error messages and logs
- **Screenshots**: Visual evidence if applicable


**🎓💼 University Admission & Career Guidance Assistant** - Empowering students with intelligent guidance for their educational and career journey. 
