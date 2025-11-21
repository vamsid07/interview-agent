ROLE_CONFIGURATIONS = {
    "Software Engineer": {
        "categories": ["technical", "behavioral", "problem_solving"],
        "competencies": ["coding", "system_design", "debugging", "collaboration"],
        "duration": "30-45 minutes"
    },
    "Sales Representative": {
        "categories": ["sales_methodology", "behavioral", "situational"],
        "competencies": ["persuasion", "objection_handling", "client_relationships", "closing"],
        "duration": "30-40 minutes"
    },
    "Retail Associate": {
        "categories": ["customer_service", "behavioral", "situational"],
        "competencies": ["customer_interaction", "conflict_resolution", "product_knowledge", "teamwork"],
        "duration": "20-30 minutes"
    }
}

QUESTION_BANKS = {
    "Software Engineer": {
        "opening": [
            "Tell me about your experience as a software engineer.",
            "What interests you most about software development?"
        ],
        "technical": [
            "Describe a complex technical problem you solved recently.",
            "How do you approach debugging a production issue?",
            "Explain how you would design a system for high availability."
        ],
        "behavioral": [
            "Tell me about a time you disagreed with a team member on a technical decision.",
            "Describe a situation where you had to learn a new technology quickly.",
            "How do you handle tight deadlines while maintaining code quality?"
        ]
    },
    "Sales Representative": {
        "opening": [
            "Tell me about your sales experience.",
            "What motivates you in a sales role?"
        ],
        "sales_methodology": [
            "Walk me through your typical sales process.",
            "How do you qualify potential leads?",
            "Describe your approach to closing a deal."
        ],
        "behavioral": [
            "Tell me about a time you lost a deal. What happened?",
            "Describe a situation where you exceeded your sales quota.",
            "How do you handle rejection in sales?"
        ]
    },
    "Retail Associate": {
        "opening": [
            "Tell me about your customer service experience.",
            "What do you enjoy about working with customers?"
        ],
        "customer_service": [
            "How would you handle an angry customer?",
            "Describe a time you went above and beyond for a customer.",
            "How do you balance helping multiple customers at once?"
        ],
        "behavioral": [
            "Tell me about a time you worked as part of a team.",
            "Describe a situation where you had to handle a difficult coworker.",
            "How do you stay motivated during slow periods?"
        ]
    }
}

EVALUATION_RUBRICS = {
    "Software Engineer": {
        "technical_knowledge": 0.35,
        "problem_solving": 0.25,
        "communication": 0.20,
        "cultural_fit": 0.20
    },
    "Sales Representative": {
        "sales_skills": 0.35,
        "communication": 0.30,
        "relationship_building": 0.20,
        "cultural_fit": 0.15
    },
    "Retail Associate": {
        "customer_service": 0.35,
        "communication": 0.25,
        "teamwork": 0.20,
        "cultural_fit": 0.20
    }
}