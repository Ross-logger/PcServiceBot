import json
import sqlite3

db = sqlite3.connect('database.tg')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS Users ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tele_id INTEGER, "
                "tele_nick TEXT, "
                "number TEXT, "
                "name TEXT, "
                "problem TEXT, "
                "state TEXT)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS UserPhotos ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "photo TEXT)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS CallLaterUsers ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tele_id TEXT, "
                "tele_nick TEXT, "
                "number TEXT)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS ServiceCentres ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tele_id TEXT, "
                "group_id TEXT,"
                "owner_tele_nick TEXT, "
                "owner_name TEXT, "
                "service_name TEXT,"
                "number TEXT,"
                "address TEXT,"
                "photo_room TEXT,"
                "photo_building TEXT,"
                "photo_equipment TEXT,"
                "description TEXT)"
                )
    db.commit()


async def cmd_start_db(user_id, user_nick):
    user = cur.execute("SELECT * FROM Users WHERE tele_id == {id}".format(id=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO Users (tele_id, tele_nick) VALUES (?, ?)", (user_id, user_nick))
        db.commit()


async def add_order_db(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO Users (tele_id, tele_nick, name, number, problem) VALUES (?, ?, ?, ?, ?)",
                    (data['tele_id'], data['tele_nick'], data['name'], data['number'], data['problem']))

        user_id = data['tele_id']

        if data['photo']:
            cur.execute("INSERT INTO UserPhotos (user_id, photo) VALUES (?, ?)", (user_id, data['photo']))

        db.commit()


async def add_new_service(state):
    async with state.proxy() as data:
        cur.execute(
            "INSERT INTO ServiceCentres (tele_id, owner_tele_nick, owner_name, service_name, number, address, "
            "photo_room, photo_building, photo_equipment, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data['tele_id'], data['owner_tele_nick'], data['owner_name'], data['service_name'], data['number'],
             data['address'], data['photo_room'], data['photo_building'],
             data['photo_equipment'], data['description'])
        )
        db.commit()


async def call_later_db(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO Users (tele_id, tele_nick, number) VALUES (?, ?, ?)",
                    (data['tele_id'], data['tele_nick'], data['number']))
        db.commit()
