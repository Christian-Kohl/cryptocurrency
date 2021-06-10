import sqlite3 as sql
import blockchain
from sqlite3 import Error
import os
import random


class DatabaseConnector():

    def __init__(self, filename):
        self.filename = filename
        if not self.checkExistence():
            self.createDatabases()

    def checkExistence(self):
        if os.path.isfile(self.filename):
            return True
        else:
            return False

    def createDatabases(self):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        try:
            cursor.execute(create_user_table_query)
            cursor.execute(create_block_table_query)
            cursor.execute(create_data_table_query)
            self.addUser("Christian", "password")
        except Error as e:
            print(e)
        conn.commit()
        conn.close()

    def addBlock(self, block):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute(add_block_entry_query,
                       (block.index,
                        block.proof_no,
                        block.prev_hash,
                        block.timestamp))
        for dat in block.data:
            cursor = conn.cursor()
            cursor.execute(add_data_entry_query,
                           (block.index,
                            dat['sender'],
                            dat['recipient'],
                            dat['quantity']))
        conn.commit()
        conn.close()

    def addUser(self, user, passw):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
        chars = []
        for i in range(16):
            chars.append(random.choice(ALPHABET))
        salt = "".join(chars)
        cursor.execute(add_user_entry_query,
                       (user, salt, passw))
        conn.commit()
        conn.close()

    def updateUser(self, u, a):
        update_user = f"UPDATE users SET amount= {a} WHERE user = '{u}';"
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute(update_user)
        conn.commit()
        conn.close()

    def loadUsers(self):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute(select_all_users)
        users = cursor.fetchall()
        cursor.close()
        conn.commit()
        return users

    def loadData(self):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute(select_all_data)
        data = cursor.fetchall()
        cursor.close()
        conn.commit()
        return data

    def loadBlocks(self):
        conn = sql.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute(select_all_blocks)
        blocks = cursor.fetchall()
        conn.commit()
        return blocks


create_user_table_query = """CREATE TABLE IF NOT EXISTS users (
                            user VARCHAR(30) PRIMARY KEY,
                            salt VARCHAR(10) NOT NULL,
                            pass TEXT NOT Null,
                            amount INTEGER NOT NULL
                            )"""

create_block_table_query = """CREATE TABLE IF NOT EXISTS blocks (
                            id INTEGER PRIMARY KEY,
                            proof_no TEXT NOT NULL,
                            prev_hash TEXT NOT NULL,
                            timestamp TEXT NOT NULL
                            )"""

create_data_table_query = """CREATE TABLE IF NOT EXISTS data(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            block_id INTEGER,
                            sender INTEGER NOT NULL,
                            recipient INTEGER NOT NULL,
                            amount INTEGER NOT NULL,
                            FOREIGN KEY (block_id) REFERENCES blocks(id),
                            FOREIGN KEY (sender) REFERENCES users(id),
                            FOREIGN KEY (recipient) REFERENCES users(id)
                            )"""

add_user_entry_query = """INSERT INTO users(user, salt, pass, amount)
                            VALUES(?, ?, ?, 0)"""

add_data_entry_query = """INSERT INTO data(block_id, sender, recipient, amount)
                            VALUES(?, ?, ?, ?)"""

add_block_entry_query = """INSERT INTO blocks(id, proof_no, prev_hash, timestamp)
                            VALUES(?, ?, ?, ?)"""

select_all_users = """SELECT user, pass, amount FROM Users"""

select_all_blocks = """SELECT * FROM blocks ORDER BY id"""

select_all_data = """SELECT * FROM data"""

if __name__ == "__main__":
    blockc = blockchain.BlockChain()
    d = DatabaseConnector("testDb.sqlite")
    d.addBlock(blockc.latest_block())
    d.addUser("christian", "password")
    os.remove("testDb.sqlite")
