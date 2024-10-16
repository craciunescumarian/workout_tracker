from pymongo import MongoClient

# MongoDB connection
def create_mongo_client():
    # Replace with your MongoDB Atlas connection string
    client = MongoClient("mongodb+srv://craciunescumarian:Marian123321@workout-tracker.bmwnf.mongodb.net/?retryWrites=true&w=majority&appName=workout-tracker")
    return client


# Function to add a value to the MongoDB collection
def add_value(user, exercise, weight, date):
    client = create_mongo_client()
    db = client.workout_tracker  # Use database name
    workouts_collection = db.workouts  # Use collection name
    workout_entry = {
        "user": user,
        "exercise": exercise,
        "weight": weight,
        "date": date
    }
    workouts_collection.insert_one(workout_entry)
    client.close()


# Function to fetch data from MongoDB
def fetch_data():
    client = create_mongo_client()
    db = client.workout_tracker  # Use database name
    workouts_collection = db.workouts  # Use collection name
    data = list(workouts_collection.find())
    client.close()
    return data
