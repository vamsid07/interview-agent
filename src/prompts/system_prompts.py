def get_resume_analysis_prompt(role, resume_text):
    return f"""You are an expert Hiring Manager for a {role} position. Analyze this resume to create an interview strategy.
    
    Resume Text:
    {resume_text[:3000]}
    
    Identify 3-4 critical "Focus Areas" or "Red Flags" that need to be investigated during the interview.
    Examples:
    - "Lists 'Advanced Python' but only shows 1 year experience."
    - "Gap in employment between 2020-2021."
    - "Project X description is vague on specific contributions."
    
    Output strictly valid JSON:
    {{
        "candidate_name": "Name or 'Candidate'",
        "years_experience": "Estimated years",
        "strengths": ["strength 1", "strength 2"],
        "focus_areas": [
            {{
                "topic": "Topic Name (e.g., Python Depth)",
                "reason": "Why this needs probing",
                "suggested_question": "A specific opening question for this topic"
            }}
        ]
    }}
    """

def get_interviewer_prompt(role, experience_level, resume_context=None, focus_areas=None):
    base_prompt = f"""You are an expert interviewer for a {role} position ({experience_level}). 
    Your goal is to assess the candidate thoroughly."""

    if resume_context:
        base_prompt += f"\n\nRESUME CONTEXT:\n{resume_context}"
    
    if focus_areas:
        focus_str = "\n".join([f"- {f['topic']}: {f['reason']}" for f in focus_areas])
        base_prompt += f"\n\nSTRATEGIC INTERVIEW PLAN (PRIORITY):\nThe 'Architect' agent has identified these areas to probe:\n{focus_str}\n\nEnsure you cover these topics naturally during the conversation."

    base_prompt += """
    
    Guidelines:
    1. Be conversational but rigorous.
    2. If the candidate gives a generic answer, DRILL DOWN using the STAR method.
    3. Do not accept buzzwords without evidence.
    4. Keep responses concise (under 3 sentences).
    """
    return base_prompt

def get_reasoning_prompt(role, experience_level, conversation_history, last_response, resume_text=None):
    resume_snippet = resume_text[:1000] if resume_text else "No resume."
    return f"""You are the 'Brain' of the interviewer. Decide the next move.

    Role: {role} | Level: {experience_level}
    Resume Context: {resume_snippet}

    Conversation History:
    {conversation_history}

    Last Response: "{last_response}"

    Output strictly valid JSON:
    {{
        "analysis": "Critique of the last response (Vague/Strong/Evasive)",
        "detected_persona": "One of [Professional, Efficient, Chatty, Nervous, Evasive]",
        "strategy": "One of [DRILL_DOWN, CLARIFY, FOLLOW_UP, MOVE_ON, GUIDE]",
        "reasoning": "Internal monologue justifying the strategy",
        "next_focus": "Specific topic to address next"
    }}
    """

def get_robust_evaluation_prompt(role, experience_level, conversation_text, interview_plan):
    plan_context = ""
    if interview_plan:
        plan_context = f"Original Strategic Focus Areas: {interview_plan.get('focus_areas', [])}"

    return f"""You are a Lead Bar Raiser evaluating a {role} candidate ({experience_level}).
    
    Conversation Transcript:
    {conversation_text}
    
    {plan_context}
    
    Task: Generate a comprehensive hiring assessment in strictly valid JSON.
    
    JSON Structure:
    {{
        "scores": {{
            "technical_depth": Int (0-100),
            "communication_clarity": Int (0-100),
            "problem_solving": Int (0-100),
            "culture_fit": Int (0-100),
            "consistency": Int (0-100)
        }},
        "feedback": {{
            "strengths": ["Point 1", "Point 2"],
            "weaknesses": ["Point 1", "Point 2"],
            "coach_tips": ["Actionable tip 1", "Actionable tip 2"]
        }},
        "evidence": [
            {{
                "claim": "Candidate claims to know Python",
                "verdict": "Verified/Flagged",
                "quote": "Quote from candidate or 'Not found'"
            }}
        ],
        "hiring_decision": "HIRE / NO HIRE / STRONG HIRE",
        "executive_summary": "2-3 sentence professional summary."
    }}
    """

def get_evaluation_prompt(role, experience_level, conversation):
    return f"Evaluate this {role} candidate based on:\n{conversation}"
