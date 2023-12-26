import streamlit as st
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account
import json
import pandas as pd
import numpy as np

# Authenticate to Firestore with the JSON account key.
#db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="workout-app-1aa96")


class database:
    """ Methods to get / set database tables """
    
    def fetch_users():
        """ Method that returns all of the users from the database as list of dictionary items """
        docs = db.collection("users").stream()
        items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, docs)) 
        return items
    
    def create_credentails():
        """ Method to create a credential object to use with the streamlit authentication module """
        # Get list of users
        users = database.fetch_users()

        # Get values from dictionary
        user = [user["user"] for user in users]
        name = [user["name"] for user in users]
        password = [user["password"][0] for user in users]

        # Create credential object to be used with streamlit authentication module
        cred_dict = {"usernames": {}}
        for un, name, pw in zip(user, name, password):
            user_dict = {"name": name, "password": pw}
            cred_dict["usernames"].update({un:user_dict})
        return cred_dict
    
class workout_form:
    """ Methods to use with the workout form """

    def add_data(**kwargs):
        """ Method to add form entry data to the data database"""

        docs = db.collection("data").document()
        docs.set({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date": kwargs["date"],
            "name": kwargs["name"],
            "category": kwargs["category"],
            "exercise": kwargs["exercise"],
            "sets": int(kwargs["sets"]),
            "weight": int(kwargs["weight"]),
            "superset": bool(kwargs["superset"]),
            "reps": int(kwargs["reps"]),
            "fail": bool(kwargs["failed"])
        })

    def add_data_new(df: pd.DataFrame, key):
            
        # Extract the list of dictionaries from st.session_state
        edited_rows = st.session_state[key]["edited_rows"]

        # Ensure key is present with the correct value
        for i in range(len(edited_rows)):
            if "Failed" not in edited_rows[i]:
                # If key is not present, add it with a default value of False
                edited_rows[i].update({"Failed": False})
            if "Superset" not in edited_rows[i]:
                edited_rows[i].update({"Superset": False})

        # Get the weight values from the dictionary
        weight_values = [int(edited_rows[i]["Weight"]) for i in range(len(edited_rows))]

        # Get the rep values from the dictionary
        rep_values = [int(edited_rows[i]["Reps"]) for i in range(len(edited_rows))]

        # Get the Superset values from the dictionary
        superset_values = [bool(edited_rows[i]["Superset"]) for i in range(len(edited_rows))]

        # Get the Failed values from the dictionary
        fail_values = [bool(edited_rows[i]["Failed"]) for i in range(len(edited_rows))]

        # Loop through each row in the DataFrame and update the columns
        for i, index in enumerate(df.index):
            df.at[index, "Weight"] = weight_values[i % len(weight_values)]
            df.at[index, "Reps"] = rep_values[i % len(rep_values)]
            df.at[index, "Superset"] = superset_values[i % len(superset_values)]
            df.at[index, "Failed"] = fail_values[i % len(fail_values)]

        # Write to database
        results = df.to_dict("index")
        for item in results:
            data = results[item]

            date = data["Date"].strftime("%Y-%m-%d")

            docs = db.collection("data").document()
            docs.set({
                "timestamp": firestore.SERVER_TIMESTAMP,
                "date": date,
                "name": data["Lifter"],
                "category": data["Exercise Group"],
                "exercise": data["Exercise"],
                "sets": int(data["Set"]),
                "weight": int(data["Weight"]),
                "superset": data["Superset"],
                "reps": int(data["Reps"]),
                "fail": data["Failed"]
            })

    def get_exercise(*args):
        """ Method to get a list of exercises based on group """

        # Create List from args
        group_list= []
        if args[0] is not None:
            for tup in args:
                for lst in tup:
                    group_list.append(lst)

        # Get collection Exercises
        docs = db.collection("exercises")

        # Filter by group only if group_list is not empty
        if group_list:
            results = docs.where("group", "in", group_list).stream()
        else:
            results = []

        # Create dictionary to store exercises organized by group
        exercises_by_group = {}

        # Populate the dictionary
        for result in results:
            exercise_data = result.to_dict()
            group = exercise_data.get('group', 'Unknown')
            exercise_name = exercise_data.get('type', 'Unknown')

            if group not in exercises_by_group:
                exercises_by_group[group] = []

            exercises_by_group[group].append(exercise_name)

        # Sort the groups and exercises
        for group, exercises_list in exercises_by_group.items():
            exercises_list.sort()

        # Build the list of strings
        formatted_strings = []
        for group, exercises_list in exercises_by_group.items():
            formatted_strings.append(f"---- {group} ----")
            formatted_strings.extend(exercises_list)

        return formatted_strings

    def get_data(name):
        """ Method to get a list of users data """

        # Get collection Data
        docs = db.collection("data")

        # Filter data
        query = (
            docs.where(filter=firestore.FieldFilter("name", "==", name))
            #.where(filter=FieldFilter("datetime", "==", date))
        )
        results = query.stream()

        # Create list of dictionary items
        items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, results))
        return items
    