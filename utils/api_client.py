import requests
import json
import streamlit as st
from typing import Optional


class GeminiClient:
    """Client for interacting with Gemini 1.5 Flash API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.headers = {"Content-Type": "application/json"}
        self.generation_config = {
            "temperature": 0.3,
            "topP": 0.8,
            "topK": 20,
            "maxOutputTokens": 1024
        }
        self.safety_settings = [
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
    
    def call_api(self, prompt: str) -> str:
        """Make API call to Gemini"""
        url = f"{self.base_url}?key={self.api_key}"
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": self.generation_config,
            "safetySettings": self.safety_settings
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        return candidate['content']['parts'][0]['text']
                    else:
                        return "No content generated"
                else:
                    return "No candidates in response"
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                st.error(error_msg)
                return f"API Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return "Request timeout"
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Please check your internet connection.")
            return "Connection error"
        except requests.exceptions.RequestException as e:
            st.error(f"Request error: {str(e)}")
            return f"Request error: {str(e)}"
        except json.JSONDecodeError:
            st.error("Invalid JSON response from API")
            return "Invalid JSON response"
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"