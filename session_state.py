import streamlit as st
import pandas as pd
from datetime import datetime

# Move constants here
IMPLEMENTATION_TYPES = {
    "Resource": ["Rebadge", "House Resources", "New Hire"],
    "Technology": ["Internal Build Costs"]
}

def init_session_state():
    """Initialize session state with default values"""
    if 'records' not in st.session_state:
        st.session_state.records = []
    
    if 'changes' not in st.session_state:
        st.session_state.changes = []
    
    if 'implementation_costs' not in st.session_state:
        st.session_state.implementation_costs = {}
    
    if 'assumptions' not in st.session_state:
        st.session_state.assumptions = {
            'Business A': {
                'Onshore': 100000.0,
                'Offshore': 40000.0,
                'Implementation': {
                    'Rebadge': 15000.0,
                    'House Resources': 20000.0,
                    'New Hire': 25000.0
                }
            },
            'Business B': {
                'Onshore': 90000.0,
                'Offshore': 35000.0,
                'Implementation': {
                    'Rebadge': 12000.0,
                    'House Resources': 18000.0,
                    'New Hire': 22000.0
                }
            }
        }

    # Initialize trigger rerun if not present
    if 'trigger_rerun' not in st.session_state:
        st.session_state.trigger_rerun = False

    # Add a deletion tracker
    if 'pending_deletions' not in st.session_state:
        st.session_state.pending_deletions = set()

    # Add a function to track the last modification time
    if 'last_modified' not in st.session_state:
        st.session_state.last_modified = datetime.now()

    # Initialize table data for each business and category if not present
    for business in ["Business A", "Business B"]:
        for category in ["Resource", "Technology"]:
            table_key = f"{business}_{category}_table"
            if table_key not in st.session_state:
                # Create default rows
                rows = []
                
                # Create a row for each implementation type
                for impl_type in IMPLEMENTATION_TYPES[category]:
                    row = {
                        'Description': 'No description added',
                        'Implementation Type': impl_type,
                    }
                    
                    if category == "Resource":
                        row['Salary'] = 0
                    
                    # Add year columns with zero values
                    for year in range(1, 6):
                        row[f'Year {year}'] = 0
                    
                    rows.append(row)
                
                # Add empty row for new entries
                empty_row = {
                    'Description': 'No description added',
                    'Implementation Type': IMPLEMENTATION_TYPES[category][0],
                    **({'Salary': 0} if category == "Resource" else {}),
                    **{f'Year {i+1}': 0 for i in range(5)}
                }
                rows.append(empty_row)
                
                st.session_state[table_key] = pd.DataFrame(rows)

    # Initialize business names if not exists
    if 'business_names' not in st.session_state:
        st.session_state.business_names = {
            'Business A': 'Business A',
            'Business B': 'Business B'
        }

    # Initialize functions if not exists (note the uppercase FUNCTIONS)
    if 'FUNCTIONS' not in st.session_state:
        st.session_state.FUNCTIONS = ["Development", "Testing", "Support"]