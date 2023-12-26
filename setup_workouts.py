import streamlit as st
from google.cloud import firestore
import pandas as pd
from methods import database as dbase
from methods import workout_form as wf
from itertools import product
import numpy as np
import datetime as dt

st.set_page_config(
    layout="wide"
)

# Function to update editor
# def callback(**kwargs):
#     for key, values in kwargs.items():
#         st.write(f"Key {key} : Value {values}")
        
#         edited_rows = st.session_state[values]["edited_rows"]
#         for idx, value in edited_rows.items():
#             st.write(f"Id: {idx}, Value: {value}")


# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

# Create Columns for choices
col1, col2, col3, col4 = st.columns(4)

# Get Lifters
with col1:
    users = dbase.fetch_users()
    name = [user["name"] for user in users]
    lifters = st.multiselect("Select Lifters for Session", name, placeholder="Lifters")

# Get Exercise Group
with col2:
    groups = st.multiselect(
                    'Select Exercise Group',
                    ('Back', 'Biceps', 'Chest', 'Core', 'Legs', 'Shoulders', 'Triceps'),
                    placeholder='Select a group',
                    key='group'
                    )

# Sets
with col3:
    sets = st.selectbox('Select the set you are on', (range(1,6)), placeholder='Select a set', key='set')

# Select Exercise
with col4:
    if groups:
        exercises = wf.get_exercise(groups)
        selectEx = st.multiselect("Select Exercises", exercises, placeholder="Exercises", default=None)
    else:
        exercises  = wf.get_exercise(None)
        selectEx = st.multiselect("Select Exercises", exercises, placeholder="Exercises", default=None)

# Get Exercises & Create Dictionary
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
combinations = [
    (dt.datetime.today().date(), lifter, group, exercise, set_num, bool(False), np.nan, np.nan, bool(False))
    for lifter, exercise, group in product(lifters, selectEx, ex_group.keys())
    for set_num in range(1, sets + 1)
    if exercise in ex_group[group]
]

# Create a pandas DataFrame
df = pd.DataFrame(columns=["Date", "Lifter", "Exercise Group", "Exercise", "Set", "Superset", "Weight", "Reps", "Failed"])

# Add the combinations to the DataFrame
df = pd.concat([df, pd.DataFrame(combinations, columns=df.columns)], ignore_index=True)

# Display the DataFrame
for lifter in lifters:
        st.markdown(
            f'''
            Lifter: :blue[{lifter}] | Date: :blue[{dt.datetime.today().date()}]
            '''
                    )
        if not groups:
            cols = st.columns(1)
        else:
            cols = st.columns(len(groups))
        for group in groups:
            with cols[groups.index(group)]:
                st.markdown(
                    f'''
                    Exercise Group: :blue[{group}]
                    '''
                            )
                df_mod = df[(df["Lifter"] == lifter) & (df["Exercise Group"] == group)].copy()
                df_mod["Superset"] = False
                df_mod["Failed"] = False
                with st.form(f"form_{lifter}_{group}"):
                    edited_data = st.data_editor(
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
                        hide_index=True)
   
                    submit_button = st.form_submit_button(f"Record Data for {group}", on_click=wf.add_data_new, args=(edited_data, f"lifter_{lifters.index(lifter)}_{groups.index(group)}", ))

                    if submit_button:
                        st.info("Successfully saved results")
                    
            