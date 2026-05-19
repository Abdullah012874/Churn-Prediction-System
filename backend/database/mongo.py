from pymongo import MongoClient
import os

class MongoDBHandler:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="churnpredictor", collection_name="MLProject"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_prediction(self, data):
        """Insert a single prediction document into the collection."""
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting prediction: {e}")
            return None

    def get_all_predictions(self, model_filter=None):
        """Retrieve all prediction history, optionally filtered by selected_model."""
        try:
            query = {}
            if model_filter:
                # Match both new field name and legacy field name
                query = {"$or": [
                    {"selected_model": model_filter},
                    {"used_model": model_filter}
                ]}
            cursor = self.collection.find(query).sort("timestamp", -1)
            predictions = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for JSON serialization
                predictions.append(doc)
            return predictions
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []

    def get_prediction_by_id(self, prediction_id):
        """Retrieve a single prediction by its string ID."""
        from bson.objectid import ObjectId
        try:
            doc = self.collection.find_one({"_id": ObjectId(prediction_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            print(f"Error fetching prediction by ID: {e}")
            return None

    def delete_prediction(self, prediction_id):
        """Delete a single prediction by its string ID."""
        from bson.objectid import ObjectId
        try:
            result = self.collection.delete_one({"_id": ObjectId(prediction_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting prediction: {e}")
            return False

    def clear_all_predictions(self):
        """Delete all predictions from the collection."""
        try:
            result = self.collection.delete_many({})
            return result.deleted_count
        except Exception as e:
            print(f"Error clearing predictions: {e}")
            return 0
