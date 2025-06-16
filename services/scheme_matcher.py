import json
from typing import List, Dict, Any, Tuple

from utils.api_client import api_client
from utils.data_loader import get_schemes_summary
from config.settings import PAGE_CONFIG, MATCHING_SCORES

class SchemeMatcher:
    """Handle scheme matching and eligibility analysis"""
    
    def __init__(self):
        self.max_schemes_to_process = PAGE_CONFIG["max_schemes_to_process"]
        self.minimum_score = MATCHING_SCORES["minimum_score_threshold"]
        self.simple_matching_threshold = MATCHING_SCORES["simple_matching_threshold"]
    
    def find_eligible_schemes(self, user_profile: Dict[str, Any], schemes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find eligible schemes based on user profile
        
        Args:
            user_profile (Dict): User's profile information
            schemes_data (List[Dict]): Available schemes data
            
        Returns:
            List[Dict]: List of eligible schemes with scores
        """
        if not user_profile or not api_client.is_configured():
            return self._simple_scheme_matching(user_profile, schemes_data)
        
        # Get schemes summary for API processing
        schemes_summary = get_schemes_summary(schemes_data, self.max_schemes_to_process)
        
        # Use AI-powered matching
        ai_results = self._ai_scheme_matching(user_profile, schemes_summary, schemes_data)
        
        # Fallback to simple matching if AI fails
        if not ai_results:
            return self._simple_scheme_matching(user_profile, schemes_data)
        
        return ai_results
    
    def _ai_scheme_matching(self, user_profile: Dict[str, Any], schemes_summary: List[Dict[str, Any]], full_schemes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """AI-powered scheme matching using Gemini API"""
        prompt = self._build_matching_prompt(user_profile, schemes_summary)
        response = api_client.generate_content(prompt)
        
        if self._is_error_response(response):
            return []
        
        return self._parse_matching_response(response, full_schemes_data)
    
    def _build_matching_prompt(self, user_profile: Dict[str, Any], schemes_summary: List[Dict[str, Any]]) -> str:
        """Build the prompt for AI scheme matching"""
        return f"""
        You are an expert in Indian government schemes. Analyze user eligibility for schemes.
        
        User Profile: {json.dumps(user_profile, indent=2)}
        
        Schemes to analyze: {json.dumps(schemes_summary, indent=2)}
        
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
        - State match: +{MATCHING_SCORES["state_match"]} points
        - Primary target match (student/farmer/women/disabled): +{MATCHING_SCORES["primary_target_match"]} points
        - Category match: +{MATCHING_SCORES["category_match"]} points
        - Age appropriateness: +{MATCHING_SCORES["age_appropriateness"]} points
        - Additional criteria: +{MATCHING_SCORES["additional_criteria"]} points each
        
        Return ONLY a JSON array. No explanatory text:
        [
            {{
                "scheme_name": "exact scheme name",
                "matching_score": 75,
                "reasons": ["State eligibility", "Student benefits", "Age appropriate"]
            }}
        ]
        
        Only include schemes with score >= {self.minimum_score}. Maximum 10 schemes.
        """
    
    def _parse_matching_response(self, response: str, full_schemes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse AI matching response and match with full scheme data"""
        # Clean the response to extract JSON
        response_text = response.strip()
        if response_text.startswith('json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
        
        try:
            eligible_schemes_summary = json.loads(response_text)
            
            if not isinstance(eligible_schemes_summary, list):
                return []
            
            # Match summary back to full scheme details
            eligible_schemes = []
            for summary in eligible_schemes_summary:
                if not isinstance(summary, dict):
                    continue
                
                scheme_name = summary.get("scheme_name", "")
                matching_scheme = self._find_scheme_by_name(scheme_name, full_schemes_data)
                
                if matching_scheme:
                    eligible_schemes.append({
                        "scheme_name": scheme_name,
                        "matching_score": min(summary.get("matching_score", 50), 100),
                        "eligibility_explanation": "; ".join(summary.get("reasons", ["General match"])),
                        "scheme_details": matching_scheme
                    })
            
            return sorted(eligible_schemes, key=lambda x: x['matching_score'], reverse=True)
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
    
    def _find_scheme_by_name(self, scheme_name: str, schemes_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find a scheme by its name in the full schemes data"""
        for scheme in schemes_data:
            if scheme.get("scheme_name") == scheme_name:
                return scheme
        return None
    
    def _simple_scheme_matching(self, user_profile: Dict[str, Any], schemes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple fallback matching when AI is not available"""
        eligible_schemes = []
        
        for scheme in schemes_data:
            score, explanations = self._calculate_simple_score(user_profile, scheme)
            
            if score >= self.simple_matching_threshold:
                eligible_schemes.append({
                    "scheme_name": scheme['scheme_name'],
                    "matching_score": min(score, 100),
                    "eligibility_explanation": "; ".join(explanations) if explanations else "General eligibility match",
                    "scheme_details": scheme
                })
        
        return sorted(eligible_schemes, key=lambda x: x['matching_score'], reverse=True)
    
    def _calculate_simple_score(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> Tuple[int, List[str]]:
        """Calculate matching score for simple matching algorithm"""
        score = 0
        explanations = []
        
        # State matching
        user_state = user_profile.get('state', '').lower()
        scheme_state = scheme.get('state', '').lower()
        if self._is_state_match(user_state, scheme_state):
            score += MATCHING_SCORES["state_match"]
            if user_state:
                explanations.append("State eligibility matched")
        
        # Disability matching
        if self._is_disability_match(user_profile, scheme):
            score += MATCHING_SCORES["primary_target_match"]
            explanations.append("Disability benefits available")
        
        # Occupation matching
        occupation_score, occupation_explanation = self._get_occupation_match(user_profile, scheme)
        score += occupation_score
        if occupation_explanation:
            explanations.append(occupation_explanation)
        
        # Gender matching
        if self._is_gender_match(user_profile, scheme):
            score += MATCHING_SCORES["category_match"]
            explanations.append("Women/Girl focused scheme")
        
        # Age matching
        if self._is_age_appropriate(user_profile, scheme):
            score += MATCHING_SCORES["age_appropriateness"]
            explanations.append("Age appropriate for education scheme")
        
        # Category matching
        if self._is_category_match(user_profile, scheme):
            score += MATCHING_SCORES["category_match"]
            explanations.append("Social category benefits")
        
        return score, explanations
    
    def _is_state_match(self, user_state: str, scheme_state: str) -> bool:
        """Check if user's state matches scheme's state"""
        if not user_state:
            return True
        return (scheme_state == 'all india' or 
                'all states' in scheme_state or 
                user_state in scheme_state)
    
    def _is_disability_match(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> bool:
        """Check if scheme matches user's disability status"""
        if not user_profile.get('disability'):
            return False
        
        tags = scheme.get('tags', '').lower()
        eligibility = scheme.get('eligibility_criteria', '').lower()
        
        disability_keywords = ['disabled', 'pwd', 'disability', 'handicapped']
        return (any(word in tags for word in disability_keywords) or 
                any(word in eligibility for word in disability_keywords))
    
    def _get_occupation_match(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> Tuple[int, str]:
        """Get occupation matching score and explanation"""
        occupation = user_profile.get('occupation', '').lower()
        if not occupation:
            return 0, ""
        
        tags = scheme.get('tags', '').lower()
        
        if occupation == 'farmer' and ('farmer' in tags or 'agriculture' in tags):
            return MATCHING_SCORES["primary_target_match"], "Farmer/Agriculture scheme"
        elif occupation == 'student' and ('student' in tags or 'education' in tags):
            return MATCHING_SCORES["primary_target_match"], "Student/Education scheme"
        elif occupation == 'unemployed' and ('employment' in tags or 'job' in tags):
            return MATCHING_SCORES["additional_criteria"], "Employment scheme"
        
        return 0, ""
    
    def _is_gender_match(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> bool:
        """Check if scheme matches user's gender"""
        gender = user_profile.get('gender', '').lower()
        if gender != 'female':
            return False
        
        tags = scheme.get('tags', '').lower()
        return any(word in tags for word in ['women', 'girl', 'female', 'mahila'])
    
    def _is_age_appropriate(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> bool:
        """Check if user's age is appropriate for the scheme"""
        age = user_profile.get('age')
        if not age or not isinstance(age, (int, float)):
            return False
        
        tags = scheme.get('tags', '').lower()
        
        # Age appropriate for education schemes
        if age <= 25 and ('student' in tags or 'education' in tags):
            return True
        
        # Age appropriate for senior citizen schemes
        if age >= 60 and ('senior' in tags or 'elderly' in tags):
            return True
        
        return False
    
    def _is_category_match(self, user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> bool:
        """Check if scheme matches user's social category"""
        category = user_profile.get('category', '').upper()
        if category not in ['SC', 'ST', 'OBC']:
            return False
        
        tags = scheme.get('tags', '').upper()
        eligibility = scheme.get('eligibility_criteria', '').upper()
        
        category_keywords = ['SC', 'ST', 'OBC', 'MINORITY', 'SCHEDULED CASTE', 'SCHEDULED TRIBE']
        return (any(keyword in tags for keyword in category_keywords) or
                any(keyword in eligibility for keyword in category_keywords))
    
    def _is_error_response(self, response: str) -> bool:
        """Check if the API response indicates an error"""
        if not response:
            return True
        
        error_indicators = ['error', 'timeout', 'connection error', 'api error']
        return any(indicator in response.lower() for indicator in error_indicators)

# Create a singleton instance
scheme_matcher = SchemeMatcher()