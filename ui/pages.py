import requests
import streamlit as st
import json
import os
from typing import Dict, List, Any, Optional
import google.generativeai as genai

# ============================================================================
# UTILITY FUNCTIONS (inline to avoid import issues)
# ============================================================================

def load_schemes_data(file_path: str = "data/scheme_data.json") -> List[Dict]:
    """Load schemes data from JSON file, always returning a flat list of dicts."""
    import os
    st.write(f"[DEBUG] Current working directory: {os.getcwd()}")
    st.write(f"[DEBUG] Looking for file: {file_path}")
    st.write(f"[DEBUG] Absolute path: {os.path.abspath(file_path)}")
    st.write(f"[DEBUG] File exists: {os.path.exists(file_path)}")
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Always flatten to a single list of dicts
                result = []
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list):
                            result.extend(item)
                        elif isinstance(item, dict):
                            result.append(item)
                    st.write(f"[DEBUG] Loaded {len(result)} schemes (flattened) from {file_path}")
                    return result
                else:
                    st.error(f"[DEBUG] Data is not a list. Type: {type(data)}")
                    return []
        else:
            st.error(f"Schemes data file not found at: {os.path.abspath(file_path)}")
            return []
    except Exception as e:
        st.error(f"[DEBUG] Error loading schemes data: {str(e)}")
        return []

def extract_user_profile(user_input: str, current_profile: Dict, api_key: str) -> Dict:
    """Extract user profile information from input text"""
    st.write(f"[DEBUG] extract_user_profile called with user_input: {user_input}")
    st.write(f"[DEBUG] Current profile: {current_profile}")
    st.write(f"[DEBUG] API key present: {bool(api_key)}")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Extract user profile information from this text: "{user_input}"
        Current profile: {current_profile}
        Extract and return ONLY the following fields in JSON format:
        {{
            "age": number or 0,
            "state": "string",
            "occupation": "string", 
            "education": "string",
            "gender": "string",
            "category": "string (General/OBC/SC/ST/Minority)",
            "income": "string",
            "disability": "string",
            "family_size": number or 0,
            "land_holding": number or 0
        }}
        Rules:
        - Only update fields that are explicitly mentioned
        - Keep existing values for fields not mentioned
        - Use 0 for numeric fields if not specified
        - Use empty string for text fields if not specified
        """
        st.write(f"[DEBUG] Prompt sent to Gemini: {prompt}")
        response = model.generate_content(prompt)
        # Always print the raw response, even if it's None or not as expected
        st.write(f"[DEBUG] Gemini raw response: {getattr(response, 'text', str(response))}")
        try:
            import re
            match = re.search(r'\{.*\}', getattr(response, 'text', ''), re.DOTALL)
            if match:
                json_str = match.group(0)
                extracted_data = json.loads(json_str)
            else:
                st.error("[DEBUG] No JSON object found in Gemini response.")
                return current_profile
            updated_profile = current_profile.copy()
            for key, value in extracted_data.items():
                if value and value != 0 and value != "":
                    updated_profile[key] = value
            return updated_profile
        except Exception as e:
            st.error(f"[DEBUG] Failed to decode Gemini response as JSON. Error: {e}. Raw response: {getattr(response, 'text', str(response))}")
            return current_profile
    except Exception as e:
        st.error(f"[DEBUG] Error extracting profile: {str(e)}")
        return current_profile

def find_eligible_schemes(user_profile: Dict, schemes_data: List[Dict], api_key: str) -> List[Dict]:
    """Find schemes eligible for the user with debug output for Gemini responses."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        eligible_schemes = []
        for scheme in schemes_data[:50]:  # Limit to avoid API limits
            prompt = f"""
            User Profile: {user_profile}
            Scheme: {scheme.get('scheme_name', '')}
            Category: {scheme.get('category', '')}
            State: {scheme.get('state', '')}
            Target: {scheme.get('target_beneficiaries', '')}
            Description: {scheme.get('brief_description', '')}
            Rate compatibility (0-100) and explain why this user is eligible.
            Respond in JSON format:
            {{
                "score": number,
                "explanation": "brief explanation"
            }}
            """
            try:
                response = model.generate_content(prompt)
                st.write(f"[DEBUG] Gemini scheme response for '{scheme.get('scheme_name', '')}': {getattr(response, 'text', str(response))}")
                import re
                match = re.search(r'\{.*\}', getattr(response, 'text', ''), re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                else:
                    continue
                if result.get('score', 0) >= 40:  # Threshold for eligibility
                    eligible_schemes.append({
                        'scheme_name': scheme.get('scheme_name', ''),
                        'matching_score': result.get('score', 0),
                        'eligibility_explanation': result.get('explanation', ''),
                        'scheme_details': scheme
                    })
            except Exception as e:
                st.write(f"[DEBUG] Error parsing Gemini response for '{scheme.get('scheme_name', '')}': {e}")
                continue
        eligible_schemes.sort(key=lambda x: x['matching_score'], reverse=True)
        return eligible_schemes[:20]  # Return top 20
    except Exception as e:
        st.error(f"Error finding eligible schemes: {str(e)}")
        return []

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables with file-based schemes_data loading."""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'schemes_data' not in st.session_state:
        st.session_state.schemes_data = load_schemes_data()
    if 'last_eligible_schemes' not in st.session_state:
        st.session_state.last_eligible_schemes = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'display_preferences' not in st.session_state:
        st.session_state.display_preferences = {
            'show_scores': True,
            'show_explanations': True,
            'compact_view': False
        }

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def render_schemes_list(eligible_schemes: List[Dict]):
    """Render list of eligible schemes"""
    if not eligible_schemes:
        st.warning("No eligible schemes found.")
        return
    
    for i, scheme_info in enumerate(eligible_schemes, 1):
        scheme = scheme_info['scheme_details']
        
        with st.expander(
            f"#{i} {scheme.get('scheme_name', 'Unknown Scheme')} "
            f"(Match: {scheme_info['matching_score']}%)",
            expanded=(i == 1)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {scheme.get('category', 'N/A')}")
                st.write(f"**State:** {scheme.get('state', 'N/A')}")
                st.write(f"**Level:** {scheme.get('level', 'N/A')}")
            
            with col2:
                st.write(f"**Target:** {scheme.get('target_beneficiaries', 'N/A')}")
                st.write(f"**Ministry:** {scheme.get('ministry', 'N/A')}")
            
            if st.session_state.display_preferences.get('show_explanations', True):
                st.write(f"**Why you're eligible:** {scheme_info['eligibility_explanation']}")
            
            st.write(f"**Description:** {scheme.get('brief_description', 'N/A')}")
            
            if scheme.get('Official Website'):
                st.markdown(f"🌐 [Official Website]({scheme['Official Website']})")
            
            if scheme.get('tags'):
                tags = [tag.strip() for tag in scheme.get('tags', '').split(',')]
                st.write(f"**Tags:** {', '.join(tags)}")

def render_main_page():
    """Render the main chat interface"""
    # Removed duplicate heading, only the green heading with robot emoji will be shown from main.py
    # Instructions
    with st.expander("📖 How to use this chatbot"):
        st.markdown("""
**📌 Age, gender, and state**

**💼 Occupation and education**

**♿ Special circumstances (e.g., disability, minority status)**

**👨‍👩‍👧‍👦 Family and financial background**

**🤖 The bot will understand your profile and match you with suitable government schemes.**

**🗣️ Example: I am a 22-year-old woman from Rajasthan, currently studying in college.**
""")

    # Initialize session state
    initialize_session_state()
    
    # API Key input in sidebar
    with st.sidebar:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        if not st.session_state.api_key:
            st.error("Please enter your Gemini API key to continue.")
            st.markdown("[Get API Key](https://makersuite.google.com/)")
            
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Tell me about yourself to find relevant schemes..."):
        _process_user_input(prompt)
        st.rerun()

def render_schemes_page(eligible_schemes: List[Dict]):
    """Render the schemes results page"""
    st.header("🎯 Your Eligible Schemes")
    
    if not eligible_schemes:
        st.info("No eligible schemes found yet. Please chat with the assistant to build your profile.")
        return
    
    st.success(f"Found {len(eligible_schemes)} schemes you might be eligible for!")
    render_schemes_list(eligible_schemes)

def render_profile_page():
    """Render the user profile page"""
    import streamlit as st
    initialize_session_state()
    st.header("👤 Your Profile")
    profile = st.session_state.get('user_profile', {})
    if not profile:
        st.info("No profile data found. Start chatting to build your profile!")
        return
    for key, value in profile.items():
        st.write(f"**{key.replace('_', ' ').title()}:** {value if value else 'N/A'}")

def render_search_page():
    """Render the search/filter page for schemes"""
    st.header("🔍 Search & Filter Schemes")
    
    initialize_session_state()
    
    if not st.session_state.schemes_data:
        st.error("No schemes data loaded. Please check the data file.")
        return

    # Search filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_text = st.text_input("🔍 Search by name or keyword")
        states = ['All States'] + sorted(list(set([scheme.get('state', '') for scheme in st.session_state.schemes_data if scheme.get('state')])))
        selected_state = st.selectbox("📍 Filter by State", states)

    with col2:
        categories = ['All Categories'] + sorted(list(set([scheme.get('category', '') for scheme in st.session_state.schemes_data if scheme.get('category')])))
        selected_category = st.selectbox("📂 Filter by Category", categories)
        
        levels = ['All Levels'] + sorted(list(set([scheme.get('level', '') for scheme in st.session_state.schemes_data if scheme.get('level')])))
        selected_level = st.selectbox("🏛 Filter by Level", levels)

    with col3:
        # Tag-based filtering
        all_tags = []
        for scheme in st.session_state.schemes_data:
            if scheme.get('tags'):
                all_tags.extend([tag.strip() for tag in scheme.get('tags', '').split(',')])
        unique_tags = ['All Tags'] + sorted(list(set([tag for tag in all_tags if tag])))
        selected_tag = st.selectbox("🏷 Filter by Tag", unique_tags)

    # Apply filters
    filtered_schemes = st.session_state.schemes_data.copy()

    if search_text:
        filtered_schemes = [
            scheme for scheme in filtered_schemes
            if search_text.lower() in scheme.get('scheme_name', '').lower() or
                search_text.lower() in scheme.get('brief_description', '').lower() or
                search_text.lower() in scheme.get('tags', '').lower()
        ]

    if selected_state != 'All States':
        filtered_schemes = [
            scheme for scheme in filtered_schemes
            if scheme.get('state', '').lower() == selected_state.lower() or
                'all india' in scheme.get('state', '').lower()
        ]

    if selected_category != 'All Categories':
        filtered_schemes = [
            scheme for scheme in filtered_schemes
            if scheme.get('category', '').lower() == selected_category.lower()
        ]

    if selected_level != 'All Levels':
        filtered_schemes = [
            scheme for scheme in filtered_schemes
            if scheme.get('level', '').lower() == selected_level.lower()
        ]

    if selected_tag != 'All Tags':
        filtered_schemes = [
            scheme for scheme in filtered_schemes
            if selected_tag.lower() in scheme.get('tags', '').lower()
        ]

    # Display results
    st.markdown(f"### 📊 Found {len(filtered_schemes)} schemes")

    if filtered_schemes:
        # Convert to format expected by render_schemes_list
        schemes_for_display = []
        for scheme in filtered_schemes:
            schemes_for_display.append({
                'scheme_name': scheme.get('scheme_name', ''),
                'matching_score': 100,  # Default score for search results
                'eligibility_explanation': 'Search result match',
                'scheme_details': scheme
            })
        
        render_schemes_list(schemes_for_display)
    else:
        st.warning("No schemes match your search criteria. Try adjusting the filters.")

    # Display results
    st.markdown(f"### 📊 Found {len(filtered_schemes)} schemes")

    if filtered_schemes:
        # Convert to format expected by render_schemes_list
        schemes_for_display = []
        for scheme in filtered_schemes:
            schemes_for_display.append({
                'scheme_name': scheme.get('scheme_name', ''),
                'matching_score': 100,  # Default score for search results
                'eligibility_explanation': 'Search result match',
                'scheme_details': scheme
            })
        
        render_schemes_list(schemes_for_display)
    else:
        st.warning("No schemes match your search criteria. Try adjusting the filters.")

def _process_user_input(user_input: str):
    st.write(f"[DEBUG] _process_user_input called with: {user_input}")
    """Process user input and update profile/chat history"""
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Check if API key is available
    if not st.session_state.get('api_key'):
        error_msg = "⚠️ Please enter your Gemini API key in the sidebar first."
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        st.error(error_msg)
        return

    # Check if schemes data is loaded
    if not st.session_state.schemes_data:
        error_msg = "⚠️ No schemes data loaded. Please ensure scheme_data.json is available."
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        st.error(error_msg)
        return

    # Show processing message
    with st.spinner("🤖 Processing your request..."):
        try:
            # Extract profile information
            st.session_state.user_profile = extract_user_profile(
                user_input, st.session_state.user_profile, st.session_state.api_key
            )
            
            # Find eligible schemes
            eligible_schemes = find_eligible_schemes(
                st.session_state.user_profile, 
                st.session_state.schemes_data,
                st.session_state.api_key
            )
            
            # Store eligible schemes for statistics
            st.session_state.last_eligible_schemes = eligible_schemes
            # Generate response
            if eligible_schemes:
                response = f"Great! Based on your profile, I found {len(eligible_schemes)} schemes you might be eligible for."
                st.success(response)
                
                # Show top 3 schemes inline
                st.markdown("### 🎯 Top Matches:")
                for i, scheme_info in enumerate(eligible_schemes[:3], 1):
                    scheme = scheme_info['scheme_details']
                    with st.expander(f"#{i} {scheme['scheme_name']} (Match: {scheme_info['matching_score']}%)", expanded=(i == 1)):
                        st.write(f"**Category:** {scheme.get('category', 'N/A')}")
                        st.write(f"**State:** {scheme.get('state', 'N/A')}")
                        st.write(f"**Why you're eligible:** {scheme_info['eligibility_explanation']}")
                        st.write(f"**Description:** {scheme.get('brief_description', 'N/A')[:200]}...")
                        
                        if scheme.get('Official Website'):
                            st.markdown(f"🌐 [Official Website]({scheme['Official Website']})")
                
                if len(eligible_schemes) > 3:
                    st.info(f"💡 View all {len(eligible_schemes)} schemes in the 'Eligible Schemes' section above.")
                
            else:
                response = """I need more information about you to find suitable schemes. Could you tell me about your:
                
- Age and location (which state/district)
- Occupation (farmer, student, unemployed, business, etc.)
- Education level (10th, 12th, graduate, etc.)
- Social category (General, OBC, SC, ST, Minority)
- Any disabilities or special circumstances
- Income level or BPL/APL status
- Family size and dependents"""
                
                st.info(response)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            error_msg = f"❌ Error processing your request: {str(e)}"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)

def render_about_page():
    """Render the about/help page"""
    st.header("ℹ️ About SevaSaathi")

    st.markdown("""
    ### What is this tool?
    The SevaSaathi is an AI-powered tool that helps Indian citizens find government schemes they may be eligible for based on their personal profile.

    ### How it works:
    1. **Tell us about yourself** - Share your age, location, occupation, education, etc.
    2. **AI analyzes your profile** - Our system matches your details with scheme requirements
    3. **Get personalized results** - See schemes ranked by your eligibility likelihood
    4. **Get official links** - Access direct links to government websites and application forms

    ### Features:
    - 🤖 **AI-Powered Matching**: Uses Google's Gemini AI for intelligent scheme matching
    - 🔒 **Privacy First**: Your data stays in your session and is not stored permanently
    - 📊 **Smart Scoring**: Schemes are ranked by compatibility with your profile
    - 🌐 **Official Sources**: Direct links to government websites and application forms
    - 💬 **Chat Interface**: Natural conversation to build your profile

    ### Tips for better results:
    - Be specific about your location (state/district)
    - Mention your occupation clearly (farmer, student, unemployed, etc.)
    - Include education level and social category if applicable
    - Share any disabilities or special circumstances
    - Mention family size and income level
    """)

    st.markdown("---")

    st.markdown("""
    ### Disclaimer:
    - This tool provides information about government schemes but doesn't guarantee eligibility
    - Always verify eligibility criteria on official government websites
    - Apply through official channels only - avoid middlemen
    - Scheme information is based on available data and may not be completely up-to-date
    - The AI provides suggestions based on pattern matching, not legal advice
    """)

def render_statistics_page():
    """Render statistics and analytics page"""
    st.header("📊 Schemes Statistics & Analytics")
    
    initialize_session_state()

    if not st.session_state.schemes_data:
        st.error("No schemes data loaded.")
        return

    schemes_data = st.session_state.schemes_data

    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Schemes", len(schemes_data))

    with col2:
        states = set(scheme.get('state', '') for scheme in schemes_data if scheme.get('state'))
        st.metric("States Covered", len(states))

    with col3:
        categories = set(scheme.get('category', '') for scheme in schemes_data if scheme.get('category'))
        st.metric("Categories", len(categories))

    with col4:
        if st.session_state.user_profile:
            eligible_count = len(st.session_state.get('last_eligible_schemes', []))
            st.metric("Your Eligible Schemes", eligible_count)
        else:
            st.metric("Build Profile", "to see eligible schemes")

    # Charts and visualizations
    st.markdown("### 📈 Distribution Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # State-wise distribution
        state_counts = {}
        for scheme in schemes_data:
            state = scheme.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        if state_counts:
            st.markdown("**Schemes by State:**")
            for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                st.write(f"• {state}: {count} schemes")

    with col2:
        # Category-wise distribution
        category_counts = {}
        for scheme in schemes_data:
            category = scheme.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            st.markdown("**Schemes by Category:**")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                st.write(f"• {category}: {count} schemes")

def render_settings_page():
    """Render application settings page"""
    st.header("⚙️ Settings & Preferences")
    
    initialize_session_state()

    # API Configuration
    st.markdown("### 🔑 API Configuration")

    current_api_key = st.session_state.get('api_key', '')
    if current_api_key:
        masked_key = current_api_key[:8] + "..." + current_api_key[-4:] if len(current_api_key) > 12 else current_api_key
        st.success(f"✅ API Key configured: {masked_key}")
        
        if st.button("🔄 Update API Key"):
            st.session_state.show_api_input = True
    else:
        st.warning("⚠️ No API Key configured")
        st.session_state.show_api_input = True

    if st.session_state.get('show_api_input', False):
            
        new_api_key = st.text_input("Enter new Gemini API Key:", type="password") 
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Key"):
                if new_api_key:
                    st.session_state.api_key = new_api_key
                    st.session_state.show_api_input = False
                    st.success("API Key updated!")
                    st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_api_input = False
                st.rerun()

    # Data Management
    st.markdown("### 📊 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Schemes Database:**")
        if st.session_state.schemes_data:
            st.success(f"✅ {len(st.session_state.schemes_data)} schemes loaded")
        else:
            st.error("❌ No schemes data loaded")
            if st.button("🔄 Reload Schemes Data"):
                st.session_state.schemes_data = load_schemes_data()
                st.rerun()

    with col2:
        st.markdown("**User Profile:**")
        if st.session_state.user_profile:
            profile_items = len([v for v in st.session_state.user_profile.values() if v])
            st.info(f"📝 {profile_items} profile fields filled")
        else:
            st.warning("📝 No profile data")

    # Session Management
    st.markdown("### 🗑️ Session Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear Profile Only"):
            st.session_state.user_profile = {}
            st.success("Profile cleared!")
            st.rerun()

    with col2:
        if st.button("💬 Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()

    with col3:
        if st.button("🔄 Reset Everything"):
            # Clear all session state except schemes data and API key
            api_key_backup = st.session_state.get('api_key', '')
            schemes_backup = st.session_state.schemes_data
            st.session_state.clear()
            st.session_state.api_key = api_key_backup
            st.session_state.schemes_data = schemes_backup
            st.session_state.user_profile = {}
            st.session_state.chat_history = []
            st.success("Session reset!")
            st.rerun()

# Helper function to handle navigation
def handle_page_navigation():
    """Handle page navigation and routing"""
    page = st.session_state.get('current_page', 'main')

    if page == 'main':
        render_main_page()
    elif page == 'schemes':
        eligible_schemes = st.session_state.get('last_eligible_schemes', [])
        render_schemes_page(eligible_schemes)
    elif page == 'profile':
        render_profile_page()
    elif page == 'search':
        render_search_page()
    elif page == 'about':
        render_about_page()
    elif page == 'statistics':
        render_statistics_page()
    elif page == 'settings':
        render_settings_page()
    else:
        render_main_page()  # Default fallback
