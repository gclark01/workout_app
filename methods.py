import streamlit as st
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account
import json

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
            "superset": kwargs["superset"],
            "reps": int(kwargs["reps"]),
            "fail": kwargs["fail"]
        })

    def get_exercise(*args):
        """ Method to get a list of exercises based on group """

        # Create List from args
        group_list= []
        if args[0] != None:
            for tup in args:
                for lst in tup:
                    group_list.append(lst)
        else:
            group_list.append("Empty")

        # Get collection Exercises
        docs = db.collection("exercises")

        # Filter by group
        results = docs.where(filter=FieldFilter("group", "in", group_list)).stream()

        # Create list of dictionary items
        items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, results))

        # Create a list to return unique values
        res_list = []
        for item in items:
            res_list.append(item['type'])
        type = list(set(res_list))
        type.sort()
        return type

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
    