import streamlit as st
import sys
import os
from pathlib import Path
import uuid

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from career_agent.career_graph import create_career_graph
from career_agent.career_states import CareerState, CareerRecommendation
from langgraph.types import Command

# --- Page Configuration ---
st.set_page_config(
    page_title="Career Advisor Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Graph Initialization ---
@st.cache_resource
def get_career_graph():
    """Get the career recommendation graph."""
    try:
        return create_career_graph()
    except Exception as e:
        st.error(f"Error initializing career graph: {e}")
        return None

graph = get_career_graph()

# --- Session State Management ---
if "career_thread_id" not in st.session_state:
    st.session_state.career_thread_id = str(uuid.uuid4())[:8]
if "career_state" not in st.session_state:
    st.session_state.career_state = None
if "career_config" not in st.session_state:
    st.session_state.career_config = None

# --- UI Header ---
st.title("💼 Career Advisor Agent")
st.markdown("Get personalized career recommendations based on your skills, interests, and preferences.")
st.divider()

# --- Sidebar for additional information ---
with st.sidebar:
    st.header("ℹ️ About This Tool")
    st.markdown("""
    This career advisor uses machine learning to analyze your:
    - **Academic Performance** (Math & Biology scores)
    - **Interests** (Technology vs Arts)
    - **Work Preferences** (Team work, logical thinking, public speaking)
    
    The system then recommends careers that best match your profile.
    """)
    
    st.header("📊 Supported Careers")
    careers = ["IT", "Engineering", "Medicine", "Business", "Design", "Social Sciences", "Education"]
    for career in careers:
        st.markdown(f"• {career}")

# --- Main Two-Column Layout ---
left_col, right_col = st.columns([2, 1], gap="large")

# --- Left Column: Input Form ---
with left_col:
    st.header("📝 Your Profile")
    
    with st.form("career_input_form"):
        st.subheader("Academic Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            math_score = st.slider("Mathematics Score", 0, 100, 70, help="Your mathematics performance (0-100)")
        
        with col2:
            bio_score = st.slider("Biology Score", 0, 100, 70, help="Your biology performance (0-100)")
        
        st.subheader("Interests")
        col1, col2 = st.columns(2)
        
        with col1:
            interest_tech = st.checkbox("Interested in Technology", value=True, help="Do you enjoy working with computers and technology?")
        
        with col2:
            interest_art = st.checkbox("Interested in Arts/Creativity", help="Do you enjoy creative and artistic activities?")
        
        st.subheader("Work Preferences")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            group_work = st.checkbox("Enjoy Group Work", value=True, help="Do you prefer working in teams?")
        
        with col2:
            logical_thinking = st.checkbox("Logical Thinking", value=True, help="Do you enjoy solving logical problems?")
        
        with col3:
            likes_speaking = st.checkbox("Public Speaking", help="Do you enjoy presenting or public speaking?")
        
        # Note: The career prediction model uses only the 7 core features above
        # Additional preferences are not currently supported by the model
        
        submitted = st.form_submit_button("🚀 Get Career Recommendations", type="primary")

# --- Right Column: Results Display ---
with right_col:
    st.header("📊 Recommendations")
    
    if submitted and graph:
        # Create initial state
        initial_state = CareerState(
            math_score=math_score,
            bio_score=bio_score,
            interest_tech=interest_tech,
            interest_art=interest_art,
            group_work=group_work,
            logical_thinking=logical_thinking,
            likes_speaking=likes_speaking,
            career_predictions=[],
            career_recommendations=[],
            final_recommendation=None,
            confidence_threshold=0.7,
            user_approval=None,
            current_step="",
            processing_complete=False
        )
        
        with st.spinner("🤖 Analyzing your profile and generating recommendations..."):
            try:
                config = {"configurable": {"thread_id": st.session_state.career_thread_id}}
                result = graph.invoke(initial_state, config=config)
                
                # Debug: Print the result type and content
                st.write(f"Result type: {type(result)}")
                st.write(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                st.session_state.career_state = result
                st.session_state.career_config = config
                st.rerun()
            except Exception as e:
                st.error(f"Error processing your request: {e}")
    
    # Display results
    if st.session_state.career_state:
        state = st.session_state.career_state
        
        # Handle both CareerState object and dictionary
        if hasattr(state, 'career_recommendations'):
            # It's a CareerState object
            career_recommendations = state["career_recommendations"]
            final_recommendation = state["final_recommendation"]
            current_step = state["current_step"]
        else:
            # It's a dictionary
            career_recommendations = state.get('career_recommendations', [])
            final_recommendation = state.get('final_recommendation')
            current_step = state.get('current_step', '')
        
        if career_recommendations:
            st.success("✅ Career recommendations generated!")
            
            # Display top recommendation
            if final_recommendation:
                top_career = final_recommendation
                
                with st.container(border=True):
                    st.markdown(f"### 🎯 Top Recommendation: {top_career['career_name']}")
                    st.metric("Confidence Score", f"{top_career['confidence_score']:.1%}")
                    
                    st.markdown("**Description:**")
                    st.info(top_career['description'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Salary Range:**")
                        st.success(top_career['salary_range'])
                        
                        st.markdown("**Job Outlook:**")
                        st.info(top_career['job_outlook'])
                    
                    with col2:
                        st.markdown("**Education Required:**")
                        st.warning(top_career['education_requirements'])
                    
                    st.markdown("**Required Skills:**")
                    skills_text = ", ".join(top_career['required_skills'])
                    st.markdown(f"`{skills_text}`")
                    
                    st.markdown("**Top Companies:**")
                    companies_text = ", ".join(top_career['companies'][:3])
                    st.markdown(f"`{companies_text}`")
            
            # Display all recommendations
            st.markdown("### 📋 All Recommendations")
            for i, career in enumerate(career_recommendations, 1):
                with st.expander(f"{i}. {career['career_name']} ({career['confidence_score']:.1%})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Description:** {career['description']}")
                        st.markdown(f"**Salary:** {career['salary_range']}")
                        st.markdown(f"**Outlook:** {career['job_outlook']}")
                    
                    with col2:
                        st.markdown(f"**Education:** {career['education_requirements']}")
                        st.markdown("**Skills:** " + ", ".join(career['required_skills'][:3]))
                        st.markdown("**Companies:** " + ", ".join(career['companies'][:2]))
        
        elif current_step == "validation_error":
            st.error("❌ Please check your inputs and try again.")
        
        else:
            st.info("👋 Enter your details and click 'Get Career Recommendations' to get started.")
    
    else:
        st.info("👋 Enter your details and click 'Get Career Recommendations' to get started.")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>Tip:</strong> Be honest with your preferences for better recommendations!</p>
    <p>🔍 This tool uses machine learning to analyze patterns and suggest suitable careers.</p>
</div>
""", unsafe_allow_html=True) 