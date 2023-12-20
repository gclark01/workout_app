import streamlit as st
from google.cloud import firestore
import streamlit_authenticator as stauth

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("keys\\firestore-key.json")

# Create new user Form
user = st.text_input("User Name")
name = st.text_input("Full Name")
password = st.text_input("Enter a password", type="password")
submit = st.button("Create User")

# Convert new_password to string and generate hashed password
hash_pass = stauth.Hasher([password]).generate()

if submit:
    ref = db.collection("users").document()
    ref.set({
        "user": user,
        "name": name,
        "password": hash_pass
    })

# Read all of the documents and display as dataframe
ref = db.collection("users")
docs = ref.stream()
items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, docs))
st.dataframe(items)