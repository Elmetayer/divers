import streamlit as st
import pandas as pd
from io import StringIO

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    d = json.load(f)
    print(d)
    st.write(dataframe)