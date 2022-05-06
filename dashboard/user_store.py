from dacapo import Options
from pymongo import MongoClient, ASCENDING


class UserStore:
    def __init__(self):
        """Create a user store based on the global DaCapo options."""

        options = Options.instance()

        try:
            store_type = options.type
        except RuntimeError:
            store_type = "mongo"
        if store_type == "mongo":
            self.db_host = options.mongo_db_host
            self.db_name = options.mongo_db_name + "_users"

            self.client = MongoClient(self.db_host)
            self.database = self.client[self.db_name]

            self.users = self.database["users"]
            self.users.create_index([("username", ASCENDING)], name="username", unique=True)
    
    def store_user_info(self, user_info):
        self.users.insert_one(dict(user_info))
    
    def retrieve_user_info(self, username):

        user_info = self.users.find_one(
            {"username": username}, projection={"_id": False}
        )
        return user_info