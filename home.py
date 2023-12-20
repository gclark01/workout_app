import streamlit as st
from methods import database as dbase
import streamlit_authenticator as stauth

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

        st.subheader('Get Big Workouts is a website created for users to manage workout progress')
        st.markdown('Created by: [Geoff Clark](https://www.linkedin.com/in/geoff-clark-23a1b049/)')
        st.markdown('Contact via mail: [geoff.clark@hotmail.com]')