import streamlit as st
import pandas as pd
from io import StringIO
import json

uploaded_participants_file = st.file_uploader('Participants', type = 'csv', accept_multiple_files = False)
if uploaded_participants_file is not None:
    df_participants = pd.read_csv(uploaded_participants_file)
    st.write(df_participants)

uploaded_config_file = st.file_uploader('Configuration', type = 'json', accept_multiple_files = False)
if uploaded_config_file is not None:
    json_content = json.load(uploaded_config_file)
    st.write(json_content)
             