import streamlit as st
import pandas as pd
from io import StringIO
import json

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    json_content = json.load(uploaded_file)
    st.write(json_content)