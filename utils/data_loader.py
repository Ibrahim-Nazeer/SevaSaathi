"""
Data loading utilities for SevaSaathi
"""
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Class to handle loading and processing of schemes data"""
    
    def __init__(self):  # Fixed: was _init_ instead of __init__
        self.schemes_data = None
        self.schemes_df = None
    
    @st.cache_data
    def load_schemes_data(_self, file_path: str = "data/scheme_data.json") -> List[Dict]:
        """
        Load government schemes data from JSON file
        
        Args:
            file_path: Path to the JSON file containing schemes data
            
        Returns:
            List of scheme dictionaries
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    _self.schemes_data = json.load(file)
                    logger.info(f"Successfully loaded {len(_self.schemes_data)} schemes from {file_path}")
                    return _self.schemes_data
            else:
                error_msg = f"Schemes data file not found at: {file_path}"
                logger.error(error_msg)
                st.error(error_msg)
                return []
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return []
        except Exception as e:
            error_msg = f"Error loading schemes data: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return []
    
    def prepare_schemes_dataframe(self, schemes_data: List[Dict]) -> pd.DataFrame:
        """
        Convert schemes data to pandas DataFrame for easier processing
        
        Args:
            schemes_data: List of scheme dictionaries
            
        Returns:
            DataFrame with schemes data
        """
        if not schemes_data:
            logger.warning("No schemes data provided for DataFrame preparation")
            return pd.DataFrame()
        
        try:
            # Flatten the data structure for DataFrame
            flattened_data = []
            for scheme in schemes_data:
                flat_scheme = {
                    'name': scheme.get('name', ''),
                    'category': scheme.get('category', ''),
                    'description': scheme.get('description', ''),
                    'eligibility': self._list_to_string(scheme.get('eligibility', [])),
                    'benefits': self._list_to_string(scheme.get('benefits', [])),
                    'application_process': self._list_to_string(scheme.get('application_process', [])),
                    'documents_required': self._list_to_string(scheme.get('documents_required', [])),
                    'official_website': scheme.get('official_website', ''),
                    'target_audience': self._list_to_string(scheme.get('target_audience', []))
                }
                flattened_data.append(flat_scheme)
            
            self.schemes_df = pd.DataFrame(flattened_data)
            logger.info(f"Successfully created DataFrame with {len(self.schemes_df)} schemes")
            return self.schemes_df
        except Exception as e:
            error_msg = f"Error preparing DataFrame: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return pd.DataFrame()
    
    def _list_to_string(self, list_data: Any) -> str:
        """
        Convert list to string safely
        
        Args:
            list_data: Data to convert to string
            
        Returns:
            String representation of the data
        """
        if isinstance(list_data, list):
            return ' | '.join(str(item) for item in list_data if item)
        return str(list_data) if list_data else ''
    
    def filter_schemes_by_category(self, category: str) -> List[Dict]:
        """
        Filter schemes by category
        
        Args:
            category: Category to filter by
            
        Returns:
            Filtered list of schemes
        """
        if not self.schemes_data:
            logger.warning("No schemes data available for filtering")
            return []
        
        if category == "All Categories":
            return self.schemes_data
        
        filtered_schemes = [
            scheme for scheme in self.schemes_data 
            if scheme.get('category', '').lower() == category.lower()
        ]
        
        logger.info(f"Filtered {len(filtered_schemes)} schemes for category: {category}")
        return filtered_schemes
    
    def get_scheme_categories(self) -> List[str]:
        """
        Get unique categories from schemes data
        
        Returns:
            List of unique categories
        """
        if not self.schemes_data:
            logger.warning("No schemes data available for categories")
            return []
        
        categories = set()
        for scheme in self.schemes_data:
            category = scheme.get('category')
            if category and category.strip():
                categories.add(category.strip())
        
        categories_list = sorted(list(categories))
        logger.info(f"Found {len(categories_list)} unique categories")
        return categories_list
    
    def search_schemes(self, query: str) -> List[Dict]:
        """
        Search schemes based on query string
        
        Args:
            query: Search query
            
        Returns:
            List of matching schemes
        """
        if not self.schemes_data:
            logger.warning("No schemes data available for search")
            return []
        
        if not query or not query.strip():
            return self.schemes_data
        
        query_lower = query.lower().strip()
        matching_schemes = []
        
        for scheme in self.schemes_data:
            # Search in multiple fields
            searchable_fields = [
                scheme.get('name', ''),
                scheme.get('description', ''),
                scheme.get('category', ''),
                ' '.join(scheme.get('target_audience', [])),
                ' '.join(scheme.get('benefits', [])),
                ' '.join(scheme.get('eligibility', []))
            ]
            
            searchable_text = ' '.join(searchable_fields).lower()
            
            if query_lower in searchable_text:
                matching_schemes.append(scheme)
        
        logger.info(f"Found {len(matching_schemes)} schemes matching query: '{query}'")
        return matching_schemes
    
    def get_scheme_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a specific scheme by name
        
        Args:
            name: Name of the scheme
            
        Returns:
            Scheme dictionary if found, None otherwise
        """
        if not self.schemes_data or not name:
            return None
        
        for scheme in self.schemes_data:
            if scheme.get('name', '').lower() == name.lower():
                return scheme
        
        return None

# Standalone functions for backward compatibility and easy import

def initialize_session_state():
    """
    Initialize Streamlit session state variables
    """
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    if 'schemes_data' not in st.session_state:
        st.session_state.schemes_data = []
    
    if 'schemes_df' not in st.session_state:
        st.session_state.schemes_df = pd.DataFrame()
    
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All Categories"
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    logger.info("Session state initialized successfully")

def load_schemes_data(file_path: str = "data/scheme_data.json") -> List[Dict]:
    """
    Standalone function to load schemes data
    
    Args:
        file_path: Path to the JSON file containing schemes data
        
    Returns:
        List of scheme dictionaries
    """
    # Initialize session state if not already done
    if 'data_loader' not in st.session_state:
        initialize_session_state()
    
    # Load data using the DataLoader instance
    schemes_data = st.session_state.data_loader.load_schemes_data(file_path)
    
    # Update session state
    st.session_state.schemes_data = schemes_data
    if schemes_data:
        st.session_state.schemes_df = st.session_state.data_loader.prepare_schemes_dataframe(schemes_data)
    
    return schemes_data

def get_categories() -> List[str]:
    """
    Get available scheme categories
    
    Returns:
        List of categories
    """
    if 'data_loader' not in st.session_state:
        initialize_session_state()
    
    return st.session_state.data_loader.get_scheme_categories()

def search_schemes_by_query(query: str) -> List[Dict]:
    """
    Search schemes by query
    
    Args:
        query: Search query
        
    Returns:
        List of matching schemes
    """
    if 'data_loader' not in st.session_state:
        initialize_session_state()
    
    return st.session_state.data_loader.search_schemes(query)

def filter_schemes_by_category(category: str) -> List[Dict]:
    """
    Filter schemes by category
    
    Args:
        category: Category to filter by
        
    Returns:
        Filtered list of schemes
    """
    if 'data_loader' not in st.session_state:
        initialize_session_state()
    
    return st.session_state.data_loader.filter_schemes_by_category(category)