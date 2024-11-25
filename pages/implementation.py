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
                    'resources': {
                        impl_type: [0] * 5 for impl_type in IMPLEMENTATION_TYPES[category]
                    }
                }
            
            # Create base row data
            base_row = {
                'Change': f"{'📋 ' + record['tech_name'] if category == 'Technology' else '📋 ' + ', '.join(record['functions'])}",
                'Implementation Type': None,
                'Year 1': 0,
                'Year 2': 0,
                'Year 3': 0,
                'Year 4': 0,
                'Year 5': 0
            }
            
            # Add rows for each implementation type
            for impl_type in IMPLEMENTATION_TYPES[category]:
                row = base_row.copy()
                row['Implementation Type'] = impl_type
                
                # Add year columns
                for year in range(5):
                    row[f'Year {year + 1}'] = st.session_state.implementation_costs[change_key]['resources'].get(impl_type, [0] * 5)[year]
                
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
                        for year in range(5):
                            st.session_state.implementation_costs[change_key]['resources'][impl_type][year] = row[f'Year {year + 1}']

def calculate_total_costs(business):
    """Calculate total implementation costs for a business"""
    total_by_type = {impl_type: [0] * 5 for impl_type in 
                     IMPLEMENTATION_TYPES["Resource"] + IMPLEMENTATION_TYPES["Technology"]}
    changes_by_type = {impl_type: [] for impl_type in 
                      IMPLEMENTATION_TYPES["Resource"] + IMPLEMENTATION_TYPES["Technology"]}
    
    for change_key, data in st.session_state.implementation_costs.items():
        if change_key.startswith(business):
            for impl_type, yearly_values in data['resources'].items():
                # For resource types, use assumptions
                if impl_type in IMPLEMENTATION_TYPES["Resource"]:
                    for year in range(5):
                        resource_count = yearly_values[year]
                        cost_per_resource = st.session_state.assumptions[business]['Implementation'][impl_type]
                        total_by_type[impl_type][year] += resource_count * cost_per_resource
                # For technology, use direct costs
                elif impl_type == "Internal Build Costs":
                    for year in range(5):
                        total_by_type[impl_type][year] += yearly_values[year]
                
                if any(yearly_values):  # If there are any non-zero values
                    # Find the associated change and record
                    _, record_id, timestamp = change_key.split('_')
                    record_id = int(record_id)
                    record = next(r for r in st.session_state.records if r['id'] == record_id)
                    change = next(c for c in st.session_state.changes if c['record_id'] == record_id)
                    
                    changes_by_type[impl_type].append({
                        'change': change,
                        'record': record,
                        'yearly_values': yearly_values
                    })
    
    return total_by_type, changes_by_type

def main():
    st.title("Implementation Planning")
    
    # Create main tabs
    tab1, tab2 = st.tabs(["Implementation Details", "Cost Summary"])
    
    with tab1:
        for business in ["Business A", "Business B"]:
            st.header(business)
            
            # Resource Implementation Table
            st.subheader("Resource Implementation")
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