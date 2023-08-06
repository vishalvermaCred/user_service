from enum import Enum

PSQL_USER_DB = "user_db"
MONGO_USER_DB = "user_db"
phone_regex = r"^(0\d{10}|[1-9]\d{9,11})$"


class Tables(Enum):
    psql_users_table = "users"
    mongo_users_table = "users_mongo"
    psql_profile_table = "profile"
    mongo_profile_table = "profile_mongo"
