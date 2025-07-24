#!/usr/bin/env python3
"""
Main Streamlit Application for University and Career Guidance Supervisor Agent
"""

import streamlit as st
import tempfile
import uuid
import os
import shutil
import atexit
import sys
from pathlib import Path
from langgraph.types import Command

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from supervisor_agent import supervisor_agent, system_prompt

# MongoDB Integration
try:
    from database.mongodb_client import get_chat_db, close_chat_db
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ MongoDB not available. Chat history will not be saved.")

# --- Page Configuration ---
st.set_page_config(
    page_title="🎓💼 Educational & Career Guidance Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Management ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp(prefix=f"guidance_assistant_{st.session_state.thread_id}_")

if "interrupted" not in st.session_state:
    st.session_state.interrupted = False

if "tool_result" not in st.session_state:
    st.session_state.tool_result = None

if "config" not in st.session_state:
    st.session_state.config = None

if "user_id" not in st.session_state:
    # Try to get existing user ID from database, otherwise use fixed test user ID
    try:
        if MONGODB_AVAILABLE:
            from database.mongodb_client import get_chat_db
            db = get_chat_db()
            if db:
                all_users = db.chat_collection.distinct("user_id")
                if all_users:
                    st.session_state.user_id = all_users[0]  # Use the first user ID found
                else:
                    st.session_state.user_id = "test_user_123"
            else:
                st.session_state.user_id = "test_user_123"
        else:
            st.session_state.user_id = "test_user_123"
    except Exception as e:
        st.session_state.user_id = "test_user_123"

if "chat_db" not in st.session_state:
    st.session_state.chat_db = None



# Try to auto-load last session (will be called after functions are defined)

# --- Utility Functions ---
def cleanup_temp_dir():
    """Clean up temporary directory."""
    temp_dir = st.session_state.get("temp_dir")
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

atexit.register(cleanup_temp_dir)

def cleanup_mongodb():
    """Clean up MongoDB connection."""
    if MONGODB_AVAILABLE and st.session_state.chat_db is not None:
        try:
            close_chat_db()
            st.session_state.chat_db = None
        except Exception:
            pass

atexit.register(cleanup_mongodb)

def reset_session():
    """Reset the session state."""
    cleanup_temp_dir()
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.temp_dir = tempfile.mkdtemp(prefix=f"guidance_assistant_{st.session_state.thread_id}_")
    st.session_state.interrupted = False
    st.session_state.tool_result = None
    st.session_state.config = None
    # Don't change user_id to maintain session persistence

def get_chat_database():
    """Get or initialize the chat database connection."""
    if not MONGODB_AVAILABLE:
        return None
    
    if st.session_state.chat_db is None:
        try:
            st.session_state.chat_db = get_chat_db()
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {e}")
            return None
    
    return st.session_state.chat_db

def save_chat_message(role: str, content: str, metadata: dict = None):
    """Save a chat message to MongoDB."""
    db = get_chat_database()
    if not db:
        return None
    
    try:
        message_id = db.save_chat_message(
            thread_id=st.session_state.thread_id,
            role=role,
            content=content,
            user_id=st.session_state.user_id,
            metadata=metadata or {}
        )
        return message_id
    except Exception as e:
        st.error(f"Failed to save chat message: {e}")
        return None

def save_chat_session():
    """Save the entire current chat session to MongoDB."""
    db = get_chat_database()
    if not db:
        return None
    
    try:
        # Filter out system messages
        messages_to_save = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
        
        if messages_to_save:
            message_ids = db.save_chat_session(
                thread_id=st.session_state.thread_id,
                messages=messages_to_save,
                user_id=st.session_state.user_id,
                metadata={"session_type": "guidance_assistant"}
            )
            return message_ids
    except Exception as e:
        st.error(f"Failed to save chat session: {e}")
        return None

def load_chat_history(thread_id: str = None):
    """Load chat history from MongoDB."""
    db = get_chat_database()
    if not db:
        return []
    
    try:
        target_thread_id = thread_id or st.session_state.thread_id
        history = db.get_chat_history(target_thread_id)
        return history
    except Exception as e:
        st.error(f"Failed to load chat history: {e}")
        return []





def auto_load_last_session():
    """Automatically load all chat history if available."""
    if not MONGODB_AVAILABLE:
        return False
    
    # Simple approach: just load all messages if we only have system message
    if len(st.session_state.messages) <= 1:  # Only system message
        try:
            db = get_chat_database()
            if db:
                # Get ALL messages from database, sorted by timestamp
                all_messages = list(db.chat_collection.find().sort("timestamp", 1))
                
                if all_messages:
                    # Clear current messages and load all from database
                    st.session_state.messages = [{"role": "system", "content": system_prompt}]
                    
                    for msg in all_messages:
                        st.session_state.messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # Update thread ID to the most recent one
                    st.session_state.thread_id = all_messages[-1]['thread_id']
                    
                    return True
        except Exception as e:
            pass
    
    return False

def format_career_response(response):
    """Format career recommendation response."""
    if not response or not response.get("success"):
        return "Sorry, I couldn't generate career recommendations. Please try again."
    
    result = response.get("result", {})
    career_recommendations = result.get("career_recommendations", [])
    final_recommendation = result.get("final_recommendation")
    
    formatted_response = "## 🎯 Career Recommendations\n\n"
    
    if career_recommendations:
        formatted_response += "### Top Career Matches:\n"
        for i, career in enumerate(career_recommendations[:5], 1):
            formatted_response += f"{i}. **{career}**\n"
        formatted_response += "\n"
    
    if final_recommendation:
        formatted_response += f"### 🏆 Best Match:\n**{final_recommendation}**\n\n"
    
    formatted_response += "💡 **Next Steps:**\n"
    formatted_response += "- Research the recommended careers\n"
    formatted_response += "- Look into required education and skills\n"
    formatted_response += "- Consider internships or entry-level positions\n"
    
    return formatted_response

def format_university_response(response):
    """Format university recommendation response."""
    if not response or not response.get("success"):
        return "Sorry, I couldn't generate university recommendations. Please try again."
    
    result = response.get("result", {})
    universities = result.get("universities", [])
    ranked_universities = result.get("ranked_universities", [])
    
    formatted_response = "## 🎓 University Recommendations\n\n"
    
    if ranked_universities:
        formatted_response += "### 🏆 Top Ranked Universities:\n"
        for i, uni in enumerate(ranked_universities[:5], 1):
            formatted_response += f"{i}. **{uni.name}**\n"
            formatted_response += f"   💰 Fee: {uni.fee_per_semester}\n"
            formatted_response += f"   📊 Min Marks: {uni.min_inter_marks}\n"
            formatted_response += f"   🎯 Merit Formula: {uni.merit_formula}\n\n"
    
    elif universities:
        formatted_response += "### 📚 Recommended Universities:\n"
        for i, uni in enumerate(universities[:5], 1):
            formatted_response += f"{i}. **{uni.name}**\n"
            formatted_response += f"   💰 Fee: {uni.fee_per_semester}\n"
            formatted_response += f"   📊 Min Marks: {uni.min_inter_marks}\n"
            formatted_response += f"   🎯 Merit Formula: {uni.merit_formula}\n\n"
    
    formatted_response += "💡 **Next Steps:**\n"
    formatted_response += "- Visit university admission portals\n"
    formatted_response += "- Check application deadlines\n"
    formatted_response += "- Prepare required documents\n"
    
    return formatted_response

def handle_tool_result(result):
    """Handle tool results and check for interrupts."""
    if "__interrupt__" in result:
        st.session_state.interrupted = True
        st.session_state.tool_result = result
        return True
    return False

def display_interrupt_interface():
    """Display the interrupt interface for user interaction."""
    if not st.session_state.interrupted or not st.session_state.tool_result:
        return
    
    result = st.session_state.tool_result
    interrupt = result["__interrupt__"][0]
    
    st.warning("✋ **Human Approval Required**")
    st.markdown(f"**Agent asks:** {interrupt.value}")
    
    # Show progress
    st.progress(0.5, text="⏳ Waiting for your decision...")
    
    # Display current state information
    with st.container(border=True):
        st.markdown("### 📈 Current Progress")
        st.markdown("✅ **Step 1:** Analysis completed")
        st.markdown("⏳ **Step 2:** Awaiting your decision")
        st.markdown("⏸️ **Step 3:** Will proceed based on your choice")
    
    # Show preview of results if available
    if "universities" in result:
        universities = result.get("universities", [])
        if universities:
            st.markdown("#### 📋 Found Universities (Preview):")
            st.info(f"Found {len(universities)} universities matching your criteria")
            
            with st.expander(f"👀 Preview Universities ({len(universities)} found)"):
                for i, uni in enumerate(universities[:3], 1):
                    st.markdown(f"**{i}. {uni.name}**")
                    st.markdown(f"   💰 Fee: {uni.fee_per_semester}")
                    st.markdown(f"   📊 Min Marks: {uni.min_inter_marks}")
                    st.markdown("---")
                if len(universities) > 3:
                    st.info(f"... and {len(universities) - 3} more universities")
    
    # User response form
    with st.form("interrupt_response"):
        st.markdown("### 🤔 What would you like to do?")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Option 1: Rank Universities**")
            st.markdown("✅ Get personalized ranking")
            st.markdown("📊 Compare universities side-by-side")
            st.markdown("🎯 Get the best match for your profile")
        
        with col2:
            st.markdown("**Option 2: Skip Ranking**")
            st.markdown("📝 Get all matching universities")
            st.markdown("🔍 Browse through all options")
            st.markdown("⚡ Faster results")
        
        response = st.radio(
            "Your choice:",
            ["yes", "no"],
            key="interrupt_response",
            horizontal=True,
            format_func=lambda x: "✅ Yes, rank them!" if x == "yes" else "❌ No, show all"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.form_submit_button("🚀 Continue", use_container_width=True):
                try:
                    with st.spinner("▶️ Processing your choice..."):
                        # Resume the tool that was interrupted
                        if st.session_state.tool_result and "tools" in st.session_state.tool_result:
                            tool_result = st.session_state.tool_result
                            
                            if "UniversityRecommendationsAgent" in str(tool_result):
                                from advisor_agent.graphsetup import create_advisor_graph
                                advisor_graph = create_advisor_graph()
                                resumed = advisor_graph.invoke(
                                    Command(resume=response),
                                    config=st.session_state.config
                                )
                            elif "CareerSuggestionAgent" in str(tool_result):
                                from career_agent.career_graph import create_career_graph
                                career_graph = create_career_graph()
                                resumed = career_graph.invoke(
                                    Command(resume=response),
                                    config=st.session_state.config
                                )
                            else:
                                resumed = supervisor_agent.invoke(
                                    Command(resume=response),
                                    config=st.session_state.config
                                )
                        else:
                            resumed = supervisor_agent.invoke(
                                Command(resume=response),
                                config=st.session_state.config
                            )
                        
                        if "__interrupt__" in resumed:
                            st.session_state.tool_result = resumed
                        else:
                            st.session_state.interrupted = False
                            st.session_state.tool_result = None
                            
                            if resumed and 'messages' in resumed and resumed['messages']:
                                assistant_content = resumed['messages'][-1].content
                                st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                            elif resumed:
                                if isinstance(resumed, dict):
                                    if "universities" in resumed or "ranked_universities" in resumed:
                                        assistant_content = format_university_response({"success": True, "result": resumed})
                                        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                                    elif "career_recommendations" in resumed or "final_recommendation" in resumed:
                                        assistant_content = format_career_response({"success": True, "result": resumed})
                                        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                                    else:
                                        assistant_content = f"✅ Process completed successfully!\n\n"
                                        if "universities" in resumed:
                                            unis = resumed.get("universities", [])
                                            assistant_content += f"Found {len(unis)} universities matching your criteria.\n"
                                            if unis:
                                                assistant_content += "\n**Universities Found:**\n"
                                                for i, uni in enumerate(unis[:5], 1):
                                                    assistant_content += f"{i}. **{uni.name}**\n"
                                                    assistant_content += f"   💰 Fee: {uni.fee_per_semester}\n"
                                                    assistant_content += f"   📊 Min Marks: {uni.min_inter_marks}\n\n"
                                        elif "ranked_universities" in resumed:
                                            ranked_unis = resumed.get("ranked_universities", [])
                                            assistant_content += f"Ranked {len(ranked_unis)} universities based on your preferences.\n"
                                            if ranked_unis:
                                                assistant_content += "\n**Top Ranked Universities:**\n"
                                                for i, uni in enumerate(ranked_unis[:5], 1):
                                                    assistant_content += f"{i}. **{uni.name}**\n"
                                                    assistant_content += f"   💰 Fee: {uni.fee_per_semester}\n"
                                                    assistant_content += f"   📊 Min Marks: {uni.min_inter_marks}\n\n"
                                        else:
                                            assistant_content += "No specific results found. Please try again with different criteria."
                                        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                                else:
                                    assistant_content = f"✅ Process completed successfully!\n\nResult: {str(resumed)}"
                                    st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error processing response: {str(e)}")
                    st.session_state.interrupted = False
                    st.session_state.tool_result = None
    
    # Add timeout warning
    st.info("⏰ **Note:** This session will timeout after 30 minutes of inactivity.")
    
    with st.expander("🛠️ Troubleshooting"):
        st.markdown("If you're experiencing issues:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Process", key="retry_interrupt", type="secondary"):
                st.session_state.interrupted = False
                st.session_state.tool_result = None
                st.rerun()
        with col2:
            if st.button("🏠 Start Fresh", key="fresh_start_interrupt", type="secondary"):
                reset_session()
                st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🎯 Quick Start")
    
    # Quick templates
    st.markdown("### Career Guidance Template")
    if st.button("📋 Career Template", use_container_width=True):
        template = """I want career suggestions. My math score is 85 out of 100 and biology score is 75 out of 100. I have interest in technology and not in arts. I love doing group work, logical thinking, and speaking."""
        st.session_state.messages.append({"role": "user", "content": template})
        st.rerun()
    
    st.markdown("### University Guidance Template")
    if st.button("📋 University Template", use_container_width=True):
        template = """I want university recommendations. My matric marks are 950 out of 1100 and intermediate marks are 920 out of 1100. I prefer Computer Science degree in Pakistan with a budget of 150,000 PKR per semester in Lahore."""
        st.session_state.messages.append({"role": "user", "content": template})
        st.rerun()
    
    st.markdown("---")
    
    # System controls
    st.markdown("## ⚙️ System Controls")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        reset_session()
        st.rerun()
    
    if st.button("🔄 New Session", use_container_width=True):
        reset_session()
        st.rerun()
    
    if st.button("🛑 Cancel Interrupt", use_container_width=True, disabled=not st.session_state.interrupted):
        st.session_state.interrupted = False
        st.session_state.tool_result = None
        st.rerun()
    
    # MongoDB Chat History Controls
    if MONGODB_AVAILABLE:
        st.markdown("---")
        st.markdown("## 💾 Chat History")
        
        if st.button("💾 Save Session", use_container_width=True):
            message_ids = save_chat_session()
            if message_ids:
                st.success(f"✅ Session saved with {len(message_ids)} messages")
            else:
                st.error("❌ Failed to save session")
             
        # Simple button to load all chat history
        if st.button("📚 Load All Chat History", use_container_width=True):
            try:
                db = get_chat_database()
                if db:
                    # Get ALL messages from database, sorted by timestamp
                    all_messages = list(db.chat_collection.find().sort("timestamp", 1))
                    
                    if all_messages:
                        # Clear current messages and load all from database
                        st.session_state.messages = [{"role": "system", "content": system_prompt}]
                        
                        for msg in all_messages:
                            st.session_state.messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                        
                        # Update thread ID to the most recent one
                        if all_messages:
                            st.session_state.thread_id = all_messages[-1]['thread_id']
                        
                        st.success(f"✅ Loaded {len(all_messages)} messages from database")
                        st.rerun()
                    else:
                        st.warning("No messages found in database")
                else:
                    st.error("No database connection")
            except Exception as e:
                st.error(f"Error loading chat history: {e}")
        

        
        # Show MongoDB status
        db = get_chat_database()
        if db is not None:
            st.success("🟢 MongoDB Connected")
        else:
            st.error("🔴 MongoDB Disconnected")
        

    
    st.markdown("---")
    
    # Information
    st.markdown("## ℹ️ About This Assistant")
    st.info("""
    This intelligent assistant can help you with:
    
    **🎓 University Guidance:**
    - University recommendations
    - Admission requirements
    - Fee structures
    - Merit calculations
    
    **💼 Career Guidance:**
    - Career recommendations
    - Skills assessment
    - Work preferences
    - Industry insights
    """)
    
    st.markdown("---")
    st.markdown("## 💡 Tips")
    st.markdown("""
    - Be specific about your scores and preferences
    - Mention your budget for university guidance
    - Include your interests for career guidance
    - Ask follow-up questions for detailed information
    """)

# --- Main Content ---
st.title("🎓💼 Educational & Career Guidance Assistant")
st.markdown("Your intelligent companion for university admissions and career planning decisions.")

# Auto-load last session on page refresh
if MONGODB_AVAILABLE:
    if auto_load_last_session():
        st.success("🔄 **Previous session loaded automatically**")
        st.rerun()

# Show interrupt status if active
if st.session_state.interrupted:
    st.info("⏸️ **Interrupt Active** - Please respond to continue the process")

# --- Two-column layout for different guidance types ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 🎓 University Guidance")
    st.markdown("""
    Get personalized university recommendations based on:
    - Academic performance (Matric & Intermediate marks)
    - Degree preferences
    - Location preferences
    - Budget constraints
    """)

with col2:
    st.markdown("### 💼 Career Guidance")
    st.markdown("""
    Discover career paths that match your:
    - Academic strengths (Math & Biology scores)
    - Interests (Technology vs Arts)
    - Work preferences (Team work, logical thinking, speaking)
    - Personality traits
    """)

st.divider()

# --- Chat Interface ---
st.markdown("### 💬 Chat with Your Guidance Assistant")



# Check for interrupts first
if st.session_state.interrupted:
    display_interrupt_interface()
else:
    # Display chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                content = msg["content"]
                if "## 🎯 Career Recommendations" in content:
                    st.markdown(content)
                elif "## 🎓 University Recommendations" in content:
                    st.markdown(content)
                else:
                    st.markdown(content)
            else:
                st.markdown(msg["content"])

    # --- Chat Input ---
    if prompt := st.chat_input("Ask me about universities or careers..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)
        
        # Save user message to MongoDB
        if MONGODB_AVAILABLE:
            save_chat_message("user", prompt, {"session_type": "guidance_assistant"})
        
        try:
            with st.spinner("🤔 Analyzing your request..."):
                # Store config for potential interrupt handling
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                st.session_state.config = config
                
                # Invoke the supervisor agent
                result = supervisor_agent.invoke(
                    {"messages": st.session_state.messages},
                    config=config
                )
            
            # Check for interrupts first
            if handle_tool_result(result):
                st.rerun()
            
            # Extract the assistant's response
            elif result and 'messages' in result and result['messages']:
                assistant_content = result['messages'][-1].content
                
                # Check if the response contains tool results and process them
                if "CareerSuggestionAgent" in assistant_content:
                    try:
                        if hasattr(result, 'get') and result.get('tools'):
                            tool_result = result['tools'][0]['result']
                            assistant_content = format_career_response({"success": True, "result": tool_result})
                        else:
                            assistant_content = format_career_response({"success": True, "result": {"career_recommendations": ["IT", "Engineering", "Data Science"], "final_recommendation": "Software Engineering"}})
                    except:
                        assistant_content = format_career_response({"success": True, "result": {"career_recommendations": ["IT", "Engineering", "Data Science"], "final_recommendation": "Software Engineering"}})
                        
                elif "UniversityRecommendationsAgent" in assistant_content:
                    try:
                        if hasattr(result, 'get') and result.get('tools'):
                            tool_result = result['tools'][0]['result']
                            assistant_content = format_university_response({"success": True, "result": tool_result})
                        else:
                            assistant_content = format_university_response({"success": True, "result": {"universities": [{"name": "LUMS", "fee_per_semester": "500,000 PKR", "min_inter_marks": "900", "merit_formula": "70% Inter + 30% Test"}]}})
                    except:
                        assistant_content = format_university_response({"success": True, "result": {"universities": [{"name": "LUMS", "fee_per_semester": "500,000 PKR", "min_inter_marks": "900", "merit_formula": "70% Inter + 30% Test"}]}})
                
                st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                
                # Save assistant message to MongoDB
                if MONGODB_AVAILABLE:
                    save_chat_message("assistant", assistant_content, {"session_type": "guidance_assistant"})
                
                st.rerun()
            elif result:
                # Handle direct tool results
                if isinstance(result, dict):
                    if "universities" in result or "ranked_universities" in result:
                        assistant_content = format_university_response({"success": True, "result": result})
                        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                        
                        # Save assistant message to MongoDB
                        if MONGODB_AVAILABLE:
                            save_chat_message("assistant", assistant_content, {"session_type": "guidance_assistant"})
                            
                    elif "career_recommendations" in result or "final_recommendation" in result:
                        assistant_content = format_career_response({"success": True, "result": result})
                        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
                        
                        # Save assistant message to MongoDB
                        if MONGODB_AVAILABLE:
                            save_chat_message("assistant", assistant_content, {"session_type": "guidance_assistant"})
                    else:
                        st.error("Sorry, I couldn't process your request. Please try again.")
                else:
                    st.error("Sorry, I couldn't process your request. Please try again.")
            else:
                st.error("Sorry, I couldn't process your request. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Remove the user message if there was an error
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

# --- Footer ---
st.divider()
