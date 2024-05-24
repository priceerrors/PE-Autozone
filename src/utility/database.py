from pymongo import MongoClient, UpdateOne
from datetime import datetime
import json, os

class DatabaseHandler():
    def __init__(self):
        # Load the connection data from the config
        with open("../database/config.json", "r") as json_file:
            connection_data = json.load(json_file)
        username = connection_data['db-username']
        password = connection_data['db-password']
        # Create the connection string
        connection_string = f"mongodb+srv://{username}:{password}@autozonemain.bo3jzru.mongodb.net/"
        self.client = MongoClient(connection_string)
        self.collection = self.client['products']['products']


    def save_product(self, product) -> None:
        """Add a new product to the database"""
        if self.collection.find_one({"_id": product["sku"]}):
            
            self.collection.update_one({"_id": product["sku"]}, {"$push": {"historical_pricing": {"price": product["price"], "date": datetime.now()}}})
        else:

            new_add_product = product.copy()
            new_add_product["_id"] = new_add_product.pop("sku")
            new_add_product["historical_pricing"] = [{"price": new_add_product.pop("price"), "date": datetime.now()}]

            self.collection.insert_one(new_add_product)

    def load_product(self, product_id: str ) -> dict:
        """Load products from mongodb and find them"""
        product_from_db = self.collection.find_one({"_id": product_id})
        return product_from_db

    def update_product(self, product_id: str, update_data: dict ) -> None:
        """Update a product in the database"""
        self.collection.update_one({"_id": product_id}, {"$set": update_data})