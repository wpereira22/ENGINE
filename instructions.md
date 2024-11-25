Updated Development Plan for Cost Savings Analysis Application

1. Project Overview

Develop a Python-based application using Streamlit for the user interface to analyze cost savings between the current state and future state of resources and technology for two businesses (Business A and Business B). The application will allow users to input data, adjust parameters, perform scenario analyses, and visualize cost savings over time. Data persistence is important, so the application will include functionality to save and load data.

2. Requirements Analysis

2.1 Data Requirements

    •    Common Fields for Resources and Technology/Vendor:
    •    Business: Indicates whether the item belongs to Business A or Business B.
    •    Category: Specifies whether the item is a Resource or Technology.
    •    Function: The role or purpose (e.g., cooking, cleaning for resources; software, hardware for technology).
    •    Count/Quantity: Number of units or people.
    •    Location: Onshore or Offshore (for resources); On-premise or Cloud (for technology).
    •    Cost Assumptions:
    •    Unit Cost: Salary cost per person for resources or cost per unit for technology.
    •    Total Cost: Calculated as Count × Unit Cost.
    •    Time Component:
    •    Implementation Year: The year in which changes occur (e.g., Year 1, Year 3).
    •    Comments Field: For additional notes or explanations.
    •    Relationships:
    •    Items are linked by Business and Function.
    •    Functions may have specific technologies associated with them.
    •    Data Persistence:
    •    Ability to save and load data to and from files (e.g., CSV or JSON).

2.2 Functional Requirements

    •    Data Input and Editing:
    •    Input current and future state data for both resources and technology/vendors.
    •    Add new items in the future state that are not present in the current state.
    •    Edit existing entries and adjust parameters such as counts and costs.
    •    Toggle Views and Filters:
    •    Switch between Current State and Future State.
    •    Switch between Business A and Business B.
    •    Toggle between Resource and Technology categories.
    •    Apply filters based on Function or other attributes.
    •    Parameter Adjustments:
    •    Adjust the number of resources or technology units.
    •    Move resources between onshore and offshore statuses.
    •    Modify cost assumptions (e.g., salary costs, technology costs).
    •    Schedule when changes occur using the Time Component.
    •    Scenario Analysis:
    •    Perform “what-if” analyses by adjusting parameters.
    •    Compare cost savings between different scenarios.
    •    Visualization:
    •    Display charts or graphs showing cost savings over time.
    •    Consolidate data for resources and technology in the same visualization.
    •    User Interface:
    •    Utilize Streamlit to create an interactive and user-friendly UI.
    •    Design pages that are clear and intuitive for data input and visualization.
    •    Data Persistence:
    •    Implement functionality to save the current state of data.
    •    Load previously saved data for continued analysis.

3. System Design

3.1 Architecture Overview

    •    Front-End:
    •    Use Streamlit for building the UI.
    •    Streamlit allows for interactive widgets and real-time updates.
    •    Back-End:
    •    Use Pandas for data manipulation and calculations.
    •    Organize data using data classes or structured dataframes.
    •    Implement calculation logic for costs and savings.
    •    Visualization:
    •    Use Matplotlib or Plotly within Streamlit for charting.
    •    Data Storage:
    •    Use CSV or JSON files for data persistence.
    •    Implement functions to read and write data to these files.

3.2 Data Model Design

    •    Data Structures:

import pandas as pd
from dataclasses import dataclass

@dataclass
class Item:
    business: str          # 'Business A' or 'Business B'
    category: str          # 'Resource' or 'Technology'
    function: str          # e.g., 'Cooking', 'Cleaning', 'Software'
    count: int             # Number of people or units
    location: str          # 'Onshore', 'Offshore', 'On-premise', 'Cloud'
    unit_cost: float       # Salary per person or cost per unit
    implementation_year: int  # Year when the change occurs
    comments: str          # Additional notes

    def total_cost(self):
        return self.count * self.unit_cost


    •    DataFrames:
    •    Current State DataFrame: Holds the current state data for all items.
    •    Future State DataFrame: Holds the future state data, including new items.
    •    Both DataFrames include all the fields specified in the Item class.
    •    Calculations:
    •    Anticipated Cost: Calculated per item using total_cost().
    •    Cost Savings: Difference between current and future state costs over time.
    •    Time Component Handling:
    •    Use a timeline (e.g., a range of years) to map when changes occur.
    •    Aggregate costs per year based on implementation_year.

3.3 Backend Logic

    •    Data Input Functions:
    •    Functions to add, edit, and delete items in the dataframes.
    •    Validation to ensure data integrity (e.g., non-negative counts and costs).
    •    Calculation Functions:
    •    Compute total costs for current and future states.
    •    Calculate cost savings per year based on implementation years.
    •    Aggregate costs and savings for resources and technology.
    •    Data Persistence Functions:
    •    Save dataframes to CSV or JSON files.
    •    Load dataframes from files into the application.
    •    Scenario Analysis Functions:
    •    Apply parameter adjustments and recalculate costs.
    •    Store different scenarios for comparison.

3.4 User Interface Design

Overall Layout:

    •    Sidebar:
    •    State Toggle: Radio buttons to select ‘Current State’ or ‘Future State’.
    •    Business Selector: Dropdown to choose ‘Business A’ or ‘Business B’.
    •    Category Selector: Toggle to switch between ‘Resource’ and ‘Technology’.
    •    Filters: Multi-select for Functions or other attributes.
    •    Data Persistence: Buttons to ‘Save Data’ and ‘Load Data’.
    •    Main Page:
    •    Data Entry Form:
    •    Fields for all item attributes.
    •    ‘Add Item’ and ‘Update Item’ buttons.
    •    Data Table:
    •    Displays the items based on current selections.
    •    Includes edit and delete buttons for each entry.
    •    Parameter Adjustment Controls:
    •    Sliders or input fields for counts and unit costs.
    •    Dropdowns for location and implementation year.
    •    Visualization Area:
    •    Cost Savings Chart:
    •    Line or bar chart showing costs over time for current and future states.
    •    Highlight cost savings between states.
    •    Interactive elements to update the chart in real-time.

Page Flow and Interaction:

    1.    Select Business and State:
    •    User chooses ‘Business A’ or ‘Business B’ and ‘Current State’ or ‘Future State’.
    2.    Select Category:
    •    Toggle between ‘Resource’ and ‘Technology’ to input or view relevant data.
    3.    Data Input/Edit:
    •    Use the data entry form to add new items or edit existing ones.
    •    Input all required fields, including implementation year for future state.
    4.    Adjust Parameters:
    •    Modify counts, unit costs, or locations using sliders and inputs.
    •    Schedule changes using the implementation year selector.
    5.    View Data Table:
    •    See a tabular representation of all items based on current filters.
    •    Edit or delete items directly from the table.
    6.    Visualize Cost Savings:
    •    The cost savings chart updates automatically based on data and adjustments.
    •    Users can hover over chart elements to see detailed information.
    7.    Save and Load Data:
    •    Use the sidebar buttons to save the current data to a file.
    •    Load previously saved data to continue analysis.

Visualization Details:

    •    Cost Over Time Chart:
    •    X-Axis: Years (e.g., Year 0 to Year N).
    •    Y-Axis: Total Cost.
    •    Lines/Bars for:
    •    Current State Costs.
    •    Future State Costs.
    •    Cost Savings (highlighted area or separate line).
    •    Interactivity:
    •    Selecting different businesses, states, or categories updates the chart.
    •    Adjusting parameters reflects immediately in the visualization.

4. Implementation Plan

4.1 Technology Stack

    •    Programming Language: Python 3.x
    •    Libraries and Frameworks:
    •    Streamlit: For building the UI.
    •    Install with pip install streamlit.
    •    Pandas: For data manipulation.
    •    Install with pip install pandas.
    •    Plotly: For interactive charts within Streamlit.
    •    Install with pip install plotly.
    •    Dataclasses: For structured data models (built-in with Python 3.7+).
    •    JSON/CSV Modules: For data persistence.

4.2 Development Steps

    •    Step 1: Set Up Development Environment
    •    Install Python 3.x and necessary libraries.
    •    Initialize a new project directory.
    •    Step 2: Define Data Models
    •    Implement the Item class using dataclasses.
    •    Ensure methods for calculating total cost and cost savings are included.
    •    Step 3: Develop Backend Logic
    •    Create functions for data input, editing, and deletion.
    •    Implement calculations for costs and cost savings.
    •    Develop data persistence functions to save and load data.
    •    Step 4: Build the User Interface with Streamlit
    •    Sidebar Components:
    •    State Toggle (Current/Future).
    •    Business Selector (Business A/B).
    •    Category Selector (Resource/Technology).
    •    Filters and Data Persistence Buttons.
    •    Main Page Components:
    •    Data Entry Form:
    •    Use st.form() to encapsulate input fields and submission buttons.
    •    Data Table:
    •    Display using st.dataframe() or st.table().
    •    Include action buttons for editing and deleting entries.
    •    Parameter Adjustments:
    •    Use st.slider() and st.number_input() for interactive controls.
    •    Visualization Area:
    •    Embed Plotly charts using st.plotly_chart().
    •    Step 5: Integrate Backend and Frontend
    •    Connect user inputs to backend data structures.
    •    Ensure that changes in data reflect immediately in the UI and visualizations.
    •    Implement callback functions to handle events like adding or updating items.
    •    Step 6: Implement Data Persistence
    •    Use pandas.to_csv() or pandas.to_json() to save dataframes.
    •    Use pandas.read_csv() or pandas.read_json() to load dataframes.
    •    Provide options for users to choose file paths or names.
    •    Step 7: Finalize Visualization
    •    Fine-tune the cost savings chart for clarity and aesthetics.
    •    Add tooltips and interactivity to enhance user experience.

5. Considerations and Recommendations

    •    Streamlit Advantages:
    •    Allows for rapid development of interactive UIs.
    •    Simplifies the integration of Python code and visualizations.
    •    Data Persistence:
    •    Ensure that saving and loading functions handle exceptions gracefully.
    •    Validate data when loading to prevent corruption or errors.
    •    User Interface Clarity:
    •    Keep the UI intuitive by grouping related controls.
    •    Use clear labels and help texts to guide the user.
    •    Scalability:
    •    Structure the code modularly to facilitate future enhancements.
    •    Consider implementing user authentication if the application evolves.
    •    Testing:
    •    While formal testing plans are omitted, it’s crucial to test the application thoroughly during development.
    •    Verify that all functionalities work as expected with various input scenarios.

6. Conclusion

This development plan provides a detailed roadmap for creating a Python application using Streamlit to analyze cost savings between the current and future states of resources and technology for two businesses. By focusing on specific backend logic, data structures, and user interface design, the plan ensures clarity and comprehensiveness for implementation.

If further adjustments or clarifications are needed, they can be incorporated to align the application more closely with the intended use case and user expectations.