import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

sys.path.append(str(Path(__file__).parent))

from agents.interviewer import InterviewAgent
from agents.evaluator import InterviewEvaluator
from utils.conversation_manager import ConversationManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Interview Practice",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "conversation_manager" not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
    st.session_state.interviewer = None
    st.session_state.evaluator = InterviewEvaluator()
    st.session_state.interview_started = False
    st.session_state.interview_ended = False
    st.session_state.feedback = None
    st.session_state.error_message = None

st.title("AI Interview Practice Partner")
st.caption("Practice interviews with adaptive AI feedback")

with st.sidebar:
    st.header("Interview Configuration")
    
    role = st.selectbox(
        "Select Role",
        ["Software Engineer", "Sales Representative", "Retail Associate"],
        help="Choose the job role you want to practice for"
    )
    
    experience_level = st.selectbox(
        "Experience Level",
        ["Entry", "Mid", "Senior"],
        help="Select your experience level"
    )
    
    st.divider()
    
    if not st.session_state.interview_started:
        if st.button("Start New Interview", type="primary", use_container_width=True):
            try:
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    st.session_state.error_message = "Google API key not found. Please check your .env file."
                else:
                    st.session_state.interviewer = InterviewAgent(role, experience_level)
                    st.session_state.conversation_manager.initialize_conversation(role, experience_level)
                    
                    opening = st.session_state.interviewer.start_interview()
                    st.session_state.conversation_manager.add_message("assistant", opening)
                    
                    st.session_state.interview_started = True
                    st.session_state.interview_ended = False
                    st.session_state.feedback = None
                    st.session_state.error_message = None
                    st.rerun()
            except Exception as e:
                st.session_state.error_message = f"Error starting interview: {str(e)}"
    
    if st.session_state.interview_started and not st.session_state.interview_ended:
        st.info(f"**Current Interview**\n\nRole: {role}\n\nLevel: {experience_level}")
        
        total_questions = st.session_state.interviewer.get_total_questions()
        st.metric("Questions Asked", total_questions)
        
        if st.session_state.interviewer.response_quality_scores:
            avg_score = sum(s["score"] for s in st.session_state.interviewer.response_quality_scores) / len(st.session_state.interviewer.response_quality_scores)
            st.metric("Avg Response Quality", f"{avg_score:.1f}/10")
        
        st.divider()
        
        if st.button("End Interview & Get Feedback", use_container_width=True):
            st.session_state.interview_ended = True
            st.rerun()
        
        if st.button("Cancel Interview", use_container_width=True):
            st.session_state.conversation_manager = ConversationManager()
            st.session_state.interviewer = None
            st.session_state.interview_started = False
            st.session_state.interview_ended = False
            st.session_state.feedback = None
            st.rerun()
    
    st.divider()
    st.markdown("### How to Use")
    st.markdown("""
    1. Select role and experience level
    2. Click 'Start New Interview'
    3. Type your answers in the chat
    4. Get detailed feedback at the end
    """)
    
    if st.session_state.interview_started:
        st.divider()
        engagement = st.session_state.interviewer.persona_detector.get_engagement_score()
        st.metric("Engagement Score", f"{engagement:.0%}")

if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.stop()

if not st.session_state.interview_started:
    st.info("Configure your interview settings in the sidebar and click 'Start New Interview' to begin.")
    
    with st.expander("About This Tool"):
        st.markdown("""
        This AI-powered interview practice tool helps you prepare for real interviews by:
        
        - **Adaptive Questioning**: Adjusts to your response style
        - **Intelligent Follow-ups**: Probes deeper when needed
        - **Persona Detection**: Recognizes if you're confused, efficient, or chatty
        - **Comprehensive Feedback**: Detailed evaluation with actionable insights
        
        The tool covers three major roles and adapts to different experience levels.
        """)
    
elif st.session_state.interview_ended:
    st.success("Interview completed! Generating your comprehensive feedback...")
    
    if st.session_state.feedback is None:
        with st.spinner("Analyzing your interview performance..."):
            try:
                conversation_history = st.session_state.interviewer.conversation_history
                
                feedback = st.session_state.evaluator.generate_final_feedback(
                    conversation_history,
                    role,
                    experience_level
                )
                st.session_state.feedback = feedback
                st.session_state.conversation_manager.save_conversation()
            except Exception as e:
                st.error(f"Error generating feedback: {str(e)}")
                st.session_state.feedback = "Unable to generate feedback. Please try again."
    
    st.markdown(st.session_state.feedback)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("View Full Transcript"):
            transcript = st.session_state.conversation_manager.get_formatted_transcript()
            st.text_area("Transcript", transcript, height=400, label_visibility="collapsed")
    
    with col2:
        with st.expander("Interview Statistics"):
            stats = st.session_state.interviewer.persona_detector
            st.metric("Total Responses", len(stats.response_history))
            st.metric("Average Response Length", f"{sum(stats.response_lengths) // len(stats.response_lengths) if stats.response_lengths else 0} words")
            st.metric("Engagement Score", f"{stats.get_engagement_score():.0%}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Another Interview", type="primary", use_container_width=True):
            st.session_state.conversation_manager = ConversationManager()
            st.session_state.interviewer = None
            st.session_state.interview_started = False
            st.session_state.interview_ended = False
            st.session_state.feedback = None
            st.rerun()
    
    with col2:
        if st.button("Download Transcript", use_container_width=True):
            transcript = st.session_state.conversation_manager.get_formatted_transcript()
            st.download_button(
                label="Download as Text",
                data=transcript,
                file_name=f"interview_{st.session_state.conversation_manager.session_id}.txt",
                mime="text/plain",
                use_container_width=True
            )

else:
    conversation_history = st.session_state.interviewer.conversation_history
    
    for msg in conversation_history:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])
    
    user_input = st.chat_input("Type your answer here...")
    
    if user_input:
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        st.session_state.conversation_manager.add_message("user", user_input)
        
        with st.spinner("Thinking..."):
            try:
                next_question, error_type = st.session_state.interviewer.generate_next_question(user_input)
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(next_question)
                
                st.session_state.conversation_manager.add_message("assistant", next_question)
                
                if error_type == "api_error":
                    st.warning("Note: Using fallback question due to API issues. Your response was recorded.")
                elif error_type == "validation_error":
                    st.info("Please review the feedback above and provide a valid response.")
                
                st.rerun()
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.info("Please try again or end the interview for feedback.")
                logger.exception("Unexpected error in app")