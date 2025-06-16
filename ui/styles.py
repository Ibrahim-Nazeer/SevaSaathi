"""
CSS styling for the SevaSaathi
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
    <style>
    /* Main app styling */
    .main {
        padding-top: 1rem;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Profile card styling */
    .profile-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .profile-item {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .profile-item strong {
        color: #495057;
    }
    
    /* Scheme card styling */
    .scheme-card {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .scheme-header {
        border-bottom: 2px solid #007bff;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    
    .scheme-title {
        color: #007bff;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }
    
    .scheme-score {
        background: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .scheme-score.medium {
        background: #ffc107;
        color: #212529;
    }
    
    .scheme-score.low {
        background: #6c757d;
    }
    
    /* Info sections */
    .info-section {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
    
    .info-section h4 {
        color: #007bff;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    
    .eligibility-section {
        background: #d4edda;
        border-left: 4px solid #28a745;
    }
    
    .eligibility-section h4 {
        color: #28a745;
    }
    
    .benefits-section {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    
    .benefits-section h4 {
        color: #856404;
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        display: block;
    }
    
    .assistant-message {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Progress indicators */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .progress-step {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #6c757d;
        color: white;
        line-height: 30px;
        margin: 0 0.5rem;
        font-weight: 600;
    }
    
    .progress-step.active {
        background: #007bff;
    }
    
    .progress-step.completed {
        background: #28a745;
    }
    
    /* Alerts and notifications */
    .alert {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid transparent;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border-color: #bee5eb;
        color: #0c5460;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 2rem;
        }
        
        .app-header p {
            font-size: 1rem;
        }
        
        .scheme-card {
            padding: 1rem;
        }
        
        .user-message, .assistant-message {
            max-width: 95%;
        }
    }
    
    /* Loading animations */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #007bff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Scheme statistics */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
        min-width: 150px;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #007bff;
        display: block;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e9ecef;
        color: #6c757d;
    }
    
    /* Custom expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .streamlit-expanderContent {
        background-color: white;
        border: 1px solid #e9ecef;
        border-top: none;
        border-radius: 0 0 5px 5px;
    }
    
    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

def get_scheme_score_class(score):
    """Get CSS class based on scheme matching score"""
    if score >= 80:
        return "scheme-score"
    elif score >= 60:
        return "scheme-score medium"
    else:
        return "scheme-score low"

def format_profile_display(profile):
    """Format user profile for display"""
    if not profile:
        return "<p>No profile information available</p>"
    
    html = "<div class='profile-card'>"
    for key, value in profile.items():
        if value:  # Only show non-empty values
            display_key = key.replace('_', ' ').title()
            html += f"""
            <div class='profile-item'>
                <strong>{display_key}:</strong>
                <span>{value}</span>
            </div>
            """
    html += "</div>"
    return html

def create_stats_display(total_schemes, eligible_schemes, user_state=None):
    """Create statistics display for schemes"""
    eligible_count = len(eligible_schemes) if eligible_schemes else 0
    match_percentage = (eligible_count / total_schemes * 100) if total_schemes > 0 else 0
    
    return f"""
    <div class='stats-container'>
        <div class='stat-item'>
            <span class='stat-number'>{total_schemes}</span>
            <div class='stat-label'>Total Schemes</div>
        </div>
        <div class='stat-item'>
            <span class='stat-number'>{eligible_count}</span>
            <div class='stat-label'>Eligible Schemes</div>
        </div>
        <div class='stat-item'>
            <span class='stat-number'>{match_percentage:.1f}%</span>
            <div class='stat-label'>Match Rate</div>
        </div>
        {f"<div class='stat-item'><span class='stat-number'>{user_state}</span><div class='stat-label'>Your State</div></div>" if user_state else ""}
    </div>
    """