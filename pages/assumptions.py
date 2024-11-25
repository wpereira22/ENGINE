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
            'Offshore': 40000,
            'Implementation': {
                'Rebadge': 10000,
                'House Resources': 120000,
                'New Hire': 100000
            }
        },
        'Business B': {
            'Onshore': 100000,
            'Offshore': 40000,
            'Implementation': {
                'Rebadge': 10000,
                'House Resources': 120000,
                'New Hire': 100000
            }
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
    st.header("Implementation Cost Assumptions")
    
    with st.form("implementation_costs_form"):
        # Resource Implementation Costs
        st.subheader("Resource Implementation Costs")
        st.markdown("These costs are applied per resource for each implementation type.")
        
        for business in ["Business A", "Business B"]:
            st.subheader(business)
            
            # Resource implementation costs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rebadge_cost = st.number_input(
                    "Rebadge Cost",
                    min_value=0,
                    value=st.session_state.assumptions[business]['Implementation']['Rebadge'],
                    step=1000,
                    help="One-time cost per rebadged resource",
                    key=f"rebadge_{business}"
                )
            
            with col2:
                house_cost = st.number_input(
                    "House Resource Cost",
                    min_value=0,
                    value=st.session_state.assumptions[business]['Implementation']['House Resources'],
                    step=1000,
                    help="Annual cost per house resource",
                    key=f"house_{business}"
                )
            
            with col3:
                new_hire_cost = st.number_input(
                    "New Hire Cost",
                    min_value=0,
                    value=st.session_state.assumptions[business]['Implementation']['New Hire'],
                    step=1000,
                    help="Cost per new hire including recruitment and onboarding",
                    key=f"new_hire_{business}"
                )
            
            st.divider()
        
        if st.form_submit_button("Update Implementation Costs"):
            # Update session state for both businesses
            for business in ["Business A", "Business B"]:
                st.session_state.assumptions[business]['Implementation'].update({
                    'Rebadge': st.session_state[f"rebadge_{business}"],
                    'House Resources': st.session_state[f"house_{business}"],
                    'New Hire': st.session_state[f"new_hire_{business}"]
                })
            
            st.success("Implementation costs updated successfully!")
            st.rerun()
    
    # Display current implementation costs in a table
    st.subheader("Current Implementation Cost Assumptions")
    
    # Create DataFrame for display
    data = []
    for business in ['Business A', 'Business B']:
        for cost_type, value in st.session_state.assumptions[business]['Implementation'].items():
            data.append({
                'Business': business,
                'Implementation Type': cost_type,
                'Cost': f"${value:,}"
            })
    
    df = pd.DataFrame(data)
    st.dataframe(
        df.style.set_properties(**{
            'text-align': 'left',
            'font-size': '16px'
        }),
        use_container_width=True
    )

with tab3:
    st.info("Additional assumptions can be added here in future versions") 