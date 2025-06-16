"""
Reusable UI components for the SevaSaathi
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from config.settings import PAGE_CONFIG
from .styles import get_scheme_score_class, format_profile_display, create_stats_display

def render_app_header():
    """Render the main application header"""
    st.markdown(f"""
    <div class='app-header'>
        <h1>{PAGE_CONFIG['app_icon']} {PAGE_CONFIG['app_title']}</h1>
        <p>Find government schemes you're eligible for!</p>
    </div>
    """, unsafe_allow_html=True)

def render_profile_section(user_profile: Dict[str, Any]):
    with st.sidebar:
        """Render user profile section"""
        st.header("👤 Your Profile")
        
        if user_profile:
            # Display profile in a nice format
            st.markdown(format_profile_display(user_profile), unsafe_allow_html=True)
            
            # Profile completion indicator
            total_fields = 10  # Total possible profile fields
            filled_fields = len([v for v in user_profile.values() if v])
            completion_percentage = (filled_fields / total_fields) * 100
            
            st.progress(completion_percentage / 100)
            st.caption(f"Profile completion: {completion_percentage:.0f}% ({filled_fields}/{total_fields} fields)")
            
        else:
            st.info("💡 No profile information yet. Start chatting to build your profile!")
        
        # Clear profile button
        if st.button("🗑 Clear Profile", help="Reset your profile information"):
            return True
        return False

def render_api_key_section():
    """Render API key configuration section"""
    import os
    
    # Try to load API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        st.success("✅ API Key loaded from .env file")
        # Show masked API key
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        st.caption(f"API Key: {masked_key}")
        return api_key
    else:
        st.warning("⚠️ No API key found in .env file")
        api_key = st.text_input(
            "Enter Gemini API Key manually", 
            type="password", 
            help="Get your API key from Google AI Studio (https://makersuite.google.com/app/apikey)"
        )
        if not api_key:
            st.error("Please add GEMINI_API_KEY to your .env file or enter it manually")
        return api_key

def render_schemes_statistics(total_schemes: int, eligible_schemes: List[Dict], user_profile: Dict):
    """Render schemes statistics"""
    user_state = user_profile.get('state', None)
    stats_html = create_stats_display(total_schemes, eligible_schemes, user_state)
    st.markdown(stats_html, unsafe_allow_html=True)

def render_scheme_card(scheme_info: Dict[str, Any], rank: int, expanded: bool = False):
    """Render individual scheme card"""
    scheme = scheme_info['scheme_details']
    score = scheme_info['matching_score']
    
    # Create expander with scheme information
    with st.expander(
        f"#{rank} {scheme['scheme_name']} (Match: {score}%)", 
        expanded=expanded
    ):
        # Two column layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Basic Information**")
            _render_info_item("Category", scheme.get('category', 'N/A'))
            _render_info_item("State", scheme.get('state', 'N/A'))
            _render_info_item("Level", scheme.get('level', 'N/A'))
            _render_info_item("Implementing Agency", scheme.get('implementing_agency', 'N/A'))
            _render_info_item("Target Beneficiaries", scheme.get('target_beneficiaries', 'N/A'))
        
        with col2:
            st.markdown("**✅ Why you're eligible:**")
            st.write(scheme_info['eligibility_explanation'])
            st.markdown("**🏷️ Tags:**")
            st.write(scheme.get('tags', 'N/A'))
        
        # Description section
        st.markdown("**📖 Description:**")
        description = scheme.get('brief_description') or scheme.get('detailed_description', 'N/A')
        if len(description) > PAGE_CONFIG['description_max_length']:
            description = description[:PAGE_CONFIG['description_max_length']] + "..."
        st.write(description)
        
        # Eligibility criteria
        st.markdown("**📋 Eligibility Criteria:**")
        st.write(scheme.get('eligibility_criteria', 'N/A'))
        
        # Documents required
        st.markdown("**📄 Documents Required:**")
        st.write(scheme.get('documents_required', 'N/A'))
        
        # Benefits
        st.markdown("**🎁 Benefits:**")
        st.write(scheme.get('benefits', 'N/A'))
        
        # Links section
        _render_scheme_links(scheme)

def render_schemes_list(eligible_schemes: List[Dict[str, Any]]):
    """Render list of eligible schemes"""
    if not eligible_schemes:
        st.warning("No eligible schemes found based on your profile. Please provide more details about yourself.")
        return
    
    st.success(f"Found {len(eligible_schemes)} eligible schemes for you!")
    
    # Show top schemes
    max_display = min(len(eligible_schemes), PAGE_CONFIG['max_schemes_to_display'])
    
    for i, scheme_info in enumerate(eligible_schemes[:max_display], 1):
        expanded = i <= PAGE_CONFIG['max_expanded_schemes']
        render_scheme_card(scheme_info, i, expanded)

def render_chat_interface(chat_history: List[Dict[str, str]]):
    """Render chat interface"""
    st.header("💬 Chat with the Assistant")
    
    # Display chat history
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    return st.chat_input("Tell me about yourself (age, location, occupation, etc.) or ask about schemes")

def render_loading_message():
    """Render loading message"""
    return st.spinner("🤖 Processing your request...")

def render_error_message(error_type: str, message: str = ""):
    """Render error messages"""
    if error_type == "no_api_key":
        st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
    elif error_type == "no_schemes_data":
        st.error("⚠️ No schemes data loaded. Please ensure scheme_data.json is in the same directory.")
    elif error_type == "api_error":
        st.error(f"⚠️ API Error: {message}")
    elif error_type == "custom":
        st.error(f"⚠️ {message}")

def render_success_message(message: str):
    """Render success message"""
    st.success(message)

def render_info_message(message: str):
    """Render info message"""
    st.info(message)

def render_sidebar_info(schemes_count: int):
    """Render sidebar information"""
    with st.sidebar:
        st.header("📊 Information")
        
        if schemes_count > 0:
            st.success(f"✅ Loaded {schemes_count} schemes from scheme_data.json")
        
        st.markdown("---")
        st.markdown("**💡 Tips for better results:**")
        st.markdown("""
        - Provide your age and state
        - Mention your occupation
        - Include education level
        - Specify any disabilities
        - Mention income level
        - Include social category if applicable
        """)
        
        st.markdown("---")
        st.markdown("**🔗 Useful Links:**")
        st.markdown("""
        - [India.gov.in](https://www.india.gov.in/)
        - [Digital India](https://digitalindia.gov.in/)
        - [MyGov](https://www.mygov.in/)
        """)

def render_footer():
    """Render application footer"""
    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        <p><strong>Note:</strong> This tool provides information about government schemes. 
        Please verify eligibility and apply through official channels.</p>
        <p>Built with ❤️ for citizens of India</p>
    </div>
    """, unsafe_allow_html=True)

def _render_info_item(label: str, value: str):
    """Helper function to render info items"""
    st.write(f"**{label}:** {value}")

def _render_scheme_links(scheme: Dict[str, Any]):
    """Helper function to render scheme links"""
    links_rendered = False
    
    # Official website
    if scheme.get('Official Website'):
        st.markdown(f"🌐 **Official Website:** [Click here]({scheme['Official Website']})")
        links_rendered = True
    
    # Application form
    if scheme.get('Application Form'):
        st.markdown(f"📝 **Application Form:** [Download]({scheme['Application Form']})")
        links_rendered = True
    
    # Additional links
    for key, value in scheme.items():
        if 'link' in key.lower() and key not in ['Official Website', 'Application Form'] and value:
            link_name = key.replace('_', ' ').title()
            st.markdown(f"🔗 **{link_name}:** [Click here]({value})")
            links_rendered = True
    
    if not links_rendered:
        st.caption("No official links available")

def render_no_results_help():
    """Render help message when no schemes are found"""
    st.markdown("""
    ### 🤔 No schemes found? Here's what you can do:
    
    **Provide more details about yourself:**
    - Your age and state/location
    - Your occupation (student, farmer, unemployed, etc.)
    - Education level
    - Any disabilities or special circumstances
    - Income level or BPL/APL status
    - Social category (SC, ST, OBC, if applicable)
    
    **Example messages:**
    - "I am a 25-year-old farmer from Maharashtra with 2 acres of land"
    - "I am a female student from Kerala pursuing graduation"
    - "I am unemployed, belong to SC category, and live in Rajasthan"
    """)

def create_profile_progress_indicator(user_profile: Dict[str, Any]) -> str:
    """Create a profile completion progress indicator"""
    essential_fields = ['age', 'state', 'occupation', 'gender']
    optional_fields = ['category', 'education', 'income', 'disability', 'family_size', 'land_holding']
    
    essential_filled = sum(1 for field in essential_fields if user_profile.get(field))
    optional_filled = sum(1 for field in optional_fields if user_profile.get(field))
    
    total_essential = len(essential_fields)
    total_optional = len(optional_fields)
    
    essential_percentage = (essential_filled / total_essential) * 100
    optional_percentage = (optional_filled / total_optional) * 100
    
    return f"""
    **Profile Completion:**
    - Essential fields: {essential_filled}/{total_essential} ({essential_percentage:.0f}%)
    - Additional fields: {optional_filled}/{total_optional} ({optional_percentage:.0f}%)
    """