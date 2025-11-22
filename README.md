# AI Interview Practice Partner

An intelligent, agentic interview simulation platform designed to help candidates prepare for high-stakes technical and behavioral interviews. This system moves beyond simple chatbot interactions by implementing a multi-agent architecture that reads resumes, formulates strategic interview plans, and adapts its questioning strategy in real-time based on candidate performance.

## Project Overview

This application serves as an automated "Bar Raiser" interviewer. It utilizes a Reasoning Engine ("The Brain") to analyze every candidate response for depth, clarity, and validity before deciding on the next move—whether to drill down into specifics, clarify a confusing point, or move to a new competency.

## Key Features

### 1. Strategic Resume Analysis ("The Architect")

- **Ingestion**: Parses PDF resumes to extract key skills and experiences.
- **Gap Analysis**: Automatically identifies "Red Flags" and "Focus Areas".
- **Custom Planning**: Generates a tailored interview strategy.

### 2. Agentic Reasoning Loop ("The Brain")

- **Internal Monologue**: The agent "thinks" before it speaks, evaluating input intent and quality.
- **Dynamic Strategy**: Selects strategies like DRILL_DOWN, GUIDE, or MOVE_ON.
- **Glass Box UI**: Visualizes the AI's thought process in real-time via the sidebar.

### 3. Voice Interaction Support

- **Speech-to-Text**: Transcribes candidate answers via microphone using Google Speech Recognition.
- **Text-to-Speech**: Generates realistic audio questions for an immersive interview experience.

## Demo Scenarios & Testing Evidence

This section documents how the agent handles specific user personas, as tested during development.

### 1. The Confused User

**Scenario**: User gives a vague or confused answer like "I'm not sure what you mean."

**Agent Reasoning**: Detected `detected_persona: "Confused"` and triggered `strategy: "GUIDE"`.

**Response**: "Let me rephrase - can you tell me about a time you faced a technical challenge? Think about a specific project."

**Outcome**: Successfully simplified the question without solving it for the user.

### 2. The Evasive User

**Scenario**: User claims "Expert Python" skills but gives a generic definition when asked.

**Agent Reasoning**: Detected `analysis: "Vague definitions, no specific examples"` and triggered `strategy: "DRILL_DOWN"`.

**Response**: "You mentioned Python. Can you walk me through a specific instance where you used a generator or decorator in production?"

**Outcome**: Forced the user to prove their claim.

### 3. The Efficient User

**Scenario**: User provides a comprehensive STAR method response.

**Agent Reasoning**: Detected `detected_persona: "Efficient"` and triggered `strategy: "MOVE_ON"`.

**Response**: "That's a clear example. Let's shift gears to System Design..."

**Outcome**: Kept the interview pace high without unnecessary nagging.

### 4. The Edge Case (Off-Topic)

**Scenario**: User asks "What is the weather like?"

**Agent Reasoning**: Detected `strategy: "CLARIFY"`.

**Response**: "I'm here to conduct your interview. Let's focus on your professional experience. Tell me about your last role."

**Outcome**: Firmly brought the conversation back to the interview context.

## Technical Architecture

The system follows a Planner-Executor-Evaluator pattern:

- **Input Layer**: Streamlit UI captures Resume (PDF), Chat, and Audio.
- **Analysis Layer (The Architect)**: Llama-3.3-70b (via Groq) extracts skills and gaps.
- **Interaction Layer (The Interviewer)**: Reasoning Step → Strategy Selection → Response Generation.
- **Evaluation Layer (The Evaluator)**: Compiles history → Generates scored report with evidence.

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A free Groq API Key (https://console.groq.com/)
- **FFmpeg**: Required for audio processing (Install via `brew install ffmpeg` or `apt-get install ffmpeg`).

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