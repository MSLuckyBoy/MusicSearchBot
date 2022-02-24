import sqlite3
import json

with open("config.json") as f:
    Config = json.load(f)

db = sqlite3.connect('server.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    status TEXT
)""")

db.commit()


def data_add(user_id, first_name, last_name, username, status='user'):
    if user_id in Config['admins']:
        status = "Admin"

    sql.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?)", (
            user_id,
            first_name,
            last_name,
            username,
            status
        ))
        db.commit()


def all_users_info():
    all_users = []
    keys = ["id", "first_name", "last_name", "username", "status"]
    for values in sql.execute("SELECT * FROM users"):
        i = 0
        dic = {}
        for value in values:
            dic[keys[i]] = value
            i += 1

        all_users.append(dic)

    return all_users
