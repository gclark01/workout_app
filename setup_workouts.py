import streamlit as st
from google.cloud import firestore
import pandas as pd
from methods import database as dbase
from methods import workout_form as wf
from itertools import product
import numpy as np
import datetime as dt

st.session_state

# Function to update editor
def callback(**kwargs):
    for key, values in kwargs.items():
        st.write(f"Key {key} : Value {values}")
        
        edited_rows = st.session_state[values]["edited_rows"]
        for idx, value in edited_rows.items():
            st.write(f"Id: {idx}, Value: {value}")


# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

# Get Lifters
users = dbase.fetch_users()
name = [user["name"] for user in users]
lifters = st.multiselect("Select Lifters for Session", name, placeholder="Lifters")

# Get Exercise Group
groups = st.multiselect(
                'Select the exercise group',
                ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                placeholder='Select a group',
                key='group'
                )

# Sets
sets = st.selectbox('Select the set you are on', (range(1,6)), placeholder='Select a set', key='set')

# Select Exercise
if groups:
    exercises = wf.get_exercise(groups)
    selectEx = st.multiselect("Select Exercises to be performed", exercises, placeholder="Exercises")
else:
    exercises  = wf.get_exercise(None)
    selectEx = st.multiselect("Select Exercises to be performed", exercises, placeholder="Exercises")

# Get Exercises
ex_group = {}
docs = db.collection('exercises').stream()

for doc in docs:
    exercise_name = doc.id
    doc_data = doc.to_dict()

    if doc_data:
        exercise_type = doc_data.get('type', '') 
        exercise_group = doc_data.get('group', '') 
        
        if exercise_group in ex_group:
            ex_group[exercise_group].append(exercise_type)
        else:
            ex_group[exercise_group] = [exercise_type]

# Create Combo List
#combinations = [(lifter, group, exercise, sets, np.nan, np.nan, np.nan, np.nan) for lifter, exercise in product(lifters, selectEx) for group, exercises in ex_group.items() if exercise in exercises]

combinations = [
    (dt.datetime.today().date(), lifter, group, exercise, set_num, False, np.nan, np.nan, False)
    for lifter, exercise, group in product(lifters, selectEx, ex_group.keys())
    for set_num in range(1, sets + 1)
    if exercise in ex_group[group]
]

# Create a pandas DataFrame with empty columns
df = pd.DataFrame(columns=["Date", "Lifter", "Exercise Group", "Exercise", "Set", "Superset", "Weight", "Reps", "Failed"])

# Add the combinations to the DataFrame
df = pd.concat([df, pd.DataFrame(combinations, columns=df.columns)], ignore_index=True)

# Display the DataFrame
for lifter in lifters:
    with st.container():
        st.markdown(
            f'''
            Lifter: :blue[{lifter}] | Date: :blue[{dt.datetime.today().date()}]
            '''
                    )
        for group in groups:
            with st.container():
                st.markdown(
                    f'''
                    Exercise Group: :blue[{group}]
                    '''
                            )
                df_mod = (df
                  .where(df["Lifter"] == lifter)
                  .where(df["Exercise Group"] == group)
                  .dropna(how='all'))
                st.data_editor(
                    df_mod,
                    column_config={
                                    "Date": None,
                                    "Lifter": None,
                                    "Exercise Group": None,
                                    "Exercise": "Exercise",
                                    "Set": "Set",
                                    "Superset": "Superset",
                                    "Weight": "Weight",
                                    "Reps": "Reps",
                                    "Failed": "Failed"
                                },
                    num_rows="dynamic",
                    key=f"lifter_{lifters.index(lifter)}_{groups.index(group)}",
                    use_container_width=False, 
                    on_change=callback,
                    kwargs=({"state_key" : f"lifter_{lifters.index(lifter)}_{groups.index(group)}"}),
                    hide_index=True)