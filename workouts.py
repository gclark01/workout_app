import streamlit as st
import datetime as dt
import streamlit_authenticator as stauth
from methods import workout_form as wf
from methods import database as dbase
import pandas as pd

def app():
    credentials = dbase.create_credentails()

    authenticator = stauth.Authenticate(credentials, "workout_app", "abcdef", cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status == False:
        st.error("Username/password is incorrect")

    if authentication_status == None:
        st.warning("Please enter your username and password")

    if authentication_status:
        # Sidebar Configuration
        with st.sidebar:
            welcome = st.markdown(f"*Welcome*  :blue[{st.session_state.name}]")
            authenticator.logout("Logout", "sidebar")
        
        # Column width for form buttons
        st.markdown("""
                    <style>
                        div[data-testid="column"] {
                            width: fit-content !important;
                            flex: unset;
                        }
                        div[data-testid="column"] * {
                            width: fit-content !important;
                        }
                    </style>
                    """, unsafe_allow_html=True)


        # Initialize Session States
        states = {'name':'string', 'date':'datetime', 'group':'string', 'exercise':'string'}
        for state in states.keys():
            if state not in st.session_state:
                if states.get(state) == 'string':
                    st.session_state[state] = None
                else: 
                    st.session_state[state] = dt.datetime.today().date()
        
        def form():
            # Create Entry Form
            st.write("Enter your workout session details!")

            date_value = st.date_input("Date of Session", key='date')
            exercise_group = st.selectbox(
                'Select the exercise group',
                ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                index=None,
                placeholder='Select a group',
                key='group'
                )

            # Select Exercise
            if st.session_state.group != None:
                ex_list = wf.get_exercise(st.session_state.group.lower())
                exercise = st.selectbox(
                    'Select Exercise', ex_list, index=None, placeholder='Select Exercise', key='exercise')
            else:
                ex_list = wf.get_exercise(None)
                exercise = st.selectbox(
                    'Select Exercise', ex_list, index=None, placeholder='Select Exercise', key='exercise')
            
            # Sets
            sets = st.selectbox('Select the set you are on', (range(1,6)), index=None, placeholder='Select a set', key='set')

            # SuperSets
            super_set = st.toggle('Was this a Superset', value=False, key='superset')

            # Weight
            #weight = st.select_slider('What was the weight of the lift?', options=range(10,351), key='weight')
            weight = st.selectbox('What was the weight of the lift?', range(5,501,5), index=None, placeholder="Select a weight", key='weight')
            
            # Total
            #count = st.select_slider('What was the total number of reps', options=range(1,101), key='count')
            reps = st.selectbox('What was the total number of reps', range(1,51), index=None, placeholder="Select number of reps completed", key='reps')

            # Fail Set
            fail = st.toggle('Did you fail the set?', value=False, key='fail')
                
            # Submit Button
            submit_results = None
            form_data = {
                'date' : date_value.strftime("%Y-%m-%d"),
                'name' : st.session_state.name,
                'category' : exercise_group ,
                'exercise' : exercise,
                'sets' : sets,
                'weight' : weight,
                'superset' : super_set,
                'reps' : reps,
                'fail' : fail
            }
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("Submit", kwargs=form_data, on_click=wf.add_data):
                    submit_results = True
                    #st.markdown(":green[Your workout was successfully recorded!]")
            with col2:
                if st.button("Reset Form"):
                    keys = ('group', 'date', 'exercise')
                    for key in keys:
                        del st.session_state[key]
                    st.rerun()
            
            if submit_results == True:
                st.markdown(":green[Your workout was successfully recorded!]")
        
        # Main
        form()

    
        # Get count of rows, to reduce / remove horizontal scroll bar
        user_data = wf.get_data(st.session_state.name)
        if bool(user_data): 

            # Convert List to DataFrame
            df = pd.DataFrame(user_data)

            # Order Columns
            df = df.loc[:,['date', 'name', 'category', 'exercise', 'sets', 'weight', 'superset', 'reps', 'fail']]

            # Filter DataFrame to only show values for today
            df= df[df['date'] == dt.datetime.today().strftime("%Y-%m-%d")]

            # Format Dataframe Columns
            st.dataframe(
                df,
                column_config={
                    "date": "Date",
                    "name": "Lifter",
                    "category": "Group",
                    "exercise": "Exercise",
                    "sets": "Set",
                    "weight": "Weight",
                    "superset": "Superset",
                    "reps": "Total",
                    "fail": "Failed"
                },
                hide_index=True,
                use_container_width=True
            )