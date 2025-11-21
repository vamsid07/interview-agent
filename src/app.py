import streamlit as st
from dotenv import load_dotenv
from agents.interviewer import InterviewAgent
from agents.evaluator import InterviewEvaluator
from utils.conversation_manager import ConversationManager

load_dotenv()

st.set_page_config(page_title="AI Interview Practice", layout="wide")

if "conversation_manager" not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
    st.session_state.interviewer = None
    st.session_state.evaluator = InterviewEvaluator()
    st.session_state.interview_started = False
    st.session_state.interview_ended = False
    st.session_state.feedback = None

st.title("AI Interview Practice Partner")

with st.sidebar:
    st.header("Interview Configuration")
    
    role = st.selectbox(
        "Select Role",
        ["Software Engineer", "Sales Representative", "Retail Associate"]
    )
    
    experience_level = st.selectbox(
        "Experience Level",
        ["Entry", "Mid", "Senior"]
    )
    
    if st.button("Start New Interview", type="primary"):
        st.session_state.interviewer = InterviewAgent(role, experience_level)
        st.session_state.conversation_manager.initialize_conversation(role, experience_level)
        
        opening = st.session_state.interviewer.start_interview()
        st.session_state.conversation_manager.add_message("assistant", opening)
        
        st.session_state.interview_started = True
        st.session_state.interview_ended = False
        st.session_state.feedback = None
        st.rerun()
    
    if st.session_state.interview_started and not st.session_state.interview_ended:
        if st.button("End Interview & Get Feedback"):
            st.session_state.interview_ended = True
            st.rerun()
    
    st.divider()
    st.markdown("**Instructions:**")
    st.markdown("1. Select role and experience level")
    st.markdown("2. Click 'Start New Interview'")
    st.markdown("3. Answer questions naturally")
    st.markdown("4. Click 'End Interview' for feedback")

if not st.session_state.interview_started:
    st.info("Configure your interview settings in the sidebar and click 'Start New Interview' to begin.")
    
elif st.session_state.interview_ended:
    st.success("Interview completed! Generating your feedback...")
    
    if st.session_state.feedback is None:
        conversation_history = st.session_state.interviewer.conversation_history
        
        feedback = st.session_state.evaluator.generate_final_feedback(
            conversation_history,
            role,
            experience_level
        )
        st.session_state.feedback = feedback
        st.session_state.conversation_manager.save_conversation()
    
    st.header("Interview Feedback Report")
    st.markdown(st.session_state.feedback)
    
    st.divider()
    st.subheader("Full Transcript")
    transcript = st.session_state.conversation_manager.get_formatted_transcript()
    st.text_area("Transcript", transcript, height=300)
    
    if st.button("Start Another Interview"):
        st.session_state.conversation_manager = ConversationManager()
        st.session_state.interviewer = None
        st.session_state.interview_started = False
        st.session_state.interview_ended = False
        st.session_state.feedback = None
        st.rerun()

else:
    conversation_history = st.session_state.interviewer.conversation_history
    
    for msg in conversation_history:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])
    
    user_input = st.chat_input("Type your answer here...")
    
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        st.session_state.conversation_manager.add_message("user", user_input)
        
        next_question = st.session_state.interviewer.generate_next_question(user_input)
        
        with st.chat_message("assistant"):
            st.write(next_question)
        
        st.session_state.conversation_manager.add_message("assistant", next_question)
        st.rerun()