import streamlit as st
import pandas as pd
import datetime as dt
from sqlalchemy import text

# Create sql connection
conn = st.connection('workout_db', type='sql')

class get_credentials:
    def fetch_users():
        with conn.session as s:
            sql_query = text("SELECT * FROM users")
            result = s.execute(sql_query)
            return result.all()

    def convert(list):
        headers = ('id', 'name', 'fullname', 'password')
        result = []
        
        for values in list:
            if len(headers) == len(values):
                res = dict(zip(headers, values))
                result.append(res)

        return result

    users = fetch_users()
    user_dict = convert(users)

    usernames = [user["name"] for user in user_dict]
    fullname = [user["fullname"] for user in user_dict]
    hashed_passwords = [user["password"] for user in user_dict]

    cred_obj = {"usernames": {}}
    for un, name, pw in zip(usernames, fullname, hashed_passwords):
        user_dict = {"name":name, "password":pw}
        cred_obj["usernames"].update({un:user_dict})

class form_data:
    
    # Insert data with connection
    def insert_data(**kwargs):
        with conn.session as s:
            sql_query = text(
                'INSERT INTO data (datetime, name, category, exercise, sets, weight, superset, count, fail) '
                'VALUES (:datetime, :name, :category, :exercise, :sets, :weight, :superset, :count, :fail);'
            )
            s.execute(sql_query, kwargs)
            s.commit()
    
    # Exercise Query Function
    def get_exercise(exercises):
        with conn.session as s:
            sql_query = text("SELECT ex_type FROM exercises WHERE ex_group = :group")
            result = s.execute(sql_query, {"group": exercises})
            return [row[0] for row in result] 

    # Query and get Dataframe
    def get_user_data():
        with conn.session as s:
            sql_query = text('select * from data where datetime = :date and name = :name')
            result = s.execute(sql_query, {'date': dt.date.today(), 'name': st.session_state.name})
        df = pd.DataFrame(result)
        if not df.empty:
            # Clean up Dataframe
            # Drop Index
            df = df.drop(['id'], axis=1)
            # Update Int to Bool
            dict = {0:False, 1:True}
            df = df.replace({"fail": dict})
            return df
        else:
            return df


    