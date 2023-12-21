from google.cloud import firestore

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json(".\\keys\\firestore-key.json")

docs = db.collection('exercises').stream()

ex_group = {}

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

print(ex_group)
