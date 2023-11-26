import streamlit as st
import functions as func
import datetime as dt
import streamlit_authenticator as stauth

def app():
    credentials = func.get_credentials()

    authenticator = stauth.Authenticate(credentials.cred_obj, "workout_app", "abcdef", cookie_expiry_days=30)

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
                    st.session_state[state] = dt.datetime.now()
      
        def form():
            # Create Entry Form
            st.write("Enter your workout session details")

            date = st.date_input("Date of Session", format='MM/DD/YYYY', key='date')
            exercise_group = st.selectbox(
                'Select the exercise group',
                ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                index=None,
                placeholder='Select a group',
                key='group'
                )

            # Select Exercise
            if st.session_state.group != None:
                ex_list = func.form_data.get_exercise(st.session_state.group.lower())
                exercise = st.selectbox(
                    'Select Exercise', ex_list, index=None, placeholder='Select Exercise', key='exercise')
            else:
                ex_list = func.form_data.get_exercise(None)
                exercise = st.selectbox(
                    'Select Exercise', ex_list, index=None, placeholder='Select Exercise', key='exercise')
            
            # Sets
            sets = st.selectbox('Select the set you are on', (range(1,6)), index=None, placeholder='Select a set', key='set')

            # SuperSets
            super_set = st.toggle('Was this a Superset', value=False, key='superset')

            # Weight
            weight = st.select_slider('What was the weight of the lift?', options=range(10,351), key='weight')
            
            # Total
            count = st.select_slider('What was the total number of reps', options=range(1,101), key='count')

            # Fail Set
            fail = st.toggle('Did you fail the set?', value=False, key='fail')
                
            # Submit Button
            submit_results = None
            form_data = {
                'datetime' : st.session_state.date,
                'name' : st.session_state.name,
                'category' : st.session_state.group,
                'exercise' : st.session_state.exercise,
                'sets' : st.session_state.set,
                'weight' : st.session_state.weight,
                'superset' : st.session_state.superset,
                'count' : st.session_state.count,
                'fail' : st.session_state.fail
            }
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("Submit", kwargs=form_data, on_click=func.form_data.insert_data):
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
        user_data = func.form_data.get_user_data()
              
        rows = len(user_data.index) * 45

        # Format Dataframe Columns
        st.dataframe(
            user_data,
            #height=rows,
            column_config={
                "datetime": st.column_config.DateColumn("Date"),
                "name": "Lifter",
                "category": "Group",
                "exercise": "Exercise",
                "sets": "Set",
                "weight": "Weight",
                "superset": "Superset",
                "count": "Total",
                "fail": "Failed"
            },
            hide_index=True
        )