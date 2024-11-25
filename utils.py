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