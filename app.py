import streamlit as st
import pandas as pd
from database import add_value, fetch_data
from datetime import datetime

# Streamlit UI
st.title('Integer Input')

# Input for integer value
value = st.number_input("Enter an integer value:", min_value=1)
date = st.date_input("Select date:")
if st.button('Submit'):
    add_value(value, str(date))
    st.success('Value added!')

    # Fetch and display stored values after submission
    stored_values_df = pd.DataFrame(fetch_data())
    st.subheader("Stored Values:")
    st.dataframe(stored_values_df)

else:
    # Display current stored values at the start
    stored_values_df = pd.DataFrame(fetch_data())
    st.subheader("Stored Values:")
    st.dataframe(stored_values_df)