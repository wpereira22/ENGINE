import streamlit as st

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
    
    # Get all changes for this record, sorted by implementation year
    record_changes = sorted(
        [c for c in changes if str(c['record_id']) == str(record['id'])],
        key=lambda x: x['implementation_year']
    )
    
    # Apply changes sequentially up to the specified year
    for change in record_changes:
        if change['implementation_year'] <= year:
            if change['type'] == 'count_change':
                if record['category'] == 'Resource':
                    future_cost = (change['to'] * record['unit_cost']) if record['unit_cost'] is not None else 0
            elif change['type'] == 'location_change':
                if record['category'] == 'Resource':
                    new_unit_cost = st.session_state.assumptions[record['business']][change['to']]
                    future_cost = (record['count'] * new_unit_cost) if record['count'] is not None else future_cost
            elif change['type'] == 'cost_change':
                future_cost = change['to']
    
    return future_cost

def calculate_total_savings():
    """Calculate total savings over 5 years"""
    total_current = sum(r['total_cost'] * 5 for r in st.session_state.records)
    
    total_future = 0
    for record in st.session_state.records:
        yearly_costs = []
        for year in range(1, 6):  # Years 1-5
            future_cost = calculate_future_cost(record, st.session_state.changes, year)
            yearly_costs.append(future_cost)
        total_future += sum(yearly_costs)
    
    return total_current - total_future

def calculate_implementation_costs(business):
    """Calculate implementation costs for a business"""
    costs = {
        'Resource': {impl_type: [0] * 5 for impl_type in ['Rebadge', 'House Resources', 'New Hire']},
        'Technology': {impl_type: [0] * 5 for impl_type in ['Internal Build Costs']}
    }
    
    for change_key, data in st.session_state.implementation_costs.items():
        if change_key.startswith(business):
            for impl_type, impl_data in data['resources'].items():
                if isinstance(impl_data, dict):
                    values = impl_data.get('values', [0] * 5)
                    salary = impl_data.get('salary', 0)
                    
                    if impl_type in costs['Resource']:
                        cost_per_resource = salary if salary > 0 else st.session_state.assumptions[business]['Implementation'][impl_type]
                        for year in range(5):
                            costs['Resource'][impl_type][year] += float(values[year]) * float(cost_per_resource)
                    elif impl_type in costs['Technology']:
                        for year in range(5):
                            costs['Technology'][impl_type][year] += float(values[year])
    
    return costs

def calculate_total_implementation_cost():
    """Calculate total implementation cost across all businesses"""
    total_cost = 0
    for business in ['Business A', 'Business B']:
        costs = calculate_implementation_costs(business)
        for category in costs.values():
            for yearly_costs in category.values():
                total_cost += sum(yearly_costs)
    return total_cost

def calculate_net_savings():
    """Calculate net savings (total savings minus implementation costs)"""
    return calculate_total_savings() - calculate_total_implementation_cost() 