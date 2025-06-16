"""
Configuration settings and constants for the SevaSaathi
"""

import os

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "SevaSaathi",
    "page_icon": "🏛️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# API Configuration
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
API_TIMEOUT = 30

# Generation Configuration for Gemini API
GENERATION_CONFIG = {
    "temperature": 0.3,
    "topP": 0.8,
    "topK": 20,
    "maxOutputTokens": 1024
}

# Safety Settings for Gemini API
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# Theme Colors
THEME_COLORS = {
    "sage_green": "#9CAF88",
    "sage_green_dark": "#7A8A6B",
    "beige": "#F5F2E8",
    "beige_dark": "#E8E2D5",
    "orange_accent": "#D2691E",
    "orange_light": "#F4A460",
    "text_dark": "#2C3E2D",
    "text_light": "#5A6B5D",
    "white": "#FFFFFF",
    "shadow": "rgba(44, 62, 45, 0.1)"
}

# File paths
SCHEME_DATA_FILE = "scheme_data.json"

# User profile fields for extraction
PROFILE_FIELDS = [
    "age", "state", "category", "income", "disability",
    "occupation", "education", "gender", "family_size", "land_holding"
]

# Scheme matching configuration
MATCHING_SCORES = {
    "state_match": 30,
    "primary_target_match": 25,
    "category_match": 20,
    "age_appropriateness": 15,
    "additional_criteria": 10
}

# Application limits
MAX_SCHEMES_FOR_AI = 15  # Limit schemes for API call to avoid token limits
MAX_SCHEMES_DISPLAY = 10  # Maximum schemes to display
MIN_MATCHING_SCORE = 40   # Minimum score for scheme inclusion
FALLBACK_SCORE_THRESHOLD = 60  # Threshold for simple matching fallback

# Profile extraction prompt template
PROFILE_EXTRACTION_PROMPT = """
You are a helpful assistant that extracts user profile information for government scheme eligibility.

Current Profile: {current_profile}

User Input: "{user_input}"

Extract and update the following information if mentioned in the user input:
- age: numeric age (only if explicitly mentioned)
- state: Indian state name (only if explicitly mentioned)
- category: social category like General, OBC, SC, ST, Minority (only if mentioned)
- income: annual income or APL/BPL status (only if mentioned)
- disability: disability status and percentage (only if mentioned)
- occupation: job/profession like farmer, student, business, unemployed (only if mentioned)
- education: education level like 10th, 12th, graduate, diploma (only if mentioned)
- gender: male/female/other (only if mentioned)
- family_size: number of family members (only if mentioned)
- land_holding: agricultural land size in hectares (only if mentioned)

Rules:
1. Only extract information that is explicitly mentioned in the user input
2. Preserve all existing profile information
3. Update only the fields that are mentioned in new input
4. Return a valid JSON object
5. Do not add any explanatory text or markdown

Return ONLY the JSON object:
"""

# Scheme matching prompt template
SCHEME_MATCHING_PROMPT = """
You are an expert in Indian government schemes. Analyze user eligibility for schemes.

User Profile: {user_profile}

Schemes to analyze: {schemes_summary}

For each scheme, analyze eligibility based on:
1. State compatibility (All India schemes match any state)
2. Age and demographic requirements
3. Social category requirements
4. Occupation and education requirements
5. Disability status requirements
6. Income/poverty line requirements
7. Gender requirements
8. Tags and target beneficiaries

Scoring criteria:
- State match: +30 points
- Primary target match (student/farmer/women/disabled): +25 points
- Category match: +20 points
- Age appropriateness: +15 points
- Additional criteria: +10 points each

Return ONLY a JSON array. No explanatory text:
[
    {{
        "scheme_name": "exact scheme name",
        "matching_score": 75,
        "reasons": ["State eligibility", "Student benefits", "Age appropriate"]
    }}
]

Only include schemes with score >= 40. Maximum 10 schemes.
"""

# Environment variables
def get_api_key():
    """Get Gemini API key from environment variables"""
    return os.getenv('GEMINI_API_KEY')

# Default chat messages
DEFAULT_CHAT_MESSAGES = {
    "welcome": "👋 Welcome to the SevaSaathi! I'm here to help you find government schemes you're eligible for.",
    "profile_needed": "I need more information about you to find suitable schemes. Could you tell me about your:\n- Age and location (state)\n- Occupation or if you're a student\n- Education level\n- Any disabilities or special circumstances\n- Income level or poverty line status\n- Social category (if applicable)",
    "no_schemes": "🔍 No eligible schemes found based on your profile. Please provide more details about yourself to get better matches!",
    "api_key_missing": "⚠️ Please enter your Gemini API key in the sidebar first.",
    "no_data": "⚠️ No schemes data loaded. Please ensure scheme_data.json is in the same directory."
}
