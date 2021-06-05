import sqlite3 as sql
from blockchain import BlockChain
from sqlite3 import Error
import os
import random


class DatabaseConnector():

    def __init__(self, filename):
        self.filename = filename
        if self.checkExistence():
            conn = sql.connect(self.filename)
            self.cursor = conn.cursor()
        else:
            self.createDatabases()

    def checkExistence(self):
        if os.path.isfile(self.filename):
            return True
        else:
            return False

    def createDatabases(self):
        self.conn = sql.connect(self.filename)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(create_user_table_query)
            self.cursor.execute(create_block_table_query)
            self.cursor.execute(create_data_table_query)
        except Error as e:
            print(e)

    def addBlock(self, block):
        self.cursor.execute(add_block_entry_query,
                            (block.index,
                             block.proof_no,
                             block.prev_hash,
                             block.timestamp))
        for dat in block.data:
            self.cursor.execute(add_data_entry_query,
                                (block.index,
                                 dat['sender'],
                                 dat['recipient'],
                                 dat['amount']))
        self.conn.commit()

    def addUser(self, user, passw):
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
        chars = []
        for i in range(16):
            chars.append(random.choice(ALPHABET))
        salt = "".joint(chars)
        self.cursor.execute(add_user_entry_query,
                            (user, salt, passw))

    def closeConnection(self):
        self.conn.close()


create_user_table_query = """CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            user VARCHAR(30) NOT NULL,
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

if __name__ == "__main__":
    blockc = BlockChain()
    d = DatabaseConnector("testDb.sqlite")
    d.addBlock(blockc.latest_block())
