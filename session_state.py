import streamlit as st
import pandas as pd
from datetime import datetime

def init_session_state():
    """Initialize all session state variables"""
    
    # Initialize implementation costs if not present
    if 'implementation_costs' not in st.session_state:
        st.session_state.implementation_costs = {}

    # Initialize records if not present
    if 'records' not in st.session_state:
        st.session_state.records = [
            # Business A Resources
            {
                'id': 0,
                'business': 'Business A',
                'category': 'Resource',
                'functions': ['Development', 'Testing'],
                'function_descriptions': {
                    'Development': 'Core development work',
                    'Testing': 'Unit testing responsibilities'
                },
                'tech_name': None,
                'location': 'Onshore',
                'count': 10,
                'unit_cost': 100000,
                'total_cost': 1000000,
                'comments': 'Core development team',
                'timestamp': '2024-01-01T00:00:00'
            }
        ]

    # Initialize changes if not present
    if 'changes' not in st.session_state:
        st.session_state.changes = []

    # Initialize assumptions if not present
    if 'assumptions' not in st.session_state:
        st.session_state.assumptions = {
            'Business A': {
                'Onshore': 100000,
                'Offshore': 40000,
                'Implementation': {
                    'Rebadge': 5000,
                    'House Resources': 10000,
                    'New Hire': 15000,
                    'Internal Build Costs': 0
                }
            },
            'Business B': {
                'Onshore': 100000,
                'Offshore': 40000,
                'Implementation': {
                    'Rebadge': 5000,
                    'House Resources': 10000,
                    'New Hire': 15000,
                    'Internal Build Costs': 0
                }
            }
        }