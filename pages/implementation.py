import streamlit as st
import pandas as pd
from datetime import datetime
from utils import create_change_message
from session_state import init_session_state, IMPLEMENTATION_TYPES

# Initialize session state
init_session_state()

def delete_implementation_entry(business, record_id, timestamp, impl_type):
    """Delete a specific implementation row"""
    change_key = f"{business}_{record_id}_{timestamp}"
    if change_key in st.session_state.implementation_costs:
        if impl_type in st.session_state.implementation_costs[change_key]['resources']:
            del st.session_state.implementation_costs[change_key]['resources'][impl_type]
            
            # If no more implementation types, remove the entire record
            if not st.session_state.implementation_costs[change_key]['resources']:
                del st.session_state.implementation_costs[change_key]
                st.session_state.records = [r for r in st.session_state.records if r['id'] != record_id]
                st.session_state.changes = [c for c in st.session_state.changes if c['record_id'] != record_id]
    
    # Force update of last_modified to trigger recalculation
    st.session_state.last_modified = datetime.now()
    st.rerun()

def create_editable_table(business, category):
    """Create an editable table with default rows for each implementation type"""
    # Get table data from session state or create default if not exists
    table_key = f"{business}_{category}_table"
    
    if table_key not in st.session_state:
        # Create default rows
        rows = []
        
        # Create a row for each implementation type
        for impl_type in IMPLEMENTATION_TYPES[category]:
            row = {
                'Description': 'No description added',  # Default description
                'Implementation Type': impl_type,
            }
            
            if category == "Resource":
                row['Salary'] = 0
            
            # Add year columns with zero values
            for year in range(1, 6):
                row[f'Year {year}'] = 0
            
            rows.append(row)
        
        # Add empty row for new entries with default values
        empty_row = {
            'Description': 'No description added',  # Default description for new row
            'Implementation Type': IMPLEMENTATION_TYPES[category][0],
            **({'Salary': 0} if category == "Resource" else {}),
            **{f'Year {i+1}': 0 for i in range(5)}
        }
        rows.append(empty_row)
        
        # Store in session state
        st.session_state[table_key] = pd.DataFrame(rows)
    
    return st.session_state[table_key]

def handle_edited_table(edited_df, business, category):
    """Handle changes to the editable table"""
    # Update the stored table data
    table_key = f"{business}_{category}_table"
    st.session_state[table_key] = edited_df
    
    # Clear existing implementation costs for this business and category
    keys_to_remove = []
    for key in st.session_state.implementation_costs:
        if key.startswith(f"{business}_") and any(impl_type in key for impl_type in IMPLEMENTATION_TYPES[category]):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state.implementation_costs[key]
    
    # Add new implementation costs
    for idx, row in edited_df.iterrows():
        # Skip empty or invalid rows
        if pd.isna(row.get('Implementation Type')):
            continue
            
        description = str(row.get('Description', ''))
        impl_type = row['Implementation Type']
        
        # Get values with defaults
        yearly_values = []
        for i in range(5):
            try:
                value = float(row.get(f'Year {i+1}', 0))
                yearly_values.append(value if not pd.isna(value) else 0)
            except (ValueError, TypeError):
                yearly_values.append(0)
        
        # Handle salary
        try:
            salary = float(row.get('Salary', 0)) if category == "Resource" else None
            if pd.isna(salary):
                salary = None
        except (ValueError, TypeError):
            salary = None
        
        # Create unique key for this entry
        change_key = f"{business}_{impl_type}_{idx}"
        
        # Only add non-zero entries or entries with descriptions
        if any(v != 0 for v in yearly_values) or description.strip():
            if change_key not in st.session_state.implementation_costs:
                st.session_state.implementation_costs[change_key] = {'resources': {}}
            
            st.session_state.implementation_costs[change_key]['resources'][impl_type] = {
                'values': yearly_values,
                'salary': salary,
                'description': description
            }
    
    # Force update of last_modified to trigger recalculation
    st.session_state.last_modified = datetime.now()

def calculate_total_costs(business_internal):
    """Calculate total implementation costs for a business"""
    total_by_type = {impl_type: [0] * 5 for impl_type in 
                     IMPLEMENTATION_TYPES["Resource"] + IMPLEMENTATION_TYPES["Technology"]}
    
    for change_key, data in st.session_state.implementation_costs.items():
        if change_key.startswith(business_internal):
            for impl_type, impl_data in data['resources'].items():
                if isinstance(impl_data, dict):
                    values = impl_data.get('values', [0] * 5)
                    salary = impl_data.get('salary')
                    
                    # For resources, multiply count by salary or assumption cost
                    if impl_type in IMPLEMENTATION_TYPES["Resource"]:
                        # Fix salary comparison
                        cost_per_resource = salary if salary is not None and float(salary) > 0 else \
                            st.session_state.assumptions[business_internal]['Implementation'][impl_type]
                        for year in range(5):
                            total_by_type[impl_type][year] += float(values[year]) * float(cost_per_resource)
                    
                    # For technology, use direct costs
                    elif impl_type in IMPLEMENTATION_TYPES["Technology"]:
                        for year in range(5):
                            total_by_type[impl_type][year] += float(values[year])
    
    return total_by_type

def main():
    st.title("Implementation Planning")
    
    # Create main tabs
    tab1, tab2 = st.tabs(["Implementation Details", "Cost Summary"])
    
    with tab1:
        for business_internal, business_display in st.session_state.business_names.items():
            st.header(business_display)
            
            with st.expander("View Change Summary"):
                resource_changes = []
                tech_changes = []
                
                for change in st.session_state.changes:
                    record = next((r for r in st.session_state.records 
                                 if r['id'] == change['record_id'] and 
                                 r['business'] == business_internal), None)
                    if record:
                        if record['category'] == "Resource":
                            resource_changes.append((change, record))
                        else:
                            tech_changes.append((change, record))
                
                if resource_changes:
                    st.markdown("##### Resource Changes")
                    for change, record in resource_changes:
                        st.markdown(f"**{', '.join(record['functions'])}**")
                        st.markdown(create_change_message(change, record))
                        st.divider()
                
                if tech_changes:
                    st.markdown("##### Technology Changes")
                    for change, record in tech_changes:
                        st.markdown(f"**{record['tech_name']}**")
                        st.markdown(create_change_message(change, record))
                        st.divider()
                
                if not resource_changes and not tech_changes:
                    st.info("No changes recorded for this business")
            
            # Resource Implementation Table
            st.subheader("Resource Implementation")
            
            resource_df = create_editable_table(business_internal, "Resource")
            
            edited_df = st.data_editor(
                resource_df,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "Description": st.column_config.TextColumn(
                        "Description",
                        help="Enter description",
                        width="medium",
                    ),
                    "Implementation Type": st.column_config.SelectboxColumn(
                        "Implementation Type",
                        help="Select implementation type",
                        width="medium",
                        options=IMPLEMENTATION_TYPES["Resource"]
                    )
                },
                key=f"resource_table_{business_internal}"
            )
            
            # Handle table edits
            handle_edited_table(edited_df, business_internal, "Resource")
            
            # Technology Implementation Table
            st.subheader("Technology Implementation")
            
            tech_df = create_editable_table(business_internal, "Technology")
            
            edited_df = st.data_editor(
                tech_df,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "Description": st.column_config.TextColumn(
                        "Description",
                        help="Enter description",
                        width="medium",
                    ),
                    "Implementation Type": st.column_config.SelectboxColumn(
                        "Implementation Type",
                        help="Select implementation type",
                        width="medium",
                        options=IMPLEMENTATION_TYPES["Technology"]
                    )
                },
                key=f"tech_table_{business_internal}"
            )
            
            # Handle table edits
            handle_edited_table(edited_df, business_internal, "Technology")
            
            st.divider()
    
    with tab2:
        st.header("Implementation Cost Summary")
        
        for business_internal, business_display in st.session_state.business_names.items():
            st.subheader(business_display)
            
            total_by_type = calculate_total_costs(business_internal)
            
            # Create summary tables
            resource_summary = []
            tech_summary = []
            
            # Resource Implementation Costs
            st.markdown("#### Resource Implementation Costs")
            resource_df = pd.DataFrame([
                {
                    'Implementation Type': impl_type,
                    **{f'Year {i+1}': f'${cost:,.2f}' for i, cost in enumerate(total_by_type[impl_type])},
                    'Total': f'${sum(total_by_type[impl_type]):,.2f}'
                }
                for impl_type in IMPLEMENTATION_TYPES["Resource"]
            ])
            st.dataframe(resource_df, hide_index=True, use_container_width=True)
            
            # Technology Implementation Costs
            st.markdown("#### Technology Implementation Costs")
            tech_df = pd.DataFrame([
                {
                    'Implementation Type': impl_type,
                    **{f'Year {i+1}': f'${cost:,.2f}' for i, cost in enumerate(total_by_type[impl_type])},
                    'Total': f'${sum(total_by_type[impl_type]):,.2f}'
                }
                for impl_type in IMPLEMENTATION_TYPES["Technology"]
            ])
            st.dataframe(tech_df, hide_index=True, use_container_width=True)
            
            # Display total implementation cost
            total_cost = sum(sum(costs) for costs in total_by_type.values())
            st.metric("Total Implementation Cost", f"${total_cost:,.2f}")
            
            st.divider()

if __name__ == "__main__":
    main()