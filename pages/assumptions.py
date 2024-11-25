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

# Add business names to session state if not exists
if 'business_names' not in st.session_state:
    st.session_state.business_names = {
        'Business A': 'Business A',
        'Business B': 'Business B'
    }

# Initialize functions with default values if not exists
if 'FUNCTIONS' not in st.session_state:
    st.session_state.FUNCTIONS = ["Development", "Testing", "Support"]

st.title("Cost Assumptions")

# Update tabs to include business names
tab1, tab2, tab3, tab4 = st.tabs(["Resource Costs", "Functions", "Business Names", "Other Assumptions"])

with tab1:
    st.header("Resource Cost Assumptions")
    
    # Create a form for resource costs
    with st.form("resource_costs_form"):
        # Business A costs
        st.subheader(st.session_state.business_names['Business A'])
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
        st.subheader(st.session_state.business_names['Business B'])
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
    
    # Display current functions
    st.subheader("Current Functions")
    
    # Create a form for editing existing functions
    with st.form("edit_functions"):
        edited_functions = []
        functions_to_remove = set()
        
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
                    functions_to_remove.add(function)
        
        # Add new function field
        st.subheader("Add New Function")
        new_function = st.text_input("New Function Name", key="new_function")
        
        if st.form_submit_button("Update Functions"):
            # Store old functions for reference
            old_functions = st.session_state.FUNCTIONS.copy()
            
            # Create new edited_functions list excluding removed functions
            edited_functions = [
                f for f in edited_functions 
                if f not in functions_to_remove
            ]
            
            # Update existing records that use any removed function
            if 'records' in st.session_state:
                for record in st.session_state.records:
                    # Store the base ID
                    base_id = str(record['id']).split('_')[0]
                    
                    # Update functions list
                    new_functions = []
                    for f in record['functions']:
                        if f in functions_to_remove:
                            if 'Unassigned' not in new_functions:
                                new_functions.append('Unassigned')
                        else:
                            new_functions.append(f)
                    record['functions'] = new_functions

                    # Update function descriptions
                    new_descriptions = {}
                    for func, desc in record['function_descriptions'].items():
                        if func in functions_to_remove:
                            new_descriptions['Unassigned'] = desc
                        else:
                            new_descriptions[func] = desc
                    record['function_descriptions'] = new_descriptions

                    # Update record ID while preserving the base ID
                    record['id'] = f"{base_id}_{datetime.now().timestamp()}"
                    
                    # Update any related changes to use the base ID
                    if 'changes' in st.session_state:
                        for change in st.session_state.changes:
                            if str(change['record_id']) == base_id:
                                change['record_id'] = base_id
            
            # Add new function if provided
            if new_function and new_function not in edited_functions:
                edited_functions.append(new_function)
            
            # Ensure "Unassigned" is always available
            if 'Unassigned' not in edited_functions:
                edited_functions.append('Unassigned')
            
            # Update session state
            st.session_state.FUNCTIONS = edited_functions
            
            # Update existing records with renamed functions
            if 'records' in st.session_state:
                for record in st.session_state.records:
                    # Create a mapping of old function names to new ones
                    function_mapping = {
                        old: new for old, new in zip(old_functions, edited_functions)
                        if old != new and old in record['functions']
                    }
                    
                    # Update functions using the mapping
                    record['functions'] = [
                        function_mapping.get(f, f) for f in record['functions']
                    ]
                    
                    # Update function descriptions
                    new_descriptions = {}
                    for func, desc in record['function_descriptions'].items():
                        new_func = function_mapping.get(func, func)
                        new_descriptions[new_func] = desc
                    record['function_descriptions'] = new_descriptions
            
            st.success("Functions updated successfully!")
            st.rerun()

with tab3:
    st.header("Business Names Management")
    
    with st.form("business_names_form"):
        st.subheader("Edit Business Names")
        
        business_a_name = st.text_input(
            "Business A Display Name",
            value=st.session_state.business_names['Business A']
        )
        
        business_b_name = st.text_input(
            "Business B Display Name",
            value=st.session_state.business_names['Business B']
        )
        
        if st.form_submit_button("Update Business Names"):
            # Just update the display names in business_names
            st.session_state.business_names['Business A'] = business_a_name
            st.session_state.business_names['Business B'] = business_b_name
            
            # Don't update the records - they should keep using internal names
            # Remove this section:
            # if 'records' in st.session_state:
            #     for record in st.session_state.records:
            #         if record['business'] == old_names['Business A']:
            #             record['business'] = business_a_name
            #         elif record['business'] == old_names['Business B']:
            #             record['business'] = business_b_name
            
            st.success("Business names updated successfully!")
            st.rerun()

    # Display current business names in a table
    st.subheader("Current Business Names")
    business_names_df = pd.DataFrame([
        {"Internal Name": "Business A", "Display Name": st.session_state.business_names['Business A']},
        {"Internal Name": "Business B", "Display Name": st.session_state.business_names['Business B']}
    ])
    st.dataframe(business_names_df, use_container_width=True)

with tab4:
    st.info("Additional assumptions can be added here in future versions") 