# AI Interview Practice Partner

An AI-powered interview practice agent that conducts mock interviews, asks intelligent follow-ups, and provides comprehensive feedback.

## Features

- Conducts interviews for Software Engineer, Sales Representative, and Retail Associate roles
- Adapts to different user personas (confused, efficient, chatty, normal)
- Generates intelligent follow-up questions based on responses
- Provides detailed feedback report after interview completion
- Saves interview transcripts for review

## Tech Stack

- Python 3.9+
- Streamlit for UI
- Google Gemini 1.5 Flash (Free API)
- Pydantic for data validation

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Google API key (free at ai.google.dev)

### Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd interview-agent
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_key_here
```

### Running the Application

```bash
streamlit run src/app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. Select the job role and experience level from the sidebar
2. Click "Start New Interview"
3. Answer the interviewer's questions naturally
4. The agent will adapt its questioning style based on your responses
5. Click "End Interview & Get Feedback" when ready
6. Review your comprehensive feedback report

## Project Structure

```
interview-agent/
├── src/
│   ├── agents/
│   │   ├── interviewer.py        # Main interview agent
│   │   ├── evaluator.py          # Feedback generation
│   │   └── role_configs.py       # Role configurations
│   ├── prompts/
│   │   └── system_prompts.py     # LLM prompts
│   ├── utils/
│   │   ├── conversation_manager.py  # State management
│   │   └── persona_detector.py      # User persona detection
│   └── app.py                     # Streamlit application
├── data/
│   └── conversation_logs/         # Saved interviews
├── requirements.txt
├── .env.example
└── README.md
```

## Design Decisions

### Why Google Gemini 1.5 Flash?
- Completely free API with generous quota
- Fast response times
- Good conversation quality
- Sufficient context window for interviews

### Adaptive Questioning
The agent detects four user personas and adapts accordingly:
- **Confused**: Provides clarification and examples
- **Efficient**: Respects pace and moves forward quickly
- **Chatty**: Politely redirects to stay on track
- **Normal**: Maintains standard interview flow

### Real-time Response Evaluation
Each response is evaluated for flags like "too_brief" or "uncertain" to determine if follow-up questions are needed.

## Future Enhancements

- Voice input/output support
- Multi-language support
- Additional job roles
- Interview analytics dashboard
- PDF export of feedback reports