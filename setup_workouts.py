import streamlit as st
from google.cloud import firestore
import pandas as pd
from methods import database as dbase
from methods import workout_form as wf
from itertools import product

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

# Get Lifters
users = dbase.fetch_users()
name = [user["name"] for user in users]
lifters = st.multiselect("Select Lifters for Session", name, placeholder="Lifters")

# Get Exercise Group
exercise_group = st.multiselect(
                'Select the exercise group',
                ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                #index=None,
                placeholder='Select a group',
                key='group'
                )

# Select Exercise
if exercise_group:
    exercises = wf.get_exercise(exercise_group)
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
        exercise_type = doc_data.get('type', '')  # Use get() to avoid KeyError
        exercise_group = doc_data.get('group', '')  # Use get() to avoid KeyError
        
        if exercise_group in ex_group:
            ex_group[exercise_group].append(exercise_type)
        else:
            ex_group[exercise_group] = [exercise_type]

# Create Combo List
combinations = [(lifter, group, exercise) for lifter, exercise in product(lifters, selectEx) for group, exercises in ex_group.items() if exercise in exercises]

# Create a pandas DataFrame
df = pd.DataFrame(combinations, columns=["Lifter", "Exercise Group", "Exercise"])

# Display the DataFrame using Streamlit
st.dataframe(df, use_container_width=False)






