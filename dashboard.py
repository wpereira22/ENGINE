# Add business selector at the top
business_options = ["All Businesses"] + [
    st.session_state.business_names[b] for b in ['Business A', 'Business B']
]
selected_business_view = st.selectbox(
    "Select Business View",
    business_options
)

# Access session state from main app
if 'records' in st.session_state and 'changes' in st.session_state:
    records = st.session_state.records
    changes = st.session_state.changes
    
    if records:
        # Modify the data filtering based on business selection
        if selected_business_view != "All Businesses":
            # Map display name back to internal name
            internal_business_name = next(
                internal for internal, display in st.session_state.business_names.items()
                if display == selected_business_view
            )
            records = [r for r in records if r['business'] == internal_business_name]
            changes = [c for c in changes if next(
                r for r in st.session_state.records if r['id'] == c['record_id']
            )['business'] == internal_business_name] 