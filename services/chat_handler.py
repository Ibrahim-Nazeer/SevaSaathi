"""
Chat handling service for SevaSaathi
"""
import streamlit as st
from typing import List, Dict, Any
from utils.api_client import GeminiAPIClient
from utils.data_loader import DataLoader
from ui.components import UIComponents

class ChatHandler:
    """Handle chat interactions and AI responses"""
    
    def __init__(self, api_client: GeminiAPIClient, data_loader: DataLoader):
        self.api_client = api_client
        self.data_loader = data_loader
        self.ui_components = UIComponents()
    
    def initialize_chat_history(self):
        """Initialize chat history in session state"""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "schemes_context" not in st.session_state:
            st.session_state.schemes_context = ""
    
    def prepare_schemes_context(self, schemes_data: List[Dict]) -> str:
        """
        Prepare schemes data as context for the AI
        
        Args:
            schemes_data: List of scheme dictionaries
            
        Returns:
            Formatted context string
        """
        if not schemes_data:
            return "No schemes data available."
        
        context = "Available Government Schemes Information:\n\n"
        
        for i, scheme in enumerate(schemes_data[:20], 1):  # Limit to first 20 schemes
            context += f"{i}. **{scheme.get('name', 'Unknown')}**\n"
            context += f"   Category: {scheme.get('category', 'Not specified')}\n"
            context += f"   Description: {scheme.get('description', 'No description')}\n"
            
            if scheme.get('target_audience'):
                context += f"   Target Audience: {', '.join(scheme['target_audience'])}\n"
            
            if scheme.get('eligibility'):
                context += f"   Eligibility: {', '.join(scheme['eligibility'][:3])}...\n"
            
            if scheme.get('benefits'):
                context += f"   Benefits: {', '.join(scheme['benefits'][:3])}...\n"
            
            context += "\n"
        
        if len(schemes_data) > 20:
            context += f"... and {len(schemes_data) - 20} more schemes available.\n"
        
        return context
    
    def create_enhanced_prompt(self, user_question: str, schemes_context: str) -> str:
        """
        Create an enhanced prompt with schemes context
        
        Args:
            user_question: User's question
            schemes_context: Context about available schemes
            
        Returns:
            Enhanced prompt string
        """
        return f"""
You are a helpful SevaSaathi. You have access to information about various government schemes and programs.

Context about available schemes:
{schemes_context}

User Question: {user_question}

Please provide a helpful, accurate, and detailed response about government schemes. If the user is asking about specific schemes, eligibility, benefits, or application processes, use the provided context to give accurate information. If you need to recommend schemes, base your recommendations on the available data.

Guidelines:
1. Be helpful and informative
2. Provide specific scheme names when relevant
3. Include eligibility criteria and benefits when applicable
4. Mention application processes if asked
5. If you don't have specific information, say so clearly
6. Format your response in a clear, easy-to-read manner
7. Use bullet points or numbered lists when appropriate

Response:
"""
    
    def process_chat_message(self, user_input: str, schemes_data: List[Dict]) -> str:
        """
        Process user chat message and generate response
        
        Args:
            user_input: User's input message
            schemes_data: Available schemes data
            
        Returns:
            AI-generated response
        """
        try:
            # Prepare context
            schemes_context = self.prepare_schemes_context(schemes_data)
            
            # Create enhanced prompt
            enhanced_prompt = self.create_enhanced_prompt(user_input, schemes_context)
            
            # Get response from AI
            response = self.api_client.generate_response(enhanced_prompt)
            
            return response
            
        except Exception as e:
            st.error(f"Error processing chat message: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again."
    
    def add_to_chat_history(self, user_message: str, ai_response: str):
        """
        Add messages to chat history
        
        Args:
            user_message: User's message
            ai_response: AI's response
        """
        st.session_state.chat_history.append({
            "user": user_message,
            "assistant": ai_response,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def display_chat_history(self):
        """Display the chat history"""
        if st.session_state.chat_history:
            st.markdown("### 💬 Chat History")
            
            # Display messages in reverse order (newest first)
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    # User message
                    self.ui_components.render_chat_message(chat["user"], is_user=True)
                    
                    # Assistant response
                    self.ui_components.render_chat_message(chat["assistant"], is_user=False)
                    
                    # Separator
                    if i < len(st.session_state.chat_history) - 1:
                        st.markdown("---")
    
    def handle_chat_interface(self, schemes_data: List[Dict]):
        """
        Handle the main chat interface
        
        Args:
            schemes_data: Available schemes data
        """
        self.initialize_chat_history()
        
        # Render chat interface header
        self.ui_components.render_chat_interface()
        
        # Chat input
        user_input = st.text_input(
            "Ask your question:",
            placeholder="e.g., What schemes are available for farmers?",
            key="chat_input"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit_button = st.button("Send 📤", type="primary")
        with col2:
            clear_button = st.button("Clear Chat 🗑️")
        
        # Handle clear chat
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        # Handle submit
        if submit_button and user_input.strip():
            # Show loading spinner
            with st.spinner("Generating response..."):
                # Process the message
                ai_response = self.process_chat_message(user_input, schemes_data)
                
                # Add to history
                self.add_to_chat_history(user_input, ai_response)
                
                # Clear input and rerun
                st.rerun()
        
        # Display chat history
        if st.session_state.chat_history:
            self.display_chat_history()
        else:
            st.markdown("""
            <div style='text-align: center; color: #6B7280; padding: 2rem;'>
                <h4>👋 Welcome! Ask me anything about government schemes.</h4>
                <p>Try questions like:</p>
                <ul style='text-align: left; display: inline-block;'>
                    <li>"What schemes are available for students?"</li>
                    <li>"How do I apply for housing schemes?"</li>
                    <li>"What are the eligibility criteria for farmer schemes?"</li>
                    <li>"Show me healthcare related schemes"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def get_scheme_recommendations(self, user_profile: Dict[str, Any], schemes_data: List[Dict]) -> List[Dict]:
        """
        Get scheme recommendations based on user profile
        
        Args:
            user_profile: User profile information
            schemes_data: Available schemes data
            
        Returns:
            List of recommended schemes
        """
        recommendations = []
        
        # Simple recommendation logic based on user profile
        for scheme in schemes_data:
            score = 0
            
            # Check target audience match
            if scheme.get('target_audience'):
                for audience in scheme['target_audience']:
                    if any(keyword in audience.lower() for keyword in user_profile.get('keywords', [])):
                        score += 2
            
            # Check category match
            if scheme.get('category', '').lower() in [cat.lower() for cat in user_profile.get('interested_categories', [])]:
                score += 3
            
            # Add scheme with score if it has any relevance
            if score > 0:
                scheme_with_score = scheme.copy()
                scheme_with_score['recommendation_score'] = score
                recommendations.append(scheme_with_score)
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        return recommendations[:5]  # Return top 5 recommendations