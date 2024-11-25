import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Cost Savings Dashboard", layout="wide")

# Constants (keep in sync with main app)
BUSINESS_TYPES = ["Business A", "Business B"]
CATEGORIES = ["Resource", "Technology"]
FUNCTIONS = ["Development", "Testing", "Support"]

def create_change_message(change, record):
    """Create a descriptive message for a change"""
    if change['type'] == 'count_change':
        return (
            f"The number of {', '.join(record['functions'])} resources will change from "
            f"**{change['from']}** to **{change['to']}** in Year {change['implementation_year']}\n"
            f"- Impact: {'Reduction' if change['to'] < change['from'] else 'Increase'} of "
            f"**{abs(change['from'] - change['to'])}** resources\n"
            f"- Reason: {change.get('description', 'No description provided')}"
        )
    elif change['type'] == 'location_change':
        return (
            f"{', '.join(record['functions'])} team location will move from "
            f"**{change['from']}** to **{change['to']}** in Year {change['implementation_year']}\n"
            f"- Impact: Cost structure will change due to location shift\n"
            f"- Reason: {change.get('description', 'No description provided')}"
        )
    else:  # cost_change
        cost_diff = change['to'] - change['from']
        return (
            f"Annual cost will change from "
            f"**${change['from']:,}** to **${change['to']:,}** in Year {change['implementation_year']}\n"
            f"- Impact: {'Savings' if cost_diff < 0 else 'Increase'} of "
            f"**${abs(cost_diff):,}** per year\n"
            f"- Reason: {change.get('description', 'No description provided')}"
        )

def calculate_future_cost(record, changes, year=5):
    """Calculate future cost for a record based on changes for a specific year"""
    future_cost = record['total_cost']
    record_changes = [c for c in changes if c['record_id'] == record['id']]
    
    for change in record_changes:
        if change['implementation_year'] <= year:
            if change['type'] == 'count_change':
                future_cost = (change['to'] * record['unit_cost'])
            elif change['type'] == 'location_change':
                new_unit_cost = 100000 if change['to'] == 'Onshore' else 40000
                future_cost = (record['count'] * new_unit_cost)
            elif change['type'] == 'cost_change':
                future_cost = change['to']
    
    return future_cost

def create_summary_metrics(records, changes):
    """Calculate summary metrics for all businesses"""
    total_current = sum(r['total_cost'] for r in records)
    total_future = sum(calculate_future_cost(r, changes) for r in records)
    total_savings = total_current - total_future
    return total_current, total_future, total_savings

def calculate_change_impact(record, change):
    """Calculate the 5-year impact of a change"""
    if change['type'] == 'count_change':
        old_annual_cost = record['total_cost']
        new_annual_cost = change['to'] * record['unit_cost']
    elif change['type'] == 'location_change':
        old_annual_cost = record['total_cost']
        new_unit_cost = 100000 if change['to'] == 'Onshore' else 40000
        new_annual_cost = record['count'] * new_unit_cost
    elif change['type'] == 'cost_change':
        old_annual_cost = record['total_cost']
        new_annual_cost = change['to']
    else:
        return 0
    
    # Calculate impact considering implementation year
    annual_savings = old_annual_cost - new_annual_cost
    years_affected = 5 - change['implementation_year'] + 1
    total_impact = annual_savings * years_affected
    
    return total_impact

st.title("Cost Savings Dashboard")

# Add business selector at the top
selected_business_view = st.selectbox(
    "Select Business View",
    ["All Businesses", "Business A", "Business B"]
)

# Access session state from main app
if 'records' in st.session_state and 'changes' in st.session_state:
    records = st.session_state.records
    changes = st.session_state.changes
    
    if records:
        # Modify the data filtering based on business selection
        if selected_business_view != "All Businesses":
            records = [r for r in records if r['business'] == selected_business_view]
            changes = [c for c in changes if next(r for r in st.session_state.records if r['id'] == c['record_id'])['business'] == selected_business_view]
        
        # Create three columns for high-level metrics with detailed breakdowns
        col1, col2, col3 = st.columns(3)
        
        total_current, total_future, total_savings = create_summary_metrics(records, changes)
        
        # Current Cost Details
        with col1:
            st.metric(
                "Total Current Cost",
                f"${total_current:,.2f}",
            )
            with st.expander("View Details", expanded=False):
                # Resource costs by function
                st.write("**Resource Costs:**")
                for function in FUNCTIONS:
                    resource_cost = sum(r['total_cost'] for r in records 
                                     if r['category'] == 'Resource' 
                                     and function in r['functions'])
                    if resource_cost > 0:
                        st.write(f"{function}: ${resource_cost:,.2f}")
                
                st.divider()
                
                # Technology costs by function
                st.write("**Technology Costs:**")
                for function in FUNCTIONS:
                    tech_records = [r for r in records 
                                  if r['category'] == 'Technology' 
                                  and function in r['functions']]
                    for record in tech_records:
                        st.write(f"{record['tech_name']}: ${record['total_cost']:,.2f}")
        
        # Future Cost Details
        with col2:
            st.metric(
                "Total Future Cost",
                f"${total_future:,.2f}",
            )
            with st.expander("View Details", expanded=False):
                # Resource costs by function
                st.write("**Resource Costs:**")
                for function in FUNCTIONS:
                    future_resource_cost = sum(calculate_future_cost(r, changes) 
                                            for r in records 
                                            if r['category'] == 'Resource' 
                                            and function in r['functions'])
                    if future_resource_cost > 0:
                        st.write(f"{function}: ${future_resource_cost:,.2f}")
                        # Show changes inline instead of in nested expander
                        changes_for_function = [c for c in changes 
                                              if function in next(r for r in records 
                                                     if r['id'] == c['record_id'])['functions']]
                        if changes_for_function:
                            st.markdown("*Changes:*")
                            for change in changes_for_function:
                                st.markdown(f"• {change['description']} (Year {change['implementation_year']})")
                
                st.divider()
                
                # Technology costs by function
                st.write("**Technology Costs:**")
                for function in FUNCTIONS:
                    tech_records = [r for r in records 
                                  if r['category'] == 'Technology' 
                                  and function in r['functions']]
                    for record in tech_records:
                        future_cost = calculate_future_cost(record, changes)
                        st.write(f"{record['tech_name']}: ${future_cost:,.2f}")
                        # Show changes inline
                        changes_for_tech = [c for c in changes if c['record_id'] == record['id']]
                        if changes_for_tech:
                            st.markdown("*Changes:*")
                            for change in changes_for_tech:
                                st.markdown(f"• {change['description']} (Year {change['implementation_year']})")
        
        with col3:
            st.metric(
                "Total Savings",
                f"${total_savings:,.2f}",
                f"{(total_savings/total_current)*100:.1f}%" if total_current != 0 else "0%"
            )
        
        st.divider()  # Add sharp line after metrics
        
        # State toggle without divider after it
        state_toggle = st.radio(
            "View State",
            ["Current State", "Future State"],
            horizontal=True
        )
        
        # Charts with better colors
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Unit Count by Function")
            # Create data for pie chart based on selected state
            function_counts = {}
            
            if state_toggle == "Current State":
                for record in records:
                    if record['category'] == 'Resource':
                        for func in record['functions']:
                            function_counts[func] = function_counts.get(func, 0) + (record['count'] or 0)
            else:  # Future State
                for record in records:
                    if record['category'] == 'Resource':
                        record_changes = [c for c in changes if c['record_id'] == record['id'] and c['type'] == 'count_change']
                        if record_changes:
                            latest_change = max(record_changes, key=lambda x: x['implementation_year'])
                            count = latest_change['to']
                        else:
                            count = record['count']
                        for func in record['functions']:
                            function_counts[func] = function_counts.get(func, 0) + (count or 0)
            
            if function_counts:
                fig = px.pie(
                    values=list(function_counts.values()),
                    names=list(function_counts.keys()),
                    color_discrete_sequence=['#3498db', '#2ecc71', '#9b59b6'],  # Better colors
                )
                # Update to show actual values instead of percentages
                fig.update_traces(
                    textinfo='value',
                    textfont_size=14,
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
                    plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resource data available")
        
        with col2:
            st.subheader("Cost Distribution by Function")
            
            # Prepare data for bar chart
            function_costs = []
            
            for function in FUNCTIONS:
                if state_toggle == "Current State":
                    resource_cost = sum(r['total_cost'] for r in records 
                                     if function in r['functions'] 
                                     and r['category'] == 'Resource')
                    tech_cost = sum(r['total_cost'] for r in records 
                                  if function in r['functions'] 
                                  and r['category'] == 'Technology')
                else:  # Future State
                    resource_cost = sum(calculate_future_cost(r, changes) 
                                     for r in records 
                                     if function in r['functions'] 
                                     and r['category'] == 'Resource')
                    tech_cost = sum(calculate_future_cost(r, changes) 
                                  for r in records 
                                  if function in r['functions'] 
                                  and r['category'] == 'Technology')
                
                function_costs.extend([
                    {
                        'Function': function,
                        'Category': 'Resource',
                        'Cost': resource_cost
                    },
                    {
                        'Function': function,
                        'Category': 'Technology',
                        'Cost': tech_cost
                    }
                ])
            
            # Create DataFrame for visualization
            df_costs = pd.DataFrame(function_costs)
            
            # Create stacked bar chart with better colors
            fig = px.bar(
                df_costs,
                x='Function',
                y='Cost',
                color='Category',
                barmode='stack',
                color_discrete_map={
                    'Resource': '#3498db',  # Softer blue
                    'Technology': '#2ecc71'  # Softer green
                }
            )
            
            # Update layout for dark theme compatibility
            fig.update_layout(
                yaxis_title="Total Cost ($)",
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
                plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot
                yaxis=dict(
                    tickformat="$,.0f",
                    gridcolor='rgba(128,128,128,0.2)',  # Subtle grid
                    zerolinecolor='rgba(128,128,128,0.2)'  # Subtle zero line
                ),
                xaxis=dict(
                    gridcolor='rgba(128,128,128,0.2)',  # Subtle grid
                    zerolinecolor='rgba(128,128,128,0.2)'  # Subtle zero line
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Add divider before Summary of Changes
        st.divider()
        
        # Summary of Changes (renamed from Recent Changes)
        st.header("Summary of Changes")
        if changes:
            # Create tabs for Resource and Technology changes
            change_tab1, change_tab2 = st.tabs(["Resource Changes", "Technology Changes"])
            
            # Group changes by category
            resource_changes = []
            tech_changes = []
            
            for change in changes:
                record = next(r for r in st.session_state.records if r['id'] == change['record_id'])
                impact = calculate_change_impact(record, change)
                
                # Create descriptive message based on change type
                if change['type'] == 'count_change':
                    description = (
                        f"The number of {', '.join(record['functions'])} resources will change from "
                        f"**{change['from']}** to **{change['to']}** in Year {change['implementation_year']}\n"
                        f"- Impact: {'Reduction' if change['to'] < change['from'] else 'Increase'} of "
                        f"**{abs(change['from'] - change['to'])}** resources\n"
                        f"- Reason: {change.get('description', 'No description provided')}"
                    )
                elif change['type'] == 'location_change':
                    description = (
                        f"{', '.join(record['functions'])} team location will move from "
                        f"**{change['from']}** to **{change['to']}** in Year {change['implementation_year']}\n"
                        f"- Impact: Cost structure will change due to location shift\n"
                        f"- Reason: {change.get('description', 'No description provided')}"
                    )
                else:  # cost_change
                    cost_diff = change['to'] - change['from']
                    description = (
                        f"Annual cost will change from "
                        f"**${change['from']:,}** to **${change['to']:,}** in Year {change['implementation_year']}\n"
                        f"- Impact: {'Savings' if cost_diff < 0 else 'Increase'} of "
                        f"**${abs(cost_diff):,}** per year\n"
                        f"- Reason: {change.get('description', 'No description provided')}"
                    )
                
                if record['category'] == 'Technology':
                    name = f"{record['tech_name']} ({', '.join(record['functions'])})"
                else:
                    name = f"{', '.join(record['functions'])} Team"

                change_info = {
                    'description': description,
                    'original_description': change.get('description', 'No description provided'),
                    'impact': impact,
                    'record': record,
                    'timestamp': change['timestamp'],
                    'implementation_year': change['implementation_year'],
                    'name': name  # Store the formatted name
                }
                
                if record['category'] == 'Resource':
                    resource_changes.append(change_info)
                else:
                    tech_changes.append(change_info)
            
            # Sort changes by impact
            resource_changes.sort(key=lambda x: abs(x['impact']), reverse=True)
            tech_changes.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            # Display Resource Changes
            with change_tab1:
                for change_info in resource_changes:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(change_info['description'])
                        
                        with col2:
                            impact_color = "green" if change_info['impact'] > 0 else "red"
                            st.markdown(
                                f"<h2 style='color: {impact_color}; text-align: right;'>"
                                f"{'$' + format(abs(change_info['impact']), ',.0f')}</h2>",
                                unsafe_allow_html=True
                            )
                            st.caption("5-year savings impact")
                            
                            if st.button("Remove Change", key=f"del_change_{change_info['record']['id']}"):
                                change_to_remove = next(
                                    (c for c in st.session_state.changes 
                                     if c['record_id'] == change_info['record']['id'] 
                                     and c['timestamp'] == change_info['timestamp']),
                                    None
                                )
                                if change_to_remove:
                                    st.session_state.changes.remove(change_to_remove)
                                    st.rerun()
                        
                        st.divider()
            
            # Display Technology Changes
            with change_tab2:
                for change_info in tech_changes:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(change_info['description'])
                            st.markdown(f"**Technology:** {change_info['record']['tech_name']}")
                        
                        with col2:
                            impact_color = "green" if change_info['impact'] > 0 else "red"
                            st.markdown(
                                f"<h2 style='color: {impact_color}; text-align: right;'>"
                                f"{'$' + format(abs(change_info['impact']), ',.0f')}</h2>",
                                unsafe_allow_html=True
                            )
                            st.caption("5-year savings impact")
                            
                            if st.button("Remove Change", key=f"del_change_{change_info['record']['id']}_tech"):
                                change_to_remove = next(
                                    (c for c in st.session_state.changes 
                                     if c['record_id'] == change_info['record']['id'] 
                                     and c['timestamp'] == change_info['timestamp']),
                                    None
                                )
                                if change_to_remove:
                                    st.session_state.changes.remove(change_to_remove)
                                    st.rerun()
                        
                        st.divider()
        else:
            st.info("No changes recorded yet")

        # Add divider before Cost Analysis
        st.divider()
        
        # Update the Cost Analysis Table
        st.subheader("Cost Analysis by Year")
        if records:
            yearly_analysis = []
            
            for record in records:
                yearly_costs = [record['total_cost']]  # Year 0
                
                # Calculate costs for years 1-5
                for year in range(1, 6):
                    cost = calculate_future_cost(record, changes, year)
                    yearly_costs.append(cost)
                
                # Different name construction for Resource vs Technology
                if record['category'] == 'Technology':
                    name = f"{record['tech_name']} ({', '.join(record['functions'])})"
                else:
                    name = f"{', '.join(record['functions'])} Team"

                yearly_analysis.append({
                    'Name': name,
                    'Business': record['business'],
                    'Category': record['category'],
                    'Current': yearly_costs[0],
                    'Year 1': yearly_costs[1],
                    'Year 2': yearly_costs[2],
                    'Year 3': yearly_costs[3],
                    'Year 4': yearly_costs[4],
                    'Year 5': yearly_costs[5],
                    'Total 5Y Savings': sum(yearly_costs[0] - cost for cost in yearly_costs[1:])
                })
            
            df = pd.DataFrame(yearly_analysis)
            
            # Create style function for conditional formatting
            def style_changes(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                
                # Get numeric values for comparison
                for col in currency_cols[1:]:  # Skip 'Current' column
                    try:
                        current_vals = df['Current'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
                        col_vals = df[col].apply(lambda x: float(x.replace('$', '').replace(',', '')))
                        
                        # Apply colors based on comparison
                        styles.loc[col_vals < current_vals, col] = 'background-color: #c6efce; color: #006100'
                        styles.loc[col_vals > current_vals, col] = 'background-color: #ffc7ce; color: #9c0006'
                    except:
                        continue
                
                return styles
            
            # Format currency columns
            currency_cols = ['Current', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Total 5Y Savings']
            for col in currency_cols:
                df[col] = df[col].apply(lambda x: f"${x:,.2f}")
            
            # Apply styling
            styled_df = df.style\
                .apply(style_changes, axis=None)\
                .set_properties(**{'text-align': 'right'})
            
            st.dataframe(styled_df, use_container_width=True)
        
        # Add divider before Savings Projection
        st.divider()
        
        # Cost Savings Timeline
        st.subheader("Savings Projection")
        timeline_data = []
        
        for year in range(6):  # Years 0-5
            year_current = sum(r['total_cost'] for r in records)
            year_future = sum(calculate_future_cost(r, changes, year) for r in records)
            year_savings = year_current - year_future
            
            timeline_data.append({
                'Year': f'Year {year}',
                'Annual Savings': year_savings,
                'Cumulative Savings': year_savings * (year if year > 0 else 0)
            })
        
        # Create multi-line chart
        df_timeline = pd.DataFrame(timeline_data)
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_timeline['Year'],
            y=df_timeline['Annual Savings'],
            name='Annual Savings',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_timeline['Year'],
            y=df_timeline['Cumulative Savings'],
            name='Cumulative Savings',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title="Projected Savings Over Time",
            yaxis_title="Savings ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No data available. Please add some records in the main application.")
else:
    st.warning("Please add some records in the main application first.") 