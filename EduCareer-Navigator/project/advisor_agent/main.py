import streamlit as st
import time
from langgraph.types import Command
from pathlib import Path
from advisor_agent.graphsetup import create_advisor_graph
import uuid
from advisor_agent.universitiesstates import systemState

# --- Page Configuration ---
st.set_page_config(
    page_title="University Admission Advisor Agent",
    page_icon="🎓",
    layout="wide",
)

# --- Graph Initialization ---
graph = create_advisor_graph()

# --- Session State Management ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]
if "state" not in st.session_state:
    st.session_state.state = None
if "interrupted" not in st.session_state:
    st.session_state.interrupted = False
if "config" not in st.session_state:
    st.session_state.config = None
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()

# Session timeout check (30 minutes)
current_time = time.time()
session_duration = current_time - st.session_state.session_start_time
if session_duration > 1800:
    st.warning("⏰ Session timeout detected. Starting fresh...")
    st.session_state.state = None
    st.session_state.interrupted = False
    st.session_state.config = None
    st.session_state.session_start_time = current_time
    st.rerun()

# --- UI Header ---
st.title("🎓 University Admission Advisor")
st.markdown("Get tailored university recommendations based on your academic profile and preferences.")
st.divider()

# --- Main Layout ---
left_col, right_col = st.columns(2, gap="large")

# --- Left Column: Input Form ---
with left_col:
    st.header("📄 Your Details")
    with st.form("input_form"):
        st.subheader("Academic Profile")
        matric_marks = st.number_input("Matric Marks (out of 1100)", min_value=0, max_value=1100)
        inter_marks = st.number_input("Intermediate Marks (out of 1100)", min_value=0, max_value=1100)

        st.subheader("Preferences")
        degree_preference = st.text_input("Degree Preference", placeholder="e.g., Computer Science, BBA")
        fee_budget = st.text_input("Fee Budget per Semester", placeholder="e.g., 150,000 PKR")

        st.subheader("Location")
        location = st.text_input("Country", placeholder="e.g., Pakistan")
        city = st.text_input("City (Optional)", placeholder="e.g., Lahore")

        submitted = st.form_submit_button("🚀 Find Universities")

# --- Right Column: Recommendations ---
with right_col:
    st.header("📊 Recommendations")

    if st.session_state.state is not None:
        if st.button("🔄 Start Over", type="secondary"):
            st.session_state.state = None
            st.session_state.interrupted = False
            st.session_state.config = None
            st.rerun()

    def university_card(uni_name, ranked=False, rank_number=0):
        with st.container(border=True):
            if ranked:
                st.markdown(f"### {rank_number}. {uni_name.name}")
            else:
                st.markdown(f"### {uni_name.name}")

            st.markdown(f'Fee per semester: {uni_name.fee_per_semester}')
            st.markdown(f'Marks required in inter: {uni_name.min_inter_marks}')
            st.markdown(f'Merit formula: {uni_name.merit_formula}')

            st.link_button("🔗 Admission Portal", f"{uni_name.admission_portal}", type="primary")

    if submitted:
        st.session_state.interrupted = False
        st.session_state.state = None
        st.session_state.config = None

        initial_state = systemState(
            matric_marks=matric_marks,
            inter_marks=inter_marks,
            degree_preference=degree_preference,
            location=location,
            rank_unis="no",
            city=city,
            fee_budget=fee_budget,
            universities=[],
            ranked_universities=[]
        )

        try:
            with st.spinner("🤖 Processing your inputs and finding universities..."):
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = graph.invoke(initial_state, config=config)
                st.session_state.state = result
                st.session_state.config = config
                st.session_state.interrupted = "__interrupt__" in result
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error processing your request: {str(e)}")
            st.session_state.state = None
            st.session_state.config = None

    if st.session_state.interrupted:
        try:
            interrupt = st.session_state.state["__interrupt__"][0]

            st.progress(0.5, text="⏳ Waiting for your decision...")
            st.warning("✋ **Human Approval Required**")
            st.markdown(f"**Agent asks:** {interrupt.value}")

            with st.container(border=True):
                st.markdown("### 📈 Current Progress")
                st.markdown("✅ **Step 1:** University search completed")
                st.markdown("⏳ **Step 2:** Awaiting your decision")
                st.markdown("⏸️ **Step 3:** Will proceed based on your choice")

            universities = st.session_state.state.get("universities")
            if universities:
                st.markdown("#### 📋 Found Universities (Unranked):")
                st.info(f"Found {len(universities)} universities matching your criteria")

                with st.expander(f"👀 Preview Universities ({len(universities)} found)"):
                    for i, uni in enumerate(universities[:3], 1):
                        university_card(uni)
                    if len(universities) > 3:
                        st.info(f"... and {len(universities) - 3} more universities")

            # Main interrupt choice form
            with st.form("resume_form"):
                st.markdown("### 🤔 What would you like to do?")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Option 1: Rank Universities**")
                    st.markdown("✅ Get personalized ranking")
                with col2:
                    st.markdown("**Option 2: Skip Ranking**")
                    st.markdown("📝 Browse all matching universities")

                resume_response = st.radio(
                    "Your choice:",
                    ["yes", "no"],
                    key="resume_response",
                    horizontal=True,
                    format_func=lambda x: "✅ Yes, rank them!" if x == "yes" else "❌ No, show all"
                )

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    submitted_continue = st.form_submit_button("🚀 Continue", use_container_width=True)

            if submitted_continue:
                try:
                    with st.spinner("▶️ Processing your choice..."):
                        resumed = graph.invoke(
                            Command(resume=resume_response),
                            config=st.session_state.config
                        )
                        st.session_state.state = resumed
                        st.session_state.interrupted = "__interrupt__" in resumed
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error resuming process: {str(e)}")
                    st.session_state.interrupted = False
                    st.session_state.state = None

            # Troubleshooting options OUTSIDE form
            with st.expander("🛠️ Troubleshooting"):
                st.markdown("If you're experiencing issues:")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Retry Process", key="retry_process"):
                        st.session_state.interrupted = False
                        st.session_state.state = None
                        st.rerun()
                with col2:
                    if st.button("🏠 Start Fresh", key="start_fresh"):
                        st.session_state.interrupted = False
                        st.session_state.state = None
                        st.session_state.config = None
                        st.rerun()

        except Exception as e:
            st.error(f"❌ Error handling interrupt: {str(e)}")
            st.session_state.interrupted = False
            st.session_state.state = None

    elif st.session_state.state:
        try:
            final = st.session_state.state
            rank_unis = final.get("rank_unis")

            if rank_unis == "yes":
                st.balloons()
                st.success("🎉 Ranked University Recommendations")
                ranked_unis = final.get("ranked_universities", [])
                if ranked_unis:
                    for idx, uni in enumerate(ranked_unis, start=1):
                        university_card(uni, ranked=True, rank_number=idx)
                else:
                    st.warning("⚠️ Could not rank the universities.")

            elif rank_unis == "no":
                st.info("📝 All Matching Universities")
                unis = final.get("universities", [])
                for uni in unis:
                    university_card(uni)

            with st.expander("🔧 Debug Information"):
                st.json({k: v for k, v in final.items() if k != "__interrupt__"})

        except Exception as e:
            st.error(f"❌ Error displaying results: {str(e)}")
            st.session_state.state = None
            st.session_state.interrupted = False

    else:
        st.info("👋 Enter your details on the left and click 'Find Universities' to get started.")
