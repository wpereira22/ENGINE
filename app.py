import streamlit as st
import pandas as pd
from datetime import datetime
import json
from openpyxl import Workbook
import io
from utils import create_change_message
from session_state import init_session_state, IMPLEMENTATION_TYPES

# Page config
st.set_page_config(page_title="Cost Savings Analysis", layout="wide")

# Initialize session state
init_session_state()

# Constants
CATEGORIES = ["Resource", "Technology"]
RESOURCE_LOCATIONS = ["Onshore", "Offshore"]
TECH_LOCATIONS = ["On-premise", "Cloud"]

# Helper functions
def delete_record(record):
    # Store the record ID before deletion
    record_id = record['id']
    
    # Remove the record first
    st.session_state.records = [r for r in st.session_state.records if r['id'] != record_id]
    
    # Remove associated changes while preserving other changes
    st.session_state.changes = [
        c for c in st.session_state.changes 
        if c['record_id'] != record_id
    ]
    
    # Remove any implementation costs associated with this record
    keys_to_remove = []
    for key in st.session_state.implementation_costs:
        if f"_{record_id}_" in key:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state.implementation_costs[key]
    
    # Set flag to trigger rerun
    st.session_state.trigger_rerun = True

def add_sample_data():
    """Add sample records and changes for demonstration"""
    # Sample records
    st.session_state.records = [
        # Business A Resources
        {
            'id': 1,
            'business': 'Business A',
            'category': 'Resource',
            'functions': ['Development'],
            'function_descriptions': {
                'Development': 'Core development team for business applications'
            },
            'tech_name': None,
            'location': 'Onshore',
            'count': 5,
            'unit_cost': 100000,
            'total_cost': 500000,
            'comments': 'Primary development team',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 2,
            'business': 'Business A',
            'category': 'Resource',
            'functions': ['Testing'],
            'function_descriptions': {
                'Testing': 'QA and testing team for all applications'
            },
            'tech_name': None,
            'location': 'Offshore',
            'count': 8,
            'unit_cost': 40000,
            'total_cost': 320000,
            'comments': 'Offshore testing team',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 3,
            'business': 'Business A',
            'category': 'Resource',
            'functions': ['Support'],
            'function_descriptions': {
                'Support': '24/7 application support team'
            },
            'tech_name': None,
            'location': 'Offshore',
            'count': 10,
            'unit_cost': 40000,
            'total_cost': 400000,
            'comments': 'Application support team',
            'timestamp': datetime.now().isoformat()
        },
        # Business A Technology
        {
            'id': 4,
            'business': 'Business A',
            'category': 'Technology',
            'functions': ['Development', 'Testing'],
            'function_descriptions': {
                'Development': 'Development environment and tools',
                'Testing': 'Testing and QA tools'
            },
            'tech_name': 'Development Suite',
            'location': None,
            'count': None,
            'unit_cost': None,
            'total_cost': 750000,
            'comments': 'Development and testing tools suite',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 5,
            'business': 'Business A',
            'category': 'Technology',
            'functions': ['Support'],
            'function_descriptions': {
                'Support': 'Support ticketing and monitoring system'
            },
            'tech_name': 'Support System',
            'location': None,
            'count': None,
            'unit_cost': None,
            'total_cost': 250000,
            'comments': 'Support and monitoring tools',
            'timestamp': datetime.now().isoformat()
        },
        # Business B Resources
        {
            'id': 6,
            'business': 'Business B',
            'category': 'Resource',
            'functions': ['Development'],
            'function_descriptions': {
                'Development': 'Core development team for business applications'
            },
            'tech_name': None,
            'location': 'Onshore',
            'count': 4,
            'unit_cost': 90000,
            'total_cost': 360000,
            'comments': 'Primary development team',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 7,
            'business': 'Business B',
            'category': 'Resource',
            'functions': ['Testing'],
            'function_descriptions': {
                'Testing': 'QA and testing team'
            },
            'tech_name': None,
            'location': 'Offshore',
            'count': 6,
            'unit_cost': 35000,
            'total_cost': 210000,
            'comments': 'Testing team',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 8,
            'business': 'Business B',
            'category': 'Resource',
            'functions': ['Support'],
            'function_descriptions': {
                'Support': 'Application support team'
            },
            'tech_name': None,
            'location': 'Offshore',
            'count': 8,
            'unit_cost': 35000,
            'total_cost': 280000,
            'comments': 'Support team',
            'timestamp': datetime.now().isoformat()
        },
        # Business B Technology
        {
            'id': 9,
            'business': 'Business B',
            'category': 'Technology',
            'functions': ['Development', 'Testing'],
            'function_descriptions': {
                'Development': 'Development tools and platforms',
                'Testing': 'Testing automation suite'
            },
            'tech_name': 'Development Platform',
            'location': None,
            'count': None,
            'unit_cost': None,
            'total_cost': 500000,
            'comments': 'Development and testing platform',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 10,
            'business': 'Business B',
            'category': 'Technology',
            'functions': ['Support'],
            'function_descriptions': {
                'Support': 'Support and monitoring tools'
            },
            'tech_name': 'Support Tools',
            'location': None,
            'count': None,
            'unit_cost': None,
            'total_cost': 200000,
            'comments': 'Support infrastructure',
            'timestamp': datetime.now().isoformat()
        }
    ]

    # Sample changes
    st.session_state.changes = [
        {
            'record_id': 1,
            'timestamp': datetime.now().isoformat(),
            'type': 'count_change',
            'from': 5,
            'to': 3,
            'implementation_year': 2,
            'description': 'Reduce development team through automation'
        },
        {
            'record_id': 4,
            'timestamp': datetime.now().isoformat(),
            'type': 'cost_change',
            'from': 750000,
            'to': 500000,
            'implementation_year': 3,
            'description': 'Move to cloud-based development tools'
        },
        {
            'record_id': 7,
            'timestamp': datetime.now().isoformat(),
            'type': 'location_change',
            'from': 'Offshore',
            'to': 'Onshore',
            'implementation_year': 2,
            'description': 'Relocate testing team onshore'
        }
    ]

    # Add sample implementation costs
    for change in st.session_state.changes:
        record = next(r for r in st.session_state.records if r['id'] == change['record_id'])
        change_key = f"{record['business']}_{change['record_id']}_{change['timestamp']}"
        
        if change_key not in st.session_state.implementation_costs:
            st.session_state.implementation_costs[change_key] = {
                'resources': {}
            }
            
            if record['category'] == 'Resource':
                st.session_state.implementation_costs[change_key]['resources'] = {
                    'Rebadge': [2, 1, 0, 0, 0],
                    'House Resources': [1, 2, 1, 0, 0],
                    'New Hire': [1, 1, 1, 0, 0]
                }
            else:  # Technology
                st.session_state.implementation_costs[change_key]['resources'] = {
                    'Internal Build Costs': [100000, 50000, 25000, 10000, 0]
                }

    # Add sample assumptions
    st.session_state.assumptions = {
        'Business A': {
            'Onshore': 100000,
            'Offshore': 40000,
            'Implementation': {
                'Rebadge': 15000,
                'House Resources': 20000,
                'New Hire': 25000
            }
        },
        'Business B': {
            'Onshore': 90000,
            'Offshore': 35000,
            'Implementation': {
                'Rebadge': 12000,
                'House Resources': 18000,
                'New Hire': 22000
            }
        }
    }

    st.success("Sample data loaded successfully!")
    st.rerun()

# Main content
st.title("Cost Savings Analysis")

# Move Save/Load to sidebar
st.sidebar.title("Data Management")

# Create three columns in the sidebar for the buttons
col1, col2, col3 = st.sidebar.columns(3)

with col1:
    if st.button("Save Analysis"):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Save records
            records_df = pd.DataFrame(st.session_state.records)
            if not records_df.empty:
                records_df['functions'] = records_df['functions'].apply(lambda x: json.dumps(x))
                records_df['function_descriptions'] = records_df['function_descriptions'].apply(lambda x: json.dumps(x))
            records_df.to_excel(writer, sheet_name='Records', index=False)
            
            # Save changes
            changes_df = pd.DataFrame(st.session_state.changes)
            changes_df.to_excel(writer, sheet_name='Changes', index=False)
            
            # Save implementation costs
            impl_costs_data = []
            for key, data in st.session_state.implementation_costs.items():
                if isinstance(data, dict) and 'resources' in data:
                    for impl_type, impl_data in data['resources'].items():
                        if isinstance(impl_data, dict):
                            row = {
                                'key': key,
                                'implementation_type': impl_type,
                                'values': json.dumps(impl_data.get('values', [])),
                                'salary': impl_data.get('salary'),
                                'description': impl_data.get('description', '')
                            }
                            impl_costs_data.append(row)
            
            if impl_costs_data:
                impl_costs_df = pd.DataFrame(impl_costs_data)
                impl_costs_df.to_excel(writer, sheet_name='Implementation', index=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cost_analysis_{timestamp}.xlsx"
        st.sidebar.download_button(
            label="Download Excel",
            data=buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.sidebar.success("Analysis ready for download!")

with col2:
    uploaded_file = st.file_uploader("Load Analysis", type=['xlsx'])
    if uploaded_file is not None:
        try:
            # Load records and changes as before
            records_df = pd.read_excel(uploaded_file, sheet_name='Records')
            changes_df = pd.read_excel(uploaded_file, sheet_name='Changes')
            
            # Load implementation costs
            try:
                impl_costs_df = pd.read_excel(uploaded_file, sheet_name='Implementation')
                
                # Reset implementation costs
                st.session_state.implementation_costs = {}
                
                # Rebuild implementation costs structure
                for _, row in impl_costs_df.iterrows():
                    key = row['key']
                    impl_type = row['implementation_type']
                    
                    try:
                        values = json.loads(row['values']) if isinstance(row['values'], str) else []
                        values = [float(v) if not pd.isna(v) else 0.0 for v in values]
                    except:
                        values = [0.0] * 5
                    
                    try:
                        salary = float(row['salary']) if not pd.isna(row['salary']) else None
                    except:
                        salary = None
                    
                    description = row.get('description', '') if not pd.isna(row.get('description')) else ''
                    
                    if key not in st.session_state.implementation_costs:
                        st.session_state.implementation_costs[key] = {'resources': {}}
                    
                    st.session_state.implementation_costs[key]['resources'][impl_type] = {
                        'values': values,
                        'salary': salary,
                        'description': description
                    }
                    
                    # Update the corresponding table in session state
                    business = key.split('_')[0]
                    category = "Resource" if impl_type in IMPLEMENTATION_TYPES["Resource"] else "Technology"
                    table_key = f"{business}_{category}_table"
                    
                    if table_key not in st.session_state:
                        st.session_state[table_key] = pd.DataFrame()
                    
                    # Update the table with the loaded values
                    table_data = {
                        'Description': description,
                        'Implementation Type': impl_type,
                        **{f'Year {i+1}': values[i] for i in range(5)}
                    }
                    if category == "Resource":
                        table_data['Salary'] = salary
                    
                    st.session_state[table_key] = pd.concat([
                        st.session_state[table_key],
                        pd.DataFrame([table_data])
                    ]).reset_index(drop=True)
                    
            except Exception as e:
                st.sidebar.warning(f"No implementation data found or error loading it: {str(e)}")
            
            # Continue with existing loading logic for records and changes...
            if not records_df.empty:
                records_df['functions'] = records_df['functions'].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
                records_df['function_descriptions'] = records_df['function_descriptions'].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else {}
                )
            
            st.session_state.records = records_df.to_dict('records')
            st.session_state.changes = changes_df.to_dict('records')
            
            # Clean up NaN values
            for record in st.session_state.records:
                for key, value in record.items():
                    if pd.isna(value):
                        if key in ['functions']:
                            record[key] = []
                        elif key in ['function_descriptions']:
                            record[key] = {}
                        else:
                            record[key] = None
            
            for change in st.session_state.changes:
                for key, value in change.items():
                    if pd.isna(value):
                        change[key] = None
            
            st.sidebar.success("Analysis loaded successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
            st.sidebar.error("Please ensure the file format is correct.")

with col3:
    if st.button("Load Sample Data", help="Click to populate with sample data for demonstration"):
        add_sample_data()

# Add this check at the top of the main content section (after initializing session state):
if st.session_state.get('trigger_rerun', False):
    st.session_state.trigger_rerun = False
    st.rerun()

# Create business level tabs
business_tabs = st.tabs([st.session_state.business_names[business] 
                        for business in ['Business A', 'Business B']])

for i, business_tab in enumerate(business_tabs):
    with business_tab:
        # Get the internal business name (Business A or Business B)
        internal_business = ['Business A', 'Business B'][i]
        # Get the display name
        selected_business = st.session_state.business_names[internal_business]
        
        # Add key metrics in columns
        col1, col2, col3 = st.columns([1, 1, 2])
        
        # Calculate metrics for the selected business
        resource_count = sum(r['count'] for r in st.session_state.records 
                            if r['business'] == internal_business 
                            and r['category'] == 'Resource')
        
        tech_count = sum(1 for r in st.session_state.records 
                        if r['business'] == internal_business 
                        and r['category'] == 'Technology')
        
        total_cost = sum(r['total_cost'] for r in st.session_state.records 
                        if r['business'] == internal_business)
        
        # Display metrics
        with col1:
            st.metric("Total Resources", resource_count)
        
        with col2:
            st.metric("Total Technology Items", tech_count)
        
        with col3:
            st.metric("Total Current Cost", f"${total_cost:,}")
        
        st.divider()  # Add a line to separate metrics from category tabs
        
        # Create category level tabs
        category_tabs = st.tabs(CATEGORIES)
        
        for j, category_tab in enumerate(category_tabs):
            with category_tab:
                selected_category = CATEGORIES[j]
                
                # Create the main function tabs with reordered tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "Current Records",  # Moved to first position
                    "Add Record", 
                    "Future State Changes",
                    "Cost Analysis"
                ])
                
                # Move the Current Records content to tab1
                with tab1:
                    total_cost = 0
                    for record in st.session_state.records:
                        if record['business'] == internal_business and record['category'] == selected_category:
                            total_cost += record['total_cost']
                            
                            # Different display for resources vs technology
                            if selected_category == "Resource":
                                title = f"### {', '.join(record['functions'])} Team - ${record['total_cost']:,}"
                            else:
                                title = f"### {record['tech_name']} - ${record['total_cost']:,}"
                                
                            with st.expander(title, expanded=False):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    # Simplified layout for better readability
                                    if selected_category == "Resource":
                                        # Resource layout
                                        st.markdown(f"""
                                            #### Key Information
                                            - **Location:** {record['location']}
                                            - **Team Size:** {record['count']} resources
                                            - **Cost per Resource:** ${record['unit_cost']:,}
                                            
                                            #### Comments
                                            _{record['comments'] if record['comments'] else 'No comments provided'}_
                                        """)
                                    else:
                                        # Technology layout
                                        st.markdown(f"""
                                            #### Key Information
                                            - **Annual Cost:** ${record['total_cost']:,}
                                            
                                            #### Comments
                                            _{record['comments'] if record['comments'] else 'No comments provided'}_
                                        """)
                                
                                with col2:
                                    if selected_category == "Resource":
                                        change_type = st.selectbox(
                                            "Plan Change",
                                            ["No Change", "Modify Count", "Change Location"],
                                            key=f"change_type_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                        )
                                        
                                        implementation_year = st.selectbox(
                                            "Implementation Year",
                                            range(1, 6),
                                            key=f"year_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                        )
                                        
                                        st.button("Delete Record", 
                                                key=f"del_record_{record['id']}_{hash(tuple(sorted(record['functions'])))}",
                                                type="secondary",
                                                on_click=delete_record,
                                                args=(record,))
                                        
                                        if change_type == "Modify Count":
                                            new_count = st.number_input(
                                                "New Count",
                                                min_value=0,
                                                value=record['count'],
                                                key=f"new_count_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            change_description = st.text_area(
                                                "Change Description",
                                                placeholder="e.g., Automation reduces headcount",
                                                key=f"desc_count_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            if st.button("Apply Change", key=f"apply_count_{record['id']}_{hash(tuple(sorted(record['functions'])))}"):
                                                # Calculate new total cost based on unit cost
                                                new_total_cost = (new_count * record['unit_cost']) if record['unit_cost'] is not None else 0
                                                
                                                change = {
                                                    'record_id': record['id'],
                                                    'type': 'count_change',
                                                    'from': record['count'],
                                                    'to': new_count,
                                                    'implementation_year': implementation_year,
                                                    'description': change_description,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'new_total_cost': new_total_cost,
                                                    'category': record['category'],  # Explicitly set category
                                                    'functions': record['functions'].copy(),  # Make a copy of functions
                                                    'original_location': record['location'],
                                                    'original_unit_cost': record['unit_cost'],
                                                    'business': record['business'],  # Add business for more specific matching
                                                    'record_timestamp': record['timestamp']  # Add record timestamp for unique identification
                                                }
                                                
                                                st.session_state.changes.append(change)
                                                st.success("Change recorded!")
                                        
                                        elif change_type == "Change Location":
                                            new_location = st.selectbox(
                                                "New Location",
                                                RESOURCE_LOCATIONS if record['category'] == "Resource" else TECH_LOCATIONS,
                                                key=f"new_location_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            # Add description field before the button
                                            change_description = st.text_area(
                                                "Change Description",
                                                placeholder="e.g., Moving to cloud reduces headcount",
                                                key=f"desc_location_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            
                                            if st.button("Apply Change", key=f"apply_location_{record['id']}_{hash(tuple(sorted(record['functions'])))}"):
                                                # Get new unit cost from assumptions
                                                new_unit_cost = st.session_state.assumptions[internal_business][new_location]
                                                # Calculate new total cost based on the ratio of unit costs
                                                new_total_cost = (new_unit_cost / record['unit_cost']) * record['total_cost'] if record['unit_cost'] > 0 else record['total_cost']
                                                
                                                change = {
                                                    'record_id': record['id'],
                                                    'type': 'location_change',
                                                    'from': record['location'],
                                                    'to': new_location,
                                                    'implementation_year': implementation_year,
                                                    'description': change_description,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'new_total_cost': new_total_cost
                                                }
                                                st.session_state.changes.append(change)
                                                st.success("Change recorded!")
                                    
                                    else:  # Technology
                                        change_type = st.selectbox(
                                            "Plan Change",
                                            ["No Change", "Modify Cost"],
                                            key=f"change_type_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                        )
                                        
                                        implementation_year = st.selectbox(
                                            "Implementation Year",
                                            range(1, 6),
                                            key=f"year_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                        )
                                        
                                        st.button("Delete Record", 
                                                key=f"del_record_{record['id']}_{hash(tuple(sorted(record['functions'])))}",
                                                type="secondary",
                                                on_click=delete_record,
                                                args=(record,))
                                        
                                        if change_type == "Modify Cost":
                                            new_cost = st.number_input(
                                                "New Annual Cost",
                                                min_value=0.0,
                                                value=float(record['total_cost']),
                                                key=f"new_cost_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            # Add description field
                                            change_description = st.text_area(
                                                "Change Description",
                                                placeholder="e.g., Cloud migration reduces cost",
                                                key=f"desc_cost_{record['id']}_{hash(tuple(sorted(record['functions'])))}"
                                            )
                                            if st.button("Apply Change", key=f"apply_cost_{record['id']}_{hash(tuple(sorted(record['functions'])))}"):
                                                change = {
                                                    'record_id': record['id'],
                                                    'type': 'cost_change',
                                                    'from': record['total_cost'],
                                                    'to': new_cost,  # Just use the new cost directly
                                                    'implementation_year': implementation_year,
                                                    'description': change_description,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'new_total_cost': new_cost  # Add this to be consistent with other changes
                                                }
                                                st.session_state.changes.append(change)
                                                st.success("Change recorded!")
                                
                    st.metric("Total Current Cost", f"${total_cost:,}")

                # Move the Add Record content to tab2
                with tab2:
                    with st.form(f"new_record_{selected_business}_{selected_category}"):
                        st.subheader("New Record Details")
                        
                        # Replace single function selector with multiple checkboxes
                        st.write("**Select Functions:**")
                        selected_functions = {}
                        function_descriptions = {}
                        
                        # Create columns for better layout
                        cols = st.columns(len(st.session_state.FUNCTIONS))
                        for i, function in enumerate(st.session_state.FUNCTIONS):
                            with cols[i]:
                                selected_functions[function] = st.checkbox(
                                    function,
                                    key=f"func_{function}_{selected_business}_{selected_category}"
                                )
                                if selected_functions[function]:
                                    function_descriptions[function] = st.text_area(
                                        f"Description for {function}",
                                        key=f"func_desc_{function}_{selected_business}_{selected_category}",
                                        placeholder=f"Describe {function} responsibilities..."
                                    )
                        
                        # Validate at least one function is selected
                        functions_selected = any(selected_functions.values())
                        if not functions_selected:
                            st.warning("Please select at least one function.")
                        
                        if selected_category == "Resource":
                            # Resource-specific fields
                            location = st.selectbox("Location", RESOURCE_LOCATIONS)
                            count = st.number_input("Count", min_value=1, value=1)
                            unit_cost = st.session_state.assumptions[internal_business][location]
                            total_cost = unit_cost * count
                            
                            st.write(f"Unit Cost: ${unit_cost:,}")
                            st.write(f"Total Cost: ${total_cost:,}")
                            
                        else:  # Technology
                            tech_name = st.text_input("Technology Name")
                            total_cost = st.number_input("Total Annual Cost", min_value=0.0, value=0.0)
                            unit_cost = None
                            count = None
                            location = None
                        
                        comments = st.text_area("Comments")
                        
                        if st.form_submit_button("Add Record"):
                            if functions_selected:
                                # Get list of selected functions
                                selected_function_list = [
                                    f for f, selected in selected_functions.items() 
                                    if selected
                                ]
                                
                                # Filter descriptions to only include selected functions
                                selected_descriptions = {
                                    f: function_descriptions.get(f, '')
                                    for f in selected_function_list
                                    if f in function_descriptions
                                }
                                
                                new_record = {
                                    'id': len(st.session_state.records),
                                    'business': internal_business,
                                    'category': selected_category,
                                    'functions': selected_function_list,
                                    'function_descriptions': selected_descriptions or {},  # Ensure it's never None
                                    'tech_name': tech_name if selected_category == "Technology" else None,
                                    'location': location,
                                    'count': count,
                                    'unit_cost': unit_cost,
                                    'total_cost': total_cost,
                                    'comments': comments,
                                    'timestamp': datetime.now().isoformat()
                                }
                                st.session_state.records.append(new_record)
                                st.success("Record added successfully!")
                                st.rerun()

                # Tab 3: Future State Changes
                with tab3:
                    if st.session_state.changes:
                        # First filter changes for current business and category
                        relevant_changes = [
                            change for change in st.session_state.changes
                            if (
                                # Match the record
                                (record := next(
                                    (r for r in st.session_state.records 
                                     if r['id'] == change['record_id'] 
                                     and r['category'] == change.get('category', r['category'])),
                                    None
                                ))
                                # Check if it matches current business and category
                                and record['business'] == internal_business  # Use internal_business instead of selected_business
                                and record['category'] == selected_category
                            )
                        ]
                        
                        for change in relevant_changes:
                            # Get the record using the same matching logic as above
                            record = next(
                                (r for r in st.session_state.records 
                                 if r['id'] == change['record_id'] 
                                 and r['category'] == change.get('category', r['category'])),
                                None
                            )
                            
                            if record:  # Only proceed if we found a matching record
                                # Create message based on change type
                                if change['type'] == 'count_change' and record['category'] == 'Resource':
                                    message = (
                                        f"Resource count will change from {change['from']} to {change['to']} "
                                        f"in Year {change['implementation_year']}\n"
                                        f"- Impact: {'Reduction' if change['to'] < change['from'] else 'Increase'} "
                                        f"of {abs(change['from'] - change['to'])} resources\n"
                                        f"- Description: {change.get('description', 'No description provided')}"
                                    )
                                elif change['type'] == 'location_change':
                                    message = (
                                        f"Location will change from {change['from']} to {change['to']} "
                                        f"in Year {change['implementation_year']}\n"
                                        f"- Description: {change.get('description', 'No description provided')}"
                                    )
                                elif change['type'] == 'cost_change':
                                    message = (
                                        f"Cost will change from ${change['from']:,} to ${change['to']:,} "
                                        f"in Year {change['implementation_year']}\n"
                                        f"- Description: {change.get('description', 'No description provided')}"
                                    )
                                
                                # Display the change
                                if record['category'] == "Resource":
                                    st.subheader(f"{', '.join(record['functions'])} Team ({record['location']})")
                                else:
                                    st.subheader(f"{record['tech_name']} ({', '.join(record['functions'])})")
                                
                                st.markdown(message)
                                
                                # Add delete button for each change
                                if st.button("Delete Change", 
                                           key=f"del_change_{record['id']}_{change['timestamp']}"):
                                    st.session_state.changes.remove(change)
                                    st.rerun()
                                
                                st.divider()
                    else:
                        st.info("No changes recorded yet.")

                # Tab 4: Cost Analysis Table
                with tab4:
                    if st.session_state.records:
                        # Calculate current and future costs
                        analysis_data = []
                        total_current = 0
                        total_future = 0
                        
                        for record in st.session_state.records:
                            # Use internal_business instead of selected_business for comparison
                            if record['business'] == internal_business and record['category'] == selected_category:
                                current_cost = record['total_cost']
                                total_current += current_cost
                                
                                # Calculate future cost based on changes and implementation year
                                future_costs_by_year = [current_cost] * 6  # Year 0-5
                                
                                for change in st.session_state.changes:
                                    if change['record_id'] == record['id']:
                                        year = change['implementation_year']
                                        if change['type'] == 'count_change':
                                            if record['category'] == 'Resource':
                                                new_cost = (change['to'] * record['unit_cost']) if record['unit_cost'] is not None else 0
                                            else:
                                                new_cost = record['total_cost']  # For technology records, keep original cost
                                        elif change['type'] == 'location_change':
                                            new_unit_cost = st.session_state.assumptions[internal_business][change['to']]
                                            new_cost = (record['count'] * new_unit_cost) if record['count'] is not None else record['total_cost']
                                        elif change['type'] == 'cost_change':
                                            new_cost = change['to']
                                        
                                        # Apply the new cost from implementation year onwards
                                        for y in range(year, 6):
                                            future_costs_by_year[y] = new_cost
                                
                                # Different name construction for Resource vs Technology
                                if record['category'] == 'Technology':
                                    name = f"{record['tech_name']} ({', '.join(record['functions'])})"
                                else:
                                    name = f"{', '.join(record['functions'])} Team"
                                
                                analysis_data.append({
                                    'Business': st.session_state.business_names[record['business']],  # Use display name for display
                                    'Category': record['category'],
                                    'Name': name,
                                    'Current Cost': current_cost,
                                    'Year 1': future_costs_by_year[1],
                                    'Year 2': future_costs_by_year[2],
                                    'Year 3': future_costs_by_year[3],
                                    'Year 4': future_costs_by_year[4],
                                    'Year 5': future_costs_by_year[5],
                                    'Total 5Y Savings': sum(current_cost - cost for cost in future_costs_by_year[1:]),
                                    'Row Total': sum(future_costs_by_year[1:])
                                })

                        # Only create and format DataFrame if we have data
                        if analysis_data:
                            # Create DataFrame and sort by Business and Category
                            df = pd.DataFrame(analysis_data)
                            df = df.sort_values(['Business', 'Category', 'Name'])
                            
                            # Format currency columns
                            currency_cols = ['Current Cost', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 
                                           'Total 5Y Savings', 'Row Total']
                            for col in currency_cols:
                                df[col] = df[col].apply(lambda x: f"${x:,.2f}")
                            
                            # Create a style function for background colors with better contrast
                            def style_df(df):
                                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                                
                                # Simpler styling with better contrast
                                for col in currency_cols[1:-1]:  # Skip Current Cost and Row Total
                                    try:
                                        current_vals = df['Current Cost'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
                                        col_vals = df[col].apply(lambda x: float(x.replace('$', '').replace(',', '')))
                                        
                                        # Use more subtle colors with dark text
                                        styles.loc[col_vals < current_vals, col] = 'color: #006100'  # Dark green
                                        styles.loc[col_vals > current_vals, col] = 'color: #9c0006'  # Dark red
                                    except:
                                        continue
                                
                                # Style savings column
                                styles.loc[:, 'Total 5Y Savings'] = df['Total 5Y Savings'].apply(
                                    lambda x: 'color: #006100' if '-' not in x else 'color: #9c0006'
                                )
                                
                                return styles
                            
                            # Apply styling
                            styled_df = df.style\
                                .apply(style_df, axis=None)\
                                .set_properties(**{
                                    'text-align': 'right',
                                    'padding': '5px 15px',
                                    'font-size': '14px'
                                })\
                                .set_table_styles([
                                    {'selector': 'th', 'props': [
                                        ('text-align', 'center'),
                                        ('font-weight', 'bold'),
                                        ('color', '#333333'),
                                        ('background-color', '#f0f2f6')
                                    ]},
                                    {'selector': 'td', 'props': [
                                        ('text-align', 'right'),
                                        ('color', '#333333')
                                    ]}
                                ])
                            
                            # Display the table
                            st.dataframe(styled_df, use_container_width=True)
                            
                            # Add column totals at the bottom
                            st.divider()
                            st.subheader("Column Totals")
                            totals = {}
                            for col in currency_cols:
                                try:
                                    total = sum(float(x.replace('$', '').replace(',', '')) 
                                              for x in df[col])
                                    totals[col] = f"${total:,.2f}"
                                except:
                                    continue
                            
                            # Display totals in a single row with same styling as main table
                            totals_df = pd.DataFrame([totals])
                            
                            # Create style function for totals with same conditional formatting
                            def style_totals(df):
                                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                                
                                # Apply same color coding for changes
                                for col in currency_cols[1:-1]:  # Skip Current Cost and Row Total
                                    try:
                                        current_val = float(df['Current Cost'].iloc[0].replace('$', '').replace(',', ''))
                                        col_val = float(df[col].iloc[0].replace('$', '').replace(',', ''))
                                        
                                        if col_val < current_val:
                                            styles.iloc[0][col] = 'color: #006100'  # Dark green
                                        elif col_val > current_val:
                                            styles.iloc[0][col] = 'color: #9c0006'  # Dark red
                                    except:
                                        continue
                                
                                # Style savings column
                                try:
                                    savings_val = df['Total 5Y Savings'].iloc[0]
                                    styles.iloc[0]['Total 5Y Savings'] = 'color: #006100' if '-' not in savings_val else 'color: #9c0006'
                                except:
                                    pass
                                
                                return styles
                            
                            # Apply styling to totals
                            styled_totals_df = totals_df.style\
                                .apply(style_totals, axis=None)\
                                .set_properties(**{
                                    'text-align': 'right',
                                    'padding': '5px 15px',
                                    'font-size': '14px',
                                    'font-weight': 'bold',
                                    'color': '#333333'
                                })\
                                .set_table_styles([
                                    {'selector': 'th', 'props': [
                                        ('text-align', 'center'),
                                        ('font-weight', 'bold'),
                                        ('color', '#333333'),
                                        ('background-color', '#f0f2f6')
                                    ]},
                                    {'selector': 'td', 'props': [
                                        ('text-align', 'right'),
                                        ('color', '#333333')
                                    ]}
                                ])
                            
                            st.dataframe(styled_totals_df, use_container_width=True)
                        else:
                            st.info(f"No records found for {st.session_state.business_names[internal_business]} - {selected_category}")
                    else:
                        st.info("No records available. Please add some records first.") 