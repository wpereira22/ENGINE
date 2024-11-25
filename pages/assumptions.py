import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Cost Assumptions", layout="wide")

# Initialize session state for assumptions if not exists
if 'assumptions' not in st.session_state:
    st.session_state.assumptions = {
        'Business A': {
            'Onshore': 100000,
            'Offshore': 40000
        },
        'Business B': {
            'Onshore': 100000,
            'Offshore': 40000
        }
    }

st.title("Cost Assumptions")

# Create tabs for different types of assumptions
tab1, tab2, tab3 = st.tabs(["Resource Costs", "Functions", "Other Assumptions"])

with tab1:
    st.header("Resource Cost Assumptions")
    
    # Create a form for resource costs
    with st.form("resource_costs_form"):
        # Business A costs
        st.subheader("Business A")
        col1, col2 = st.columns(2)
        
        with col1:
            business_a_onshore = st.number_input(
                "Onshore Resource Cost (Annual)",
                min_value=0,
                value=st.session_state.assumptions['Business A']['Onshore'],
                step=1000,
                help="Annual cost per onshore resource for Business A"
            )
        
        with col2:
            business_a_offshore = st.number_input(
                "Offshore Resource Cost (Annual)",
                min_value=0,
                value=st.session_state.assumptions['Business A']['Offshore'],
                step=1000,
                help="Annual cost per offshore resource for Business A"
            )
        
        st.divider()
        
        # Business B costs
        st.subheader("Business B")
        col1, col2 = st.columns(2)
        
        with col1:
            business_b_onshore = st.number_input(
                "Onshore Resource Cost (Annual)",
                min_value=0,
                value=st.session_state.assumptions['Business B']['Onshore'],
                step=1000,
                help="Annual cost per onshore resource for Business B"
            )
        
        with col2:
            business_b_offshore = st.number_input(
                "Offshore Resource Cost (Annual)",
                min_value=0,
                value=st.session_state.assumptions['Business B']['Offshore'],
                step=1000,
                help="Annual cost per offshore resource for Business B"
            )
        
        # Submit button
        if st.form_submit_button("Update Resource Costs"):
            # Update session state
            st.session_state.assumptions['Business A']['Onshore'] = business_a_onshore
            st.session_state.assumptions['Business A']['Offshore'] = business_a_offshore
            st.session_state.assumptions['Business B']['Onshore'] = business_b_onshore
            st.session_state.assumptions['Business B']['Offshore'] = business_b_offshore
            
            # Update existing records with new costs
            for record in st.session_state.records:
                if record['category'] == 'Resource':
                    business = record['business']
                    location = record['location']
                    new_unit_cost = st.session_state.assumptions[business][location]
                    record['unit_cost'] = new_unit_cost
                    record['total_cost'] = new_unit_cost * record['count']
            
            st.success("Resource costs updated successfully!")
            st.rerun()

    # Display current assumptions in a table
    st.subheader("Current Resource Cost Assumptions")
    
    # Create DataFrame for display
    data = []
    for business in ['Business A', 'Business B']:
        for location in ['Onshore', 'Offshore']:
            data.append({
                'Business': business,
                'Location': location,
                'Annual Cost': f"${st.session_state.assumptions[business][location]:,}"
            })
    
    df = pd.DataFrame(data)
    st.dataframe(
        df.style.set_properties(**{
            'text-align': 'left',
            'font-size': '16px'
        }),
        use_container_width=True
    )

with tab2:
    st.header("Function Management")
    
    # Initialize functions in session state if not exists
    if 'FUNCTIONS' not in st.session_state:
        st.session_state.FUNCTIONS = ["Development", "Testing", "Support"]
    
    # Display current functions
    st.subheader("Current Functions")
    
    # Create a form for editing existing functions
    with st.form("edit_functions"):
        edited_functions = []
        functions_to_remove = []
        
        for i, function in enumerate(st.session_state.FUNCTIONS):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_name = st.text_input(
                    f"Function {i+1}",
                    value=function,
                    key=f"function_{i}"
                )
                edited_functions.append(new_name)
            with col2:
                if st.checkbox("Remove", key=f"remove_{i}"):
                    functions_to_remove.append(i)
        
        # Add new function field
        st.subheader("Add New Function")
        new_function = st.text_input("New Function Name", key="new_function")
        
        if st.form_submit_button("Update Functions"):
            # Remove marked functions
            for index in sorted(functions_to_remove, reverse=True):
                edited_functions.pop(index)
            
            # Add new function if provided
            if new_function and new_function not in edited_functions:
                edited_functions.append(new_function)
            
            # Update session state
            st.session_state.FUNCTIONS = edited_functions
            st.success("Functions updated successfully!")
            st.rerun()

with tab3:
    st.info("Additional assumptions can be added here in future versions") 