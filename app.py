import streamlit as st
import pandas as pd
from datetime import datetime
import json
from openpyxl import Workbook
import io
from utils import create_change_message
from session_state import init_session_state

# Page config
st.set_page_config(page_title="Cost Savings Analysis", layout="wide")

# Initialize session state
init_session_state()

# Rest of app.py remains the same... 