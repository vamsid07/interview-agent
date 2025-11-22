import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).parent))

from agents.interviewer import InterviewAgent
from agents.evaluator import InterviewEvaluator
from agents.resume_analyzer import ResumeAnalyzer
from utils.conversation_manager import ConversationManager
from utils.resume_parser import ResumeParser
from utils.audio_manager import AudioManager

load_dotenv()
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="AI Interview Partner", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "conversation_manager" not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
    st.session_state.interviewer = None
    st.session_state.evaluator = InterviewEvaluator()
    st.session_state.resume_analyzer = ResumeAnalyzer()
    st.session_state.audio_manager = AudioManager()
    st.session_state.interview_started = False
    st.session_state.interview_ended = False
    st.session_state.evaluation_report = None
    st.session_state.resume_text = ""
    st.session_state.interview_plan = None
    st.session_state.interaction_mode = "Chat"
    
    # NEW: State variables to handle audio reset and autoplay
    st.session_state.audio_key = 0 
    st.session_state.latest_audio_response = None

st.title("AI Interview Practice Partner")
st.caption("Agentic Interview Simulation with Strategic Planning")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Setup")
    role = st.selectbox("Target Role", ["Software Engineer", "Sales Representative", "Retail Associate"])
    level = st.selectbox("Level", ["Entry", "Mid", "Senior"])
    
    st.session_state.interaction_mode = st.radio("Interaction Mode", ["Chat", "Voice"], horizontal=True)
    
    st.divider()
    
    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type="pdf")
    if uploaded_resume and not st.session_state.resume_text:
        with st.spinner("Reading & Analyzing Resume..."):
            text = ResumeParser.extract_text(uploaded_resume)
            if text:
                st.session_state.resume_text = text
                plan = st.session_state.resume_analyzer.analyze(role, text)
                st.session_state.interview_plan = plan
                st.success("Resume Analyzed!")
    
    if st.session_state.interview_plan:
        with st.expander("📋 Interview Strategy", expanded=True):
            st.caption(f"Candidate: {st.session_state.interview_plan.get('candidate_name', 'Unknown')}")
            st.markdown("**Focus Areas Detected:**")
            for area in st.session_state.interview_plan.get('focus_areas', []):
                st.warning(f"🎯 {area['topic']}")
                st.caption(f"Reason: {area['reason']}")

    st.divider()
    
    if not st.session_state.interview_started:
        if st.button("Start Interview", type="primary", use_container_width=True):
            try:
                st.session_state.interviewer = InterviewAgent(
                    role, level, st.session_state.resume_text, st.session_state.interview_plan
                )
                st.session_state.conversation_manager.initialize_conversation(role, level)
                opening = st.session_state.interviewer.start_interview()
                st.session_state.conversation_manager.add_message("assistant", opening)
                st.session_state.interview_started = True
                st.session_state.interview_ended = False
                st.session_state.evaluation_report = None
                
                # Generate audio for opening if in voice mode
                if st.session_state.interaction_mode == "Voice":
                     audio_response = st.session_state.audio_manager.text_to_speech(opening)
                     st.session_state.latest_audio_response = audio_response
                
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.interview_started and not st.session_state.interview_ended:
        if st.session_state.interviewer:
            thoughts = st.session_state.interviewer.get_latest_thought_process()
            if thoughts:
                with st.expander("🧠 AI Thought Process", expanded=True):
                    st.info(f"**Strategy:** {thoughts.get('strategy', 'N/A')}")
                    st.markdown(f"*{thoughts.get('reasoning', 'Thinking...')}*")

        if st.button("End Interview", use_container_width=True):
            st.session_state.interview_ended = True
            st.rerun()

# --- MAIN AREA ---
if st.session_state.interview_started and not st.session_state.interview_ended:
    # Display Chat History
    for msg in st.session_state.interviewer.conversation_history:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            
    # INPUT HANDLING
    user_input = None
    
    if st.session_state.interaction_mode == "Voice":
        # FIX: Use dynamic key to force widget reset after processing
        audio_bytes = st.audio_input("Speak your answer...", key=f"audio_in_{st.session_state.audio_key}")
        if audio_bytes:
            with st.spinner("Transcribing..."):
                text = st.session_state.audio_manager.speech_to_text(audio_bytes)
                if text:
                    user_input = text
                else:
                    st.warning("Could not understand audio. Please try again.")
    else:
        # Chat Input
        user_input = st.chat_input("Type your answer...")

    # PROCESS INPUT
    if user_input:
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        with st.spinner("Thinking..."):
            response, _ = st.session_state.interviewer.generate_next_question(user_input)
            
            # Handle Audio Response Logic
            if st.session_state.interaction_mode == "Voice":
                audio_response = st.session_state.audio_manager.text_to_speech(response)
                if audio_response:
                    # Store audio to play AFTER the rerun (on fresh UI state)
                    st.session_state.latest_audio_response = audio_response
                    # Increment key -> This destroys the old audio widget and creates a new empty one
                    st.session_state.audio_key += 1
            
            st.rerun()

    # AUTOPLAY RESPONSE (This runs after the rerun, preventing loops)
    if st.session_state.latest_audio_response:
        st.audio(st.session_state.latest_audio_response, format="audio/mp3", autoplay=True)
        st.session_state.latest_audio_response = None # Clear immediately so it plays only once

elif st.session_state.interview_ended:
    st.header("🏁 Interview Performance Report")
    
    if not st.session_state.evaluation_report:
        with st.spinner("Compiling Comprehensive Analytics..."):
            st.session_state.evaluation_report = st.session_state.evaluator.generate_comprehensive_report(
                st.session_state.interviewer.conversation_history, role, level, st.session_state.interview_plan
            )
    
    report = st.session_state.evaluation_report
    scores = report.get('scores', {})
    
    # Top Metric Row
    col1, col2, col3 = st.columns(3)
    col1.metric("Decision", report.get('hiring_decision', 'N/A'))
    col2.metric("Technical Score", f"{scores.get('technical_depth', 0)}/100")
    col3.metric("Communication", f"{scores.get('communication_clarity', 0)}/100")
    
    st.divider()
    
    # Radar Chart
    chart_col, text_col = st.columns([1, 1])
    
    with chart_col:
        categories = list(scores.keys())
        values = list(scores.values())
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=[c.replace('_', ' ').title() for c in categories],
            fill='toself',
            name='Candidate Profile'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with text_col:
        st.subheader("Executive Summary")
        st.write(report.get('executive_summary', 'No summary available.'))
        
        st.subheader("Coach's Tips 💡")
        for tip in report.get('feedback', {}).get('coach_tips', []):
            st.info(tip)

    st.divider()
    
    # Detailed Evidence Table
    st.subheader("Evidence & Verification")
    evidence = report.get('evidence', [])
    if evidence:
        for item in evidence:
            with st.expander(f"{item.get('verdict', 'Neutral')}: {item.get('claim', 'Claim')}"):
                st.markdown(f"**Quote:** *\"{item.get('quote', 'N/A')}\"*")
    else:
        st.caption("No specific claims verified.")
        
    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()

elif not st.session_state.interview_started:
    st.info("👈 Upload a resume to see the Strategic Planning Agent in action.")