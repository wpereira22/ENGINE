import streamlit as st
import pandas as pd
from datetime import datetime
from utils import create_change_message
from session_state import init_session_state

# Constants
IMPLEMENTATION_TYPES = {
    "Resource": ["Rebadge", "House Resources", "New Hire"],
    "Technology": ["Internal Build Costs"]
}

# Initialize session state
init_session_state()

def create_editable_table(changes, records, business, category):
    """Create an editable table with change information"""
    rows = []
    
    for change in changes:
        record = next(r for r in st.session_state.records if r['id'] == change['record_id'])
        if record['business'] == business and record['category'] == category:
            change_key = f"{business}_{change['record_id']}_{change['timestamp']}"
            
            # Initialize implementation data if not exists
            if change_key not in st.session_state.implementation_costs:
                st.session_state.implementation_costs[change_key] = {
                    'resources': {}
                }
            
            # Create base row data
            base_row = {
                'Change': f"{'📋 ' + record['tech_name'] if category == 'Technology' else '📋 ' + ', '.join(record['functions'])}",
                'Implementation Type': None,
            }
            
            # Add salary column only for Resources
            if category == "Resource":
                base_row['Salary'] = 0
            
            # Add year columns
            for year in range(1, 6):
                base_row[f'Year {year}'] = 0
            
            # Add rows for each implementation type
            for impl_type in IMPLEMENTATION_TYPES[category]:
                row = base_row.copy()
                row['Implementation Type'] = impl_type
                
                # Get implementation data
                impl_data = st.session_state.implementation_costs[change_key]['resources'].get(impl_type, {})
                
                if isinstance(impl_data, dict):
                    # Get values from the dictionary structure
                    values = impl_data.get('values', [0] * 5)
                    if category == "Resource":
                        row['Salary'] = impl_data.get('salary', 0)
                else:
                    # Handle legacy data or initialize new
                    values = [0] * 5
                    
                # Add year columns
                for year in range(5):
                    try:
                        row[f'Year {year + 1}'] = values[year]
                    except (IndexError, TypeError):
                        row[f'Year {year + 1}'] = 0
                
                rows.append(row)
    
    return pd.DataFrame(rows) if rows else None

def update_costs(df, business, category):
    """Update implementation costs based on edited table values"""
    if df is not None:
        for idx, row in df.iterrows():
            change_info = row['Change'].replace('📋 ', '')
            impl_type = row['Implementation Type']
            
            # Find matching change and record
            for change in st.session_state.changes:
                record = next(r for r in st.session_state.records if r['id'] == change['record_id'])
                if record['business'] == business and record['category'] == category:
                    if (category == 'Technology' and record['tech_name'] == change_info) or \
                       (category == 'Resource' and ', '.join(record['functions']) == change_info):
                        
                        change_key = f"{business}_{change['record_id']}_{change['timestamp']}"
                        
                        # Initialize if not exists
                        if change_key not in st.session_state.implementation_costs:
                            st.session_state.implementation_costs[change_key] = {
                                'resources': {}
                            }
                        
                        # Initialize or update the implementation type data
                        if impl_type not in st.session_state.implementation_costs[change_key]['resources']:
                            st.session_state.implementation_costs[change_key]['resources'][impl_type] = {}
                        
                        # Ensure we have a dictionary
                        if not isinstance(st.session_state.implementation_costs[change_key]['resources'][impl_type], dict):
                            st.session_state.implementation_costs[change_key]['resources'][impl_type] = {}
                        
                        # Update values
                        values = []
                        for year in range(5):
                            try:
                                value = float(row[f'Year {year + 1}'])
                            except (ValueError, TypeError):
                                value = 0
                            values.append(value)
                        
                        # Update the dictionary
                        impl_data = st.session_state.implementation_costs[change_key]['resources'][impl_type]
                        impl_data['values'] = values
                        if category == "Resource" and 'Salary' in row:
                            impl_data['salary'] = float(row['Salary']) if row['Salary'] != '' else 0

def calculate_total_costs(business):
    """Calculate total implementation costs for a business"""
    total_by_type = {impl_type: [0] * 5 for impl_type in 
                     IMPLEMENTATION_TYPES["Resource"] + IMPLEMENTATION_TYPES["Technology"]}
    changes_by_type = {impl_type: [] for impl_type in 
                      IMPLEMENTATION_TYPES["Resource"] + IMPLEMENTATION_TYPES["Technology"]}
    
    for change_key, data in st.session_state.implementation_costs.items():
        if change_key.startswith(business):
            for impl_type, impl_data in data['resources'].items():
                # Handle both old and new data structures
                if isinstance(impl_data, list):
                    yearly_values = impl_data
                    salary = 0
                elif isinstance(impl_data, dict):
                    yearly_values = impl_data.get('values', [0] * 5)
                    salary = impl_data.get('salary', 0)
                else:
                    continue
                
                try:
                    # For resource types
                    if impl_type in IMPLEMENTATION_TYPES["Resource"]:
                        for year in range(5):
                            resource_count = float(yearly_values[year])
                            cost_per_resource = float(salary) if salary and float(salary) > 0 else float(st.session_state.assumptions[business]['Implementation'][impl_type])
                            total_by_type[impl_type][year] += resource_count * cost_per_resource
                    
                    # For technology types - directly use the values as costs
                    elif impl_type == "Internal Build Costs":
                        for year in range(5):
                            try:
                                value = float(yearly_values[year])
                                total_by_type["Internal Build Costs"][year] += value
                            except (ValueError, TypeError):
                                continue
                    
                    # Add to changes_by_type if there are any non-zero values
                    if any(float(v) != 0 for v in yearly_values):
                        record_id = int(change_key.split('_')[1])
                        record = next(r for r in st.session_state.records if r['id'] == record_id)
                        change = next(c for c in st.session_state.changes if c['record_id'] == record_id)
                        
                        changes_by_type[impl_type].append({
                            'change': change,
                            'record': record,
                            'yearly_values': yearly_values,
                            'salary': salary if impl_type in IMPLEMENTATION_TYPES["Resource"] else None
                        })
                        
                except (ValueError, TypeError, IndexError) as e:
                    continue
    
    return total_by_type, changes_by_type

def add_custom_row(business, category):
    """Add a custom implementation row"""
    with st.form(f"add_custom_{category.lower()}_{business}"):
        st.subheader(f"Add Custom {category} Implementation")
        
        # Common fields
        custom_name = st.text_input("Name")
        impl_type = st.selectbox("Implementation Type", IMPLEMENTATION_TYPES[category])
        
        # Salary field only for Resources
        salary = 0
        if category == "Resource":
            salary = st.number_input("Salary", min_value=0.0, format="%.2f")
        
        # Year inputs
        cols = st.columns(5)
        yearly_values = []
        for i, col in enumerate(cols):
            with col:
                value = st.number_input(f"Year {i+1}", min_value=0.0, format="%.2f")
                yearly_values.append(value)
        
        # Add two columns for submit and cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Add")
        with col2:
            cancelled = st.form_submit_button("Cancel")
        
        if cancelled:
            # Reset the show form flag
            st.session_state[f"show_{category.lower()}_form_{business}"] = False
            st.rerun()
            
        if submitted and custom_name:
            # Create a unique ID for the custom entry
            custom_id = len(st.session_state.records)
            timestamp = datetime.now().isoformat()
            
            # Create record
            record = {
                'id': custom_id,
                'business': business,
                'category': category,
                'functions': [custom_name] if category == "Resource" else [],
                'tech_name': custom_name if category == "Technology" else None,
                'location': 'Custom',
                'count': 1,
                'unit_cost': salary if category == "Resource" else sum(yearly_values),
                'total_cost': salary if category == "Resource" else sum(yearly_values),
                'comments': 'Custom Addition',
                'timestamp': timestamp
            }
            
            # Create change with required fields
            change = {
                'record_id': custom_id,
                'timestamp': timestamp,
                'type': 'Custom Addition',
                'from': 0,
                'to': record['total_cost'],
                'implementation_year': 1,  # Add default implementation year
                'description': f"Custom {category} Addition"
            }
            
            # Add to session state
            st.session_state.records.append(record)
            st.session_state.changes.append(change)
            
            # Initialize implementation costs
            change_key = f"{business}_{custom_id}_{timestamp}"
            st.session_state.implementation_costs[change_key] = {
                'resources': {
                    impl_type: {
                        'values': yearly_values,
                        'salary': salary if category == "Resource" else None
                    }
                }
            }
            
            st.success("Custom row added successfully!")
            # Reset the show form flag after successful addition
            st.session_state[f"show_{category.lower()}_form_{business}"] = False
            st.rerun()

def main():
    st.title("Implementation Planning")
    
    # Create main tabs
    tab1, tab2 = st.tabs(["Implementation Details", "Cost Summary"])
    
    with tab1:
        for business in ["Business A", "Business B"]:
            st.header(business)
            
            # Resource Implementation Table
            st.subheader("Resource Implementation")
            
            # Add custom resource button
            if st.button(f"Add Custom Resource for {business}", key=f"add_resource_{business}"):
                st.session_state[f"show_resource_form_{business}"] = True
            
            if st.session_state.get(f"show_resource_form_{business}", False):
                add_custom_row(business, "Resource")
            
            resource_df = create_editable_table(st.session_state.changes, st.session_state.records, business, "Resource")
            
            if resource_df is not None:
                # Show change details first
                with st.expander("View Change Details", expanded=False):
                    for change in st.session_state.changes:
                        record = next((r for r in st.session_state.records 
                                     if r['id'] == change['record_id'] and 
                                     r['business'] == business and 
                                     r['category'] == "Resource"), None)
                        if record:
                            st.markdown(f"**{', '.join(record['functions'])}**")
                            st.markdown(create_change_message(change, record))
                            st.divider()
                
                # Create the editable dataframe
                edited_df = st.data_editor(
                    resource_df,
                    disabled=['Change', 'Implementation Type'],
                    hide_index=True,
                    key=f"resource_table_{business}"
                )
                
                # Update costs when table is edited
                update_costs(edited_df, business, "Resource")
            
            else:
                st.info("No resource changes recorded")
            
            # Technology Implementation Table
            st.subheader("Technology Implementation")
            
            # Add custom technology button
            if st.button(f"Add Custom Technology for {business}", key=f"add_tech_{business}"):
                st.session_state[f"show_tech_form_{business}"] = True
            
            if st.session_state.get(f"show_tech_form_{business}", False):
                add_custom_row(business, "Technology")
            
            tech_df = create_editable_table(st.session_state.changes, st.session_state.records, business, "Technology")
            
            if tech_df is not None:
                # Show change details first
                with st.expander("View Change Details", expanded=False):
                    for change in st.session_state.changes:
                        record = next((r for r in st.session_state.records 
                                     if r['id'] == change['record_id'] and 
                                     r['business'] == business and 
                                     r['category'] == "Technology"), None)
                        if record:
                            st.markdown(f"**{record['tech_name']}**")
                            st.markdown(create_change_message(change, record))
                            st.divider()
                
                # Create the editable dataframe
                edited_df = st.data_editor(
                    tech_df,
                    disabled=['Change', 'Implementation Type'],
                    hide_index=True,
                    key=f"tech_table_{business}"
                )
                
                # Update costs when table is edited
                update_costs(edited_df, business, "Technology")
            
            else:
                st.info("No technology changes recorded")
            
            st.divider()
    
    with tab2:
        st.header("Implementation Cost Summary")
        
        for business in ["Business A", "Business B"]:
            st.subheader(business)
            
            total_by_type, changes_by_type = calculate_total_costs(business)
            
            # Create summary tables
            resource_summary = []
            tech_summary = []
            
            for impl_type in IMPLEMENTATION_TYPES["Resource"]:
                yearly_costs = total_by_type[impl_type]
                resource_summary.append({
                    'Implementation Type': impl_type,
                    **{f'Year {i+1}': f'${cost:,.2f}' for i, cost in enumerate(yearly_costs)},
                    'Total': f'${sum(yearly_costs):,.2f}'
                })
            
            for impl_type in IMPLEMENTATION_TYPES["Technology"]:
                yearly_costs = total_by_type[impl_type]
                tech_summary.append({
                    'Implementation Type': impl_type,
                    **{f'Year {i+1}': f'${cost:,.2f}' for i, cost in enumerate(yearly_costs)},
                    'Total': f'${sum(yearly_costs):,.2f}'
                })
            
            # Display resource summary
            st.markdown("#### Resource Implementation Costs")
            st.dataframe(
                pd.DataFrame(resource_summary),
                hide_index=True,
                use_container_width=True
            )
            
            # Display technology summary
            st.markdown("#### Technology Implementation Costs")
            st.dataframe(
                pd.DataFrame(tech_summary),
                hide_index=True,
                use_container_width=True
            )
            
            # Display total implementation cost
            total_cost = sum(sum(costs) for costs in total_by_type.values())
            st.metric("Total Implementation Cost", f"${total_cost:,.2f}")
            
            # Show detailed breakdown in expander
            with st.expander("View Implementation Details"):
                for impl_type, changes in changes_by_type.items():
                    if changes:
                        st.markdown(f"**{impl_type}**")
                        for item in changes:
                            change, record = item['change'], item['record']
                            yearly_values = item['yearly_values']
                            
                            if record['category'] == "Resource":
                                st.markdown(f"- {', '.join(record['functions'])}")
                                # Calculate costs using assumptions for resources
                                costs = [v * st.session_state.assumptions[business]['Implementation'][impl_type] 
                                       for v in yearly_values]
                                st.markdown(f"  - Resources by year: {yearly_values}")
                                st.markdown(f"  - Costs by year: {[f'${c:,.2f}' for c in costs]}")
                            else:
                                # For technology, use the values directly as costs
                                st.markdown(f"- {record['tech_name']}")
                                st.markdown(f"  - Costs by year: {[f'${v:,.2f}' for v in yearly_values]}")
                        st.divider()
            
            st.divider()

if __name__ == "__main__":
    main()