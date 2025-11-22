# AI Interview Practice Partner

An intelligent, agentic interview simulation platform designed to help candidates prepare for high-stakes technical and behavioral interviews. This system moves beyond simple chatbot interactions by implementing a multi-agent architecture that reads resumes, formulates strategic interview plans, and adapts its questioning strategy in real-time based on candidate performance.

## Project Overview

This application serves as an automated "Bar Raiser" interviewer. It does not rely on static question banks. Instead, it utilizes a **Reasoning Engine (The Brain)** to analyze every candidate response for depth, clarity, and validity before deciding on the next move—whether to drill down into specifics, clarify a confusing point, or move to a new competency.

## Key Features

### 1. Strategic Resume Analysis ("The Architect")

- **Ingestion**: Parses PDF resumes to extract key skills and experiences.
- **Gap Analysis**: Automatically identifies "Red Flags" (e.g., short tenures, vague project descriptions) and "Focus Areas" before the interview begins.
- **Custom Planning**: Generates a tailored interview strategy to probe specific claims made in the resume.

### 2. Agentic Reasoning Loop ("The Brain")

- **Internal Monologue**: Unlike standard chatbots, this agent "thinks" before it speaks. It evaluates the user's input intent (e.g., Evasive, Efficient, Nervous) and quality.
- **Dynamic Strategy**: Selects an optimal interaction strategy for each turn:
  - **DRILL_DOWN**: Demands specific examples if answers are vague.
  - **GUIDE**: Provides hints if the candidate is stuck.
  - **MOVE_ON**: Recognizes satisfactory answers and transitions topics.
- **Glass Box UI**: Visualizes the AI's thought process in real-time via the sidebar, demonstrating agentic behavior.

### 3. Comprehensive Post-Interview Analytics

- **Data-Driven Evaluation**: Generates a detailed JSON-based assessment of the candidate.
- **Visual Analytics**: Displays a Radar Chart scoring the candidate across 5 key dimensions (Technical Depth, Communication, Problem Solving, Culture Fit, Consistency).
- **Evidence Verification**: Extracts and cites specific quotes from the transcript to justify every score.

## Technical Architecture

The system follows a **Planner-Executor-Evaluator** pattern:

1. **Input Layer**: Streamlit UI captures Resume (PDF) and User Chat.
2. **Analysis Layer (The Architect)**:
   - Model: Llama-3.3-70b (via Groq)
   - Task: JSON Extraction of skills and gaps.
3. **Interaction Layer (The Interviewer)**:
   - Reasoning Step: Analyzes input quality → Outputs Strategy JSON.
   - Generation Step: Uses Strategy + Context → Generates conversational text.
4. **Evaluation Layer (The Evaluator)**:
   - Compiles conversation history + Original Plan.
   - Generates structured scoring and evidence mapping.

## Tech Stack

- **Frontend**: Streamlit (Python)
- **LLM Inference**: Groq API (Llama-3.3-70b-Versatile) for ultra-low latency.
- **Data Processing**: PyPDF (Resume parsing), Regex (Sanitization).
- **Visualization**: Plotly (Radar charts and performance metrics).
- **Environment**: Python 3.10+

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A free Groq API Key (https://console.groq.com/)

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

## Design Decisions & Trade-offs

### 1. Agentic vs. Static Behavior

**Decision**: We prioritized a "Brain" architecture (Reasoning Loop) over a faster, simpler chatbot.

**Reasoning**: Standard LLMs are too agreeable. A real interviewer must be skeptical. The reasoning step allows the AI to critique the user silently and decide to be "tough" when necessary, significantly improving conversational quality and realism.

### 2. Resume-Driven Context

**Decision**: The interview context is derived primarily from the uploaded resume rather than a generic role description.

**Reasoning**: High-quality interviews are bespoke. By parsing the resume first, the agent establishes immediate context ("I see you used PyTorch..."), creating a more immersive and personalized experience (The "Intelligence" criteria).

### 3. Structured vs. Unstructured Evaluation

**Decision**: We force the LLM to output strict JSON for evaluations instead of free text.

**Reasoning**: This allows us to render quantitative data (Charts/Graphs) which provides objective feedback to the user, rather than a generic "Good job" summary.

## Future Roadmap

- **Voice Integration**: Implementing real-time STT/TTS (Speech-to-Text) for a fully hands-free experience.
- **Coding Sandbox**: Adding a live code editor for technical screening questions.
- **Multi-Persona Configuration**: Allowing users to select "Hostile", "Friendly", or "Neutral" interviewer personalities.