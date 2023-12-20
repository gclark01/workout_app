import streamlit as st
from google.cloud import firestore
import pandas as pd



# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

# Function to delete records
def del_row(**kwargs):
    for key, values in kwargs.items():
        record = db.collection("exercises").document(values)
        record.delete()
        st.write(f"Document {key} : {values} has been deleted.")

# Create new user Form
group = st.text_input("Exercise Category")
type = st.text_input("Exercise Name")
submit = st.button("Add Exercise")

if submit:
    ref = db.collection("exercises").document()
    ref.set({
        "group": group,
        "type": type
    })

# Query Filter
#results = ref.where(filter=FieldFilter("group", "==", "back"))

# Retun list of unique Exercise Groups
ref = db.collection("exercises")
docs = ref.stream()
items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, docs))
results = []
for item in items:
    results.append(item['group'])
groups = list(set(results))
groups = [group.capitalize() for group in groups]
st.selectbox("Filter Exercise Group", groups, index=None, key='filter')

# Create and Sort DataFrame
df = pd.DataFrame(items)
df_sort = df.sort_values(by=['group'])

# Show Data Frame
if st.session_state['filter'] == None:
    if not df_sort.empty:
        st.data_editor(
            df_sort, 
            num_rows="dynamic", 
            key='dt', 
            on_change=del_row, 
            kwargs=({"id" :df_sort.loc[df_sort["id"].idxmax()]["id"]}), 
            use_container_width=True, 
            hide_index=True)
else:
    if not df_sort.empty:
        df_filtered = df_sort.loc[df_sort['group'] == str(st.session_state['filter']).lower()]
        st.data_editor(
            df_filtered, 
            num_rows="dynamic", 
            key='dt', 
            on_change=del_row, 
            kwargs=({"id" :df_filtered.loc[df_filtered["id"].idxmax()]["id"]}), 
            use_container_width=True, 
            hide_index=True)  
