import streamlit as st
from google.cloud import firestore
import pandas as pd
from methods import database as dbase
from methods import workout_form as wf

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

# Get Lifters
users = dbase.fetch_users()
name = [user["name"] for user in users]
lifters = st.multiselect("Select Lifters for Session", name, placeholder="Lifters")

# Get Exercise Group
exercise_group = st.selectbox(
                'Select the exercise group',
                ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                index=None,
                placeholder='Select a group',
                key='group'
                )

# Get Exercises
if exercise_group != None:
    exercises = wf.get_exercise(exercise_group.lower())
    selectEx = st.multiselect("Select Exercises to be performed", exercises, placeholder="Exercises")





