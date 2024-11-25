# Initialize implementation costs with some sample data
if 'implementation_costs' not in st.session_state:
    st.session_state.implementation_costs = {
        # Business A Implementation Costs
        'Business A_0_2024-01-15T00:00:00': {
            'resources': {
                'Rebadge': [2, 3, 0, 0, 0],
                'House Resources': [1, 2, 2, 1, 0],
                'New Hire': [0, 1, 2, 0, 0]
            }
        },
        'Business A_2_2024-01-17T00:00:00': {
            'resources': {
                'Internal Build Costs': [85000, 170000, 85000, 0, 0]
            }
        },
        # Business B Implementation Costs
        'Business B_3_2024-01-18T00:00:00': {
            'resources': {
                'Rebadge': [3, 2, 0, 0, 0],
                'House Resources': [2, 2, 1, 0, 0],
                'New Hire': [1, 2, 0, 0, 0]
            }
        },
        'Business B_5_2024-01-20T00:00:00': {
            'resources': {
                'Internal Build Costs': [130000, 260000, 130000, 0, 0]
            }
        }
    } 