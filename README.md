# AI Interview Practice Partner

An AI-powered interview practice agent that conducts mock interviews, asks intelligent follow-ups, and provides comprehensive feedback.

## Features

- Conducts interviews for Software Engineer, Sales Representative, and Retail Associate roles
- Adapts to different user personas (confused, efficient, chatty, normal)
- Generates intelligent follow-up questions based on responses
- Real-time engagement scoring and progress tracking
- STAR method detection in candidate responses
- Comprehensive feedback report with detailed evaluation
- Download interview transcripts
- Error handling with graceful fallbacks

## Tech Stack

- Python 3.9+
- Streamlit for UI
- Google Gemini 2.0 Flash (Free API)
- Pydantic for data validation

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Google API key (free at ai.google.dev)

### Installation

1. Clone the repository
```bash
git clone https://github.com/vamsid07/interview-agent.git
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

Get your free API key at https://ai.google.dev/

### Running the Application

```bash
python -m streamlit run src/app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. Select the job role and experience level from the sidebar
2. Click "Start New Interview"
3. Answer the interviewer's questions naturally
4. The agent will adapt its questioning style based on your responses
5. Monitor your engagement score in real-time
6. Click "End Interview & Get Feedback" when ready
7. Review your comprehensive feedback report
8. Download transcript for future reference

## Project Structure

```
interview-agent/
├── src/
│   ├── agents/
│   │   ├── interviewer.py           # Main interview agent
│   │   ├── evaluator.py             # Feedback generation
│   │   └── role_configs.py          # Role configurations
│   ├── prompts/
│   │   ├── system_prompts.py        # LLM prompts
│   │   └── evaluation_rubrics.py   # Scoring criteria
│   ├── utils/
│   │   ├── conversation_manager.py  # State management
│   │   └── persona_detector.py      # User persona detection
│   └── app.py                        # Streamlit application
├── data/
│   └── conversation_logs/            # Saved interviews
├── requirements.txt
├── .env.example
└── README.md
```

## Design Decisions

### Why Google Gemini 2.0 Flash?
- Completely free API with generous quota
- Fast response times suitable for real-time interviews
- Good conversation quality and context retention
- Sufficient context window for multi-turn interviews

### Adaptive Questioning
The agent detects four user personas and adapts accordingly:
- **Confused**: Provides clarification, examples, and structure
- **Efficient**: Respects pace, moves forward with minimal probing
- **Chatty**: Politely redirects to stay on track
- **Normal**: Maintains standard interview flow

### Real-time Response Evaluation
Each response is evaluated for:
- Word count and response length
- Uncertainty markers
- STAR method usage
- Specific examples and achievements

This enables intelligent follow-up decisions.

### Engagement Scoring
Calculates engagement based on:
- Response length consistency
- Certainty level
- Answer quality
- Overall participation

### Error Handling
- Graceful API failure handling
- Fallback questions for each role
- Environment variable validation
- User-friendly error messages

## Key Features

### Interview Adaptation
- Limits follow-up questions to avoid over-probing
- Adjusts questioning based on persona detection
- Tracks covered topics to avoid repetition
- Provides structured guidance for confused candidates

### Comprehensive Evaluation
- Role-specific scoring criteria
- Experience level expectations
- Detailed strengths and improvement areas
- Actionable recommendations
- Specific examples from conversation

### User Experience
- Real-time progress tracking
- Visual engagement metrics
- Clean, intuitive interface
- Interview statistics dashboard
- Transcript download functionality

## Future Enhancements

- Voice input/output support
- Multi-language support
- Additional job roles
- Interview analytics dashboard
- PDF export of feedback reports
- Integration with calendar for scheduling
- Practice question bank expansion

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License