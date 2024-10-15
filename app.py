import streamlit as st
import pandas as pd
import sys
from datetime import datetime
from database import add_value, fetch_data
from streamlit import runtime
from streamlit.web import cli as stcli

# Function to fetch data as DataFrame from MongoDB
@st.cache_data
def fetch_data_as_dataframe(user):
    data = fetch_data()  
    df = pd.DataFrame(data)
    return df[df['user'] == user] 


# Function to create the input form for exercises
# Function to create the input form for exercises
def exercise_input_tab(muscle_group):

    # Predefined exercises
    exercises = {
        'Legs': ['Leg Extension Machine', 'Squats', 'Leg Press'],
        'Chest': ['Bench Press', 'Push Ups'],
        'Biceps': ['Bicep Curls', 'Hammer Curls'],
        'Back': ['Deadlifts', 'Pull Ups'],
        'Triceps': ['Tricep Dips', 'Skull Crushers'],
        'Shoulders': ['Shoulder Press', 'Lateral Raises'],
        'Core': ['Planks', 'Crunches'],
        'Other': []
    }

    if muscle_group in exercises:
        for exercise in exercises[muscle_group]:
            # Fetch data for the specific exercise
            df = fetch_data_as_dataframe(st.session_state['user'])
            exercise_data = df[df['exercise'] == exercise].copy()

            # Create a placeholder dataframe in case no data exists
            if exercise_data.empty:
                exercise_data = pd.DataFrame({
                    'date': pd.to_datetime([]),  # Empty datetime
                    'weight': [],  # Empty weight
                    'exercise': []  # Empty exercise
                })

            # Convert 'date' column to datetime
            exercise_data['date'] = pd.to_datetime(exercise_data['date'])
            # Sort by date
            exercise_data.sort_values(by='date', inplace=True)

            # Create a formatted date string for x-axis
            exercise_data['formatted_date'] = exercise_data['date'].dt.strftime('%m/%d')

            # Plot the line chart for weight over time (full width)
            # st.subheader(f'{exercise}')
            st.markdown(f"""
                <div style="border: 3px solid #FFA500; padding: 3px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                    <h4 style="color:#FFA500;">{exercise}</h4>
                </div>
                """, unsafe_allow_html=True)


            
            st.line_chart(
                exercise_data.set_index('formatted_date')['weight'],
                height=200  
            )

            # Create two columns: left for input form, right for table
            col1, col2 = st.columns(2)

            # Placeholder for the exercise table (always display it, even if empty)
            table_placeholder = col2.empty()

            # Display the table using the placeholder (always show the table, even if empty)
            display_exercise_table(table_placeholder, exercise_data)

            # Column 1: Display the input form (always allow input)
            with col1:
                # Input for the weight and date with today's date as default
                value = st.number_input(
                    f"Enter weight for {exercise}:", 
                    min_value=1, 
                    key=f"{muscle_group}_{exercise}_weight_input"  
                )
                date = st.date_input(
                    "Select date:", 
                    value=datetime.today().date(), 
                    key=f"{muscle_group}_{exercise}_date_input" 
                )

                # Button to add the value to the database
                if st.button('Submit', key=f"{muscle_group}_{exercise}_submit"): 
                    add_value(st.session_state['user'], exercise, value, str(date)) 
                    st.success(f'Weight added for {st.session_state["user"]} in {exercise}!')

                    # Update the existing exercise_data directly
                    new_entry = pd.DataFrame({
                        'date': [pd.to_datetime(date)],
                        'weight': [value],
                        'exercise': [exercise]
                    })

                    # Append the new row to exercise_data
                    exercise_data = pd.concat([exercise_data, new_entry], ignore_index=True)

                    # Sort the data again after adding the new row
                    exercise_data.sort_values(by='date', inplace=True)

                    # Clear previous output and re-display the updated table using the placeholder
                    display_exercise_table(table_placeholder, exercise_data)




# Function to display the exercise table
# Function to display the exercise table
def display_exercise_table(placeholder, exercise_data):
    # Create a table with time, weight, and status
    exercise_data['date'] = pd.to_datetime(exercise_data['date'], errors='coerce')
    table_data = exercise_data[['date', 'weight']].copy()
    table_data['status'] = '-' 
    table_data['date'] = table_data['date'].dt.strftime('%Y-%m-%d')  
    table_data.rename(columns={'date': 'Time', 'weight': 'Weight'}, inplace=True)

    # Ensure there are at least 2 rows for comparison
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

    # Sort the table by 'Time' in descending order to show the latest data first
    table_data.sort_values(by='Time', ascending=False, inplace=True)

    # Display the table in the placeholder
    placeholder.dataframe(table_data,height=300)

 
# Main application page after the user is selected
def main_app_page():
    st.title(f'Workout Tracker - {st.session_state["user"]}')

    # Add a Back button to return to the user selection page
    if st.button('Back to User Selection'):
        st.session_state['show_main'] = False  # Set flag to false
        st.rerun()  # Rerun the app to show the welcome page

    # Load user-specific data
    stored_values_df = fetch_data_as_dataframe(st.session_state['user'])

    # Muscle groups tabs
    muscle_groups = ['Legs', 'Chest', 'Biceps', 'Back', 'Triceps', 'Shoulders', 'Core', 'Other']
    tabs = st.tabs(muscle_groups)

    for muscle_group, tab in zip(muscle_groups, tabs):
        with tab:
            exercise_input_tab(muscle_group)


# Welcome page
def welcome_page():
    st.title("Workout Tracker")
    st.write("Welcome! Please select a user to continue.")
    
    # User selection
    user = st.selectbox('Select a user:', ['user1', 'user2'])

    # Button to proceed to the main application
    if st.button('Continue'):
        if user:  # Ensure a user is selected
            st.session_state['user'] = user  # Initialize the 'user' in session_state
            st.session_state['show_main'] = True  # Flag to show the main page
            st.rerun()  # Rerun the app to reflect the change



# Main function controlling the app flow
def main():
    # Ensure that 'show_main' and 'user' are initialized in session state
    if 'show_main' not in st.session_state:
        st.session_state['show_main'] = False

    if st.session_state.get('show_main', False) and 'user' in st.session_state:
        # Load data only once after the user is selected
        if 'stored_values_df' not in st.session_state:
            st.session_state['stored_values_df'] = fetch_data_as_dataframe(st.session_state['user'])  # Pass the user argument

        # Proceed to the main app page after user is selected
        main_app_page()
    else:
        # Show the welcome page if user not selected
        welcome_page()

        
        
# App initialization
if __name__ == '__main__':
    if runtime.exists():    
        main()
    else:    
        sys.argv = ['streamlit', 'run', sys.argv[0]]    
        sys.exit(stcli.main())
