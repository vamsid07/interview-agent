import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
from streamlit.components.v1 import html

sys.path.append(str(Path(__file__).parent))

from agents.interviewer import InterviewAgent
from agents.evaluator import InterviewEvaluator
from utils.conversation_manager import ConversationManager

load_dotenv()

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
    st.session_state.voice_mode = False
    st.session_state.last_question = None
    st.session_state.voice_input_counter = 0

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
    
    voice_mode = st.toggle(
        "🎤 Voice Mode",
        value=st.session_state.voice_mode,
        help="Enable two-way voice conversation"
    )
    st.session_state.voice_mode = voice_mode
    
    if voice_mode:
        st.success("🎙️ Voice conversation enabled")
        st.caption("Speak your answers using the microphone button")
    
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
                    st.session_state.last_question = opening
                    
                    st.session_state.interview_started = True
                    st.session_state.interview_ended = False
                    st.session_state.feedback = None
                    st.session_state.error_message = None
                    st.rerun()
            except Exception as e:
                st.session_state.error_message = f"Error starting interview: {str(e)}"
    
    if st.session_state.interview_started and not st.session_state.interview_ended:
        st.info(f"**Current Interview**\n\nRole: {role}\n\nLevel: {experience_level}")
        
        progress = min(st.session_state.interviewer.question_count / 6, 1.0)
        st.progress(progress, text=f"Question {st.session_state.interviewer.question_count} of 6")
        
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
            st.session_state.last_question = None
            st.rerun()
    
    st.divider()
    st.markdown("### How to Use")
    if voice_mode:
        st.markdown("""
        1. Click 🎤 Record to speak your answer
        2. AI will read questions aloud
        3. Speak naturally and clearly
        4. Click Stop when done speaking
        """)
    else:
        st.markdown("""
        1. Select role and experience level
        2. Click 'Start New Interview'
        3. Type your answers
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
    st.info("👈 Configure your interview settings in the sidebar and click 'Start New Interview' to begin.")
    
    with st.expander("About This Tool"):
        st.markdown("""
        This AI-powered interview practice tool helps you prepare for real interviews by:
        
        - **Adaptive Questioning**: Adjusts to your response style
        - **Intelligent Follow-ups**: Probes deeper when needed
        - **Persona Detection**: Recognizes if you're confused, efficient, or chatty
        - **Voice Conversation**: Two-way voice interaction for realistic practice
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
            st.session_state.last_question = None
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
    if st.session_state.voice_mode:
        voice_component = f"""
        <div style="position: sticky; top: 60px; z-index: 1000; background: white; padding: 20px; border: 2px solid #0066cc; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div style="display: flex; gap: 10px;">
                    <button id="recordBtn" onclick="toggleRecording()" style="padding: 12px 24px; background: #ff4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold;">
                        🎤 Start Recording
                    </button>
                    <button onclick="stopSpeech()" style="padding: 12px 24px; background: #666; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">
                        🔇 Stop Audio
                    </button>
                </div>
                <div id="status" style="color: #0066cc; font-weight: bold; font-size: 16px;">Ready to listen</div>
            </div>
            <div id="transcript" style="min-height: 40px; padding: 10px; background: #f5f5f5; border-radius: 4px; font-style: italic; color: #666;">
                Your speech will appear here...
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isRecording = false;
            let synth = window.speechSynthesis;
            
            if ('webkitSpeechRecognition' in window) {{
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = function() {{
                    document.getElementById('status').textContent = '🎤 Listening...';
                    document.getElementById('status').style.color = '#00cc00';
                    document.getElementById('transcript').textContent = 'Speak now...';
                }};
                
                recognition.onresult = function(event) {{
                    let interimTranscript = '';
                    let finalTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {{
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {{
                            finalTranscript += transcript + ' ';
                        }} else {{
                            interimTranscript += transcript;
                        }}
                    }}
                    
                    if (finalTranscript) {{
                        document.getElementById('transcript').textContent = finalTranscript;
                        const input = document.querySelector('input[type="text"]');
                        if (input) {{
                            input.value = finalTranscript.trim();
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    }} else if (interimTranscript) {{
                        document.getElementById('transcript').textContent = interimTranscript;
                    }}
                }};
                
                recognition.onerror = function(event) {{
                    document.getElementById('status').textContent = '❌ Error: ' + event.error;
                    document.getElementById('status').style.color = '#ff0000';
                    isRecording = false;
                    document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                    document.getElementById('recordBtn').style.background = '#ff4444';
                }};
                
                recognition.onend = function() {{
                    if (isRecording) {{
                        document.getElementById('status').textContent = '✅ Done! Review your answer below';
                        document.getElementById('status').style.color = '#0066cc';
                    }}
                    isRecording = false;
                    document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                    document.getElementById('recordBtn').style.background = '#ff4444';
                }};
            }} else {{
                document.getElementById('status').textContent = '❌ Voice recognition not supported in this browser';
                document.getElementById('status').style.color = '#ff0000';
            }}
            
            function toggleRecording() {{
                if (!recognition) {{
                    alert('Voice recognition not supported. Please use Chrome, Edge, or Safari.');
                    return;
                }}
                
                if (!isRecording) {{
                    recognition.start();
                    isRecording = true;
                    document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
                    document.getElementById('recordBtn').style.background = '#00cc00';
                }} else {{
                    recognition.stop();
                    isRecording = false;
                }}
            }}
            
            function speakText(text) {{
                if (synth.speaking) {{
                    synth.cancel();
                }}
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                const voices = synth.getVoices();
                const englishVoice = voices.find(v => v.lang.startsWith('en'));
                if (englishVoice) {{
                    utterance.voice = englishVoice;
                }}
                
                synth.speak(utterance);
            }}
            
            function stopSpeech() {{
                synth.cancel();
            }}
            
            if (synth.getVoices().length === 0) {{
                synth.addEventListener('voiceschanged', function() {{
                    speakText({repr(st.session_state.last_question or "")});
                }});
            }} else {{
                speakText({repr(st.session_state.last_question or "")});
            }}
        </script>
        """
        html(voice_component, height=200)
    
    conversation_history = st.session_state.interviewer.conversation_history
    
    for msg in conversation_history:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])
    
    user_input = st.chat_input("Type your answer here or use voice recording above..." if st.session_state.voice_mode else "Type your answer here...")
    
    if user_input:
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        st.session_state.conversation_manager.add_message("user", user_input)
        
        with st.spinner("Thinking..."):
            try:
                next_question = st.session_state.interviewer.generate_next_question(user_input)
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(next_question)
                
                st.session_state.conversation_manager.add_message("assistant", next_question)
                st.session_state.last_question = next_question
                
                st.rerun()
            except Exception as e:
                st.error(f"Error generating question: {str(e)}")
                st.info("Please try responding again or end the interview for feedback.")