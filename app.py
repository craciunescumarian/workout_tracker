import streamlit as st
import sqlite3
import pandas as pd
from database import create_connection

# Function to fetch data as DataFrame
def fetch_data():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM workouts", conn)
    conn.close()
    return df

# Function to add an integer value to the database
def add_value(value, date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO workouts (value, date) VALUES (?, ?)', (value, date))
    conn.commit()
    conn.close()

# Streamlit UI
st.title('Integer Input')

# Input for integer value
value = st.number_input("Enter an integer value:", min_value=1)
date = st.date_input("Select date:")
if st.button('Submit'):
    add_value(value, str(date))
    st.success('Value added!')

# Display stored values
st.subheader("Stored Values:")
stored_values_df = fetch_data()
st.dataframe(stored_values_df)
