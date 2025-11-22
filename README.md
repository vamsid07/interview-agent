# AI Interview Practice Partner

An intelligent, adaptive interview practice agent that conducts realistic mock interviews, adapts to user behavior, and provides comprehensive feedback.

## Overview

This AI-powered agent helps candidates prepare for real-world interviews by simulating professional interview experiences across multiple roles. The system demonstrates adaptive behavior through real-time persona detection, dynamic questioning, and intelligent conversation management.

## Current Features

### Core Capabilities
- **Multi-Role Support**: Software Engineer, Sales Representative, Retail Associate
- **Experience Level Adaptation**: Entry, Mid, Senior level customization
- **Dynamic Interview Length**: 4-10 questions based on performance (not fixed)
- **Intelligent Follow-ups**: Up to 2 consecutive follow-ups based on response quality
- **Real-time Persona Detection**: Identifies confused, efficient, chatty, or normal users
- **Comprehensive Feedback**: Detailed evaluation with specific examples and recommendations
- **Response Validation**: Profanity detection, length validation, gibberish filtering
- **Robust Error Handling**: Retry logic, rate limiting, graceful degradation

### Adaptive Behaviors
- **Dynamic Question Selection**: Selects next question based on conversation flow and weak areas
- **Quality-Based Follow-ups**: Asks follow-ups based on response completeness, not arbitrary limits
- **Semantic Repetition Detection**: Uses n-gram phrase extraction to detect paraphrased repetitions
- **Performance-Based Termination**: Ends interview early if candidate performs consistently well
- **Category Coverage**: Ensures all competency areas are explored before ending
- **Response Quality Tracking**: Monitors and adapts to response quality trends

### Technical Implementation
- **API Retry Logic**: Exponential backoff with 3 retry attempts
- **Rate Limiting**: Request throttling to prevent API quota issues
- **Input Validation**: Both user input and LLM output validation
- **Error Recovery**: Multiple fallback levels for API failures
- **Logging**: Comprehensive logging for debugging and monitoring
- **Token Management**: Context window management with last 10 messages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                      │
│  (Chat Interface, Progress Tracking, Statistics)            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Application Layer                         │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ InterviewAgent   │  │ PersonaDetector  │               │
│  │ - Dynamic Q Gen  │  │ - Pattern Anal   │               │
│  │ - Smart Followup │  │ - Adaptation     │               │
│  │ - Flow Control   │  │ - Engagement     │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Evaluator        │  │ ResponseValidator│               │
│  │ - Feedback Gen   │  │ - Input Checks   │               │
│  │ - Scoring        │  │ - LLM Validation │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ RobustAPIClient  │  │ ConversationMgr  │               │
│  │ - Retry Logic    │  │ - State Mgmt     │               │
│  │ - Rate Limiting  │  │ - Persistence    │               │
│  └──────────────────┘  └──────────────────┘               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   LLM Integration Layer                     │
│              Google Gemini 2.0 Flash API                    │
└─────────────────────────────────────────────────────────────┘
```

## Recent Improvements (v2.0)

### 1. Removed Voice Mode
**Why**: Browser Web Speech API is unreliable, causes permission issues, and degrades UX. Focus on robust text-based interaction first.

### 2. Dynamic Interview Length
**Before**: Fixed 6 questions regardless of performance  
**After**: 4-10 questions based on response quality, topic coverage, and performance trends

### 3. Smart Follow-up System
**Before**: Maximum 1 follow-up per question  
**After**: Up to 2 consecutive follow-ups triggered by specific quality issues (brevity, uncertainty, lack of specifics)

### 4. Enhanced Repetition Detection
**Before**: Simple 70% word overlap  
**After**: Combined lexical and semantic similarity using n-gram phrase extraction (bigrams, trigrams)

### 5. Comprehensive Validation
**Added**: 
- User input validation (profanity, length, gibberish, copy-paste detection)
- LLM output validation (question structure, refusal detection, error checking)
- Response sanitization and normalization

### 6. Robust Error Handling
**Added**:
- Exponential backoff retry (3 attempts)
- Rate limit detection and handling
- Network error recovery
- Graceful fallbacks at multiple levels
- Comprehensive logging

### 7. Response Quality Scoring
**Added**: Multi-dimensional quality assessment considering:
- Word count and verbosity
- Uncertainty markers
- Specific examples and outcomes
- Structured answers (STAR method)
- Vagueness indicators

## Tech Stack

- **Language**: Python 3.9+
- **UI Framework**: Streamlit
- **LLM API**: Google Gemini 2.0 Flash (free tier)
- **State Management**: Session state + JSON persistence
- **Data Validation**: Custom validation layer
- **Logging**: Python logging module

## Project Structure

```
interview-agent/
├── src/
│   ├── agents/
│   │   ├── interviewer.py           # Main agent with adaptive logic
│   │   ├── evaluator.py             # Feedback generation with validation
│   │   └── role_configs.py          # Role-specific configurations
│   ├── prompts/
│   │   ├── system_prompts.py        # LLM system prompts
│   │   └── evaluation_rubrics.py   # Scoring criteria
│   ├── utils/
│   │   ├── conversation_manager.py  # State and persistence
│   │   ├── persona_detector.py      # User behavior analysis
│   │   ├── response_validator.py    # Input/output validation
│   │   └── api_client.py            # Robust API client with retry
│   └── app.py                        # Streamlit application
├── data/
│   └── conversation_logs/            # Saved interview sessions
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Google API key (free at https://ai.google.dev/)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/interview-agent.git
cd interview-agent
```

2. Create and activate virtual environment
```bash
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
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
GOOGLE_API_KEY=your_google_api_key_here
```

To get a free API key:
- Visit https://ai.google.dev/
- Click "Get API key in Google AI Studio"
- Sign in with Google account
- Create and copy API key

### Running the Application

```bash
python -m streamlit run src/app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### Basic Interview Flow

1. **Configure Interview**
   - Select job role (Software Engineer / Sales Representative / Retail Associate)
   - Choose experience level (Entry / Mid / Senior)

2. **Start Interview**
   - Click "Start New Interview"
   - AI introduces itself and asks opening question

3. **Answer Questions**
   - Type responses in chat input
   - AI adapts questioning based on your answers
   - Watch engagement score and response quality metrics in sidebar

4. **Complete Interview**
   - Interview ends automatically when performance plateaus or 10 questions reached
   - Can manually end anytime with "End Interview & Get Feedback"
   - Review comprehensive evaluation with specific examples

### Response Guidelines

**For best feedback:**
- Aim for 50-100 words per response
- Use the STAR method (Situation, Task, Action, Result)
- Provide specific examples with measurable outcomes
- Avoid excessive uncertainty markers ("I'm not sure", "maybe")
- Stay on topic and be concise

**The system will:**
- Ask clarifying questions if responses are too brief
- Redirect if you repeat previous answers
- Request specifics if answers are too general
- Flag inappropriate or invalid content

## Known Limitations

1. **LLM Dependency**: Relies on Google Gemini free tier (rate limits may apply during heavy usage)
2. **No Voice Input**: Text-only interaction (voice was removed due to reliability issues)
3. **No Persistent User Accounts**: Each session is independent, no login system
4. **Limited Question Bank**: Predefined fallback questions may repeat in very long interviews
5. **Basic Persona Detection**: Uses heuristics rather than true behavioral modeling
6. **No Real-Time Collaboration**: Single-user sessions only

## Future Enhancements

### High Priority
- Automated test suite with example conversations
- Structured evaluation output with validated JSON scores
- True agentic reasoning (planning, reflection, goal-oriented questioning)
- Privacy policy and data retention documentation

### Medium Priority
- Industry-specific question banks (FAANG, startups, enterprise)
- Multi-session progress tracking
- Comparison with previous attempts
- Mock technical coding challenges

### Low Priority
- Multi-language support
- Team/panel interview simulation
- Video recording and analysis
- Integration with job boards

## Contributing

Contributions are welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request with clear description

## License

MIT License

## Acknowledgments

Built for Eightfold.ai's AI Agent Challenge. Demonstrates practical application of LLM-based conversational agents with real-world constraints and reliability requirements.

---

**Current Status**: Production-ready for text-based mock interviews with robust error handling and adaptive behavior. Voice mode removed, test suite pending, structured output validation pending.