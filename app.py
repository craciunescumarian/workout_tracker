import streamlit as st
import pandas as pd
import json
import sys
import os
from datetime import datetime
from database import add_value, fetch_data
from streamlit import runtime
from streamlit.web import cli as stcli

# Function to initialize exercises from JSON
def initialize_exercises():
    # Check if JSON file exists and load it; otherwise, initialize with empty dictionary
    if os.path.exists('exercise_data.json') and os.path.getsize('exercise_data.json') > 0:
        with open('exercise_data.json', 'r') as file:
            st.session_state['dynamic_exercises'] = json.load(file)
    else:
        # If JSON is missing or empty, initialize with an empty structure
        st.session_state['dynamic_exercises'] = {}

# Save the current exercises to JSON file to persist changes
def save_exercises_to_json():
    with open('exercise_data.json', 'w') as file:
        json.dump(st.session_state['dynamic_exercises'], file)

# Function to fetch data as DataFrame from MongoDB
@st.cache_data(show_spinner=False)
def fetch_data_as_dataframe(user):
    data = fetch_data()  
    df = pd.DataFrame(data)
    return df[df['user'] == user] 

# Function to create the input form for exercises
def exercise_input_tab(muscle_group):
    # Exercises loaded dynamically from session state
    exercises = st.session_state['dynamic_exercises'].get(muscle_group, [])

    for exercise in exercises:
        # Fetch data for the specific exercise
        df = fetch_data_as_dataframe(st.session_state['user'])
        exercise_data = df[df['exercise'] == exercise].copy()

        # Placeholder dataframe if no data exists
        if exercise_data.empty:
            exercise_data = pd.DataFrame({'date': pd.to_datetime([]), 'weight': [], 'exercise': []})

        # Convert 'date' to datetime and sort
        exercise_data['date'] = pd.to_datetime(exercise_data['date'])
        exercise_data.sort_values(by='date', inplace=True)
        exercise_data['formatted_date'] = exercise_data['date'].dt.strftime('%m/%d')

        # Display title, chart, and table
        st.markdown(f"""<div style="border: 3px solid #FFA500; padding: 3px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                        <h4 style="color:#FFA500;">{exercise}</h4></div>""", unsafe_allow_html=True)
        st.line_chart(exercise_data.set_index('formatted_date')['weight'], height=200)

        # Create two columns for form and table
        col1, col2 = st.columns(2)
        table_placeholder = col1.empty()

        display_exercise_table(table_placeholder, exercise_data)

        # Column 2: Input form
        with col2:
            value = st.number_input(f"Enter weight for {exercise}:", min_value=1, key=f"{muscle_group}_{exercise}_weight_input")
            date = st.date_input("Select date:", value=datetime.today().date(), key=f"{muscle_group}_{exercise}_date_input")

            if st.button('Submit', key=f"{muscle_group}_{exercise}_submit"):
                add_value(st.session_state['user'], exercise, value, str(date))
                st.success(f'Weight added for {st.session_state["user"]} in {exercise}!')

                new_entry = pd.DataFrame({'date': [pd.to_datetime(date)], 'weight': [value], 'exercise': [exercise]})
                exercise_data = pd.concat([exercise_data, new_entry], ignore_index=True)
                exercise_data.sort_values(by='date', inplace=True)
                display_exercise_table(table_placeholder, exercise_data)

    # Option to add a new exercise
    new_exercise = st.text_input(f"Add a new exercise to {muscle_group}:", key=f"new_{muscle_group}_exercise")
    if st.button("Add Exercise", key=f"add_{muscle_group}_exercise") and new_exercise:
        if new_exercise not in st.session_state['dynamic_exercises'].get(muscle_group, []):
            st.session_state['dynamic_exercises'].setdefault(muscle_group, []).append(new_exercise)
            save_exercises_to_json()  # Save the updated exercises list
            st.rerun()

# Display exercise table
def display_exercise_table(placeholder, exercise_data):
    exercise_data['date'] = pd.to_datetime(exercise_data['date'], errors='coerce')
    table_data = exercise_data[['date', 'weight']].copy()
    table_data['status'] = '-'
    table_data['date'] = table_data['date'].dt.strftime('%Y-%m-%d')
    table_data.rename(columns={'date': 'Time', 'weight': 'Weight'}, inplace=True)

    previous_weight = None
    for index, row in table_data.iterrows():
        if previous_weight is not None:
            if row['Weight'] > previous_weight:
                table_data.loc[index, 'status'] = '🟢⬆️'
            elif row['Weight'] == previous_weight:
                table_data.loc[index, 'status'] = '🟡➡️'
            else:
                table_data.loc[index, 'status'] = '🔴⬇️'
        previous_weight = row['Weight']

    table_data.sort_values(by='Time', ascending=False, inplace=True)
    placeholder.dataframe(table_data, height=300)

# Main application page
def main_app_page():
    st.title(f'Workout Tracker - {st.session_state["user"]}')
    if st.button('Back to User Selection'):
        st.session_state['show_main'] = False
        st.rerun()

    stored_values_df = fetch_data_as_dataframe(st.session_state['user'])
    muscle_groups = st.session_state['dynamic_exercises'].keys()
    tabs = st.tabs(muscle_groups)

    for muscle_group, tab in zip(muscle_groups, tabs):
        with tab:
            exercise_input_tab(muscle_group)

# Welcome page
def welcome_page():
    st.title("Workout Tracker")
    st.write("Welcome! Please select a user to continue.")
    user = st.selectbox('Select a user:', ['user1', 'user2'])
    if st.button('Continue'):
        if user:
            st.session_state['user'] = user
            st.session_state['show_main'] = True
            st.rerun()

# Initialize exercises and app flow
def main():
    if 'show_main' not in st.session_state:
        st.session_state['show_main'] = False
    if 'dynamic_exercises' not in st.session_state:
        initialize_exercises()
    if st.session_state.get('show_main', False) and 'user' in st.session_state:
        main_app_page()
    else:
        welcome_page()

# App initialization
if __name__ == '__main__':
    if runtime.exists():    
        main()
    else:    
        sys.argv = ['streamlit', 'run', sys.argv[0]]    
        sys.exit(stcli.main())
