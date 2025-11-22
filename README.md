# AI Interview Practice Partner

An intelligent, agentic interview simulation platform designed to prepare candidates for high-stakes technical and behavioral interviews.

Unlike standard chatbots that rely on static decision trees, this system implements a Planner-Executor-Evaluator multi-agent architecture. It reads resumes, formulates strategic interview plans, and utilizes an LLM-based reasoning engine to adapt its questioning strategy in real-time based on candidate performance.

## Project Overview

This application acts as an automated "Bar Raiser" interviewer. It addresses the limitations of static, repetitive mock interviews by introducing a Reasoning Engine ("The Brain").

Instead of simply moving to the next question, the agent evaluates the intent and quality of every user response. It dynamically decides whether to:

- **Drill Down**: Demand specific evidence if the user is vague.
- **Guide**: Provide scaffolding if the user is confused.
- **Move On**: Recognize a strong answer and transition to a new competency.

## Key Features

### 1. Strategic Resume Analysis ("The Architect")

- **Context-Aware**: Parses PDF resumes to extract key skills, project details, and experience levels.
- **Gap Detection**: Automatically identifies "Red Flags" (e.g., short tenures, lack of specifics) and "Focus Areas" before the interview begins.
- **Custom Planning**: Generates a bespoke interview strategy to verify specific claims made in the resume.

### 2. Agentic Reasoning Loop ("The Brain")

- **Internal Monologue**: The agent utilizes an internal thought process before generating a response. It classifies the candidate's persona (e.g., Nervous, Efficient, Evasive) to tailor its tone.
- **Glass Box UI**: Visualizes the AI's decision-making process in real-time via a "Thought Process" sidebar, making the agent's logic transparent.

### 3. Multi-Modal Interaction (Voice & Chat)

- **Voice Mode**: Features full Speech-to-Text (STT) and Text-to-Speech (TTS) integration for a realistic, hands-free interview experience.
- **Chat Mode**: Standard text-based interface for expedited practice.

### 4. Data-Driven Evaluation

- **Radar Charts**: Visualizes performance across 5 key dimensions: Technical Depth, Communication, Problem Solving, Culture Fit, and Consistency.
- **Evidence Verification**: Extracts specific quotes from the transcript to justify scores, ensuring feedback is objective and actionable.

## Demo Scenarios & Testing Evidence

The agent has been rigorously tested against specific user personas to ensure robust handling of edge cases.

### Scenario 1: The Confused User

**User Input**: "I... I'm not sure what you mean by that question."

**Agent Reasoning**: Detected `detected_persona: "Confused"` → Triggered `strategy: "GUIDE"`.

**Agent Response**: "Let me rephrase. Can you tell me about a specific time you had to debug a complex system? Think about the tools you used."

**Outcome**: Successfully simplified the prompt without providing the answer directly.

### Scenario 2: The Evasive User

**User Input**: "I am an expert in Python and scalable systems." (Generic claim)

**Agent Reasoning**: Detected `analysis: "Vague assertion, lacks evidence"` → Triggered `strategy: "DRILL_DOWN"`.

**Agent Response**: "You mentioned scalable systems. Can you walk me through a specific instance where you optimized a Python application for high concurrency? What were the specific metrics?"

**Outcome**: Forced the candidate to provide concrete proof of skills.

### Scenario 3: The Efficient User

**User Input**: (Provides a structured STAR method response with metrics)

**Agent Reasoning**: Detected `detected_persona: "Efficient"` → Triggered `strategy: "MOVE_ON"`.

**Agent Response**: "That's a clear example. Let's shift gears to System Design..."

**Outcome**: Maintained a high-paced interview flow, respecting the user's time.

### Scenario 4: The Edge Case (Off-Topic)

**User Input**: "What is the weather like right now?"

**Agent Reasoning**: Detected `strategy: "CLARIFY"`.

**Agent Response**: "I'm here to conduct your interview. Let's keep our focus on your professional background. Tell me about your last role."

**Outcome**: Firmly redirected the conversation back to the professional context.

## Technical Architecture

The system is built on a Planner-Executor-Evaluator pattern:

- **Input Layer**: Streamlit UI captures Resume (PDF), Text Chat, and Audio Input.
- **Analysis Layer (The Architect)**: Uses Llama-3.3-70b (via Groq) to extract a structured JSON plan from the resume.
- **Interaction Layer (The Interviewer)**:
  - **Reasoning Step**: Analyzes input → Selects Strategy → Updates Persona.
  - **Generation Step**: Uses Strategy + Context → Generates conversational response.
- **Evaluation Layer (The Evaluator)**: Compiles conversation history → Generates structured scoring JSON → Renders Plotly charts.

## Tech Stack

- **Frontend**: Streamlit (Python)
- **LLM Inference**: Groq API (Llama-3.3-70b-Versatile) for ultra-low latency.
- **Audio Processing**: SpeechRecognition, gTTS, pydub, FFmpeg.
- **Data Processing**: PyPDF (Resume parsing), Regex (Sanitization).
- **Visualization**: Plotly (Performance metrics).

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- **FFmpeg** (Required for audio processing)
  - Mac: `brew install ffmpeg`
  - Windows: [Download Installer](https://ffmpeg.org/download.html)
  - Linux: `sudo apt-get install ffmpeg`
- A free Groq API Key from [console.groq.com](https://console.groq.com)

### Installation

**Clone the repository**

```bash
git clone https://github.com/your-username/interview-agent.git
cd interview-agent
```

**Create a Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies**

```bash
pip install -r requirements.txt
```

**Configure Environment**

Create a `.env` file in the root directory:

```
GROQ_API_KEY=gsk_your_actual_key_here
USE_MOCK_API=False
```

**Run the Application**

```bash
streamlit run src/app.py
```

## Usage Guide

1. **Setup**: Select your target role (e.g., Software Engineer) and level (e.g., Mid-Level) in the sidebar.
2. **Resume Context**: Upload your PDF resume. The "Architect" agent will analyze it and display "Focus Areas" in the sidebar.
3. **Mode Selection**: Toggle between Chat or Voice mode.
4. **Interview**: Click "Start Interview". Answer the questions naturally.
5. **Feedback**: Click "End Interview" to generate your Comprehensive Performance Report with radar charts and actionable coaching tips.

## Future Roadmap

- **Coding Sandbox**: Integrate a live code editor for technical screening questions.
- **Video Analysis**: Use computer vision to analyze non-verbal cues (eye contact, posture).
- **Multi-Persona Configuration**: Allow users to select "Hostile", "Friendly", or "Neutral" interviewer personalities.
- **Session History**: Database integration to track progress over time.

## License

MIT

## Author

Vamsidhar Venkataraman