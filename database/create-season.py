"""
Module to create a SQLite database and a table within it.
"""

import sqlite3
from sqlite3 import Error

def create_table_with_cols(conn):
    """
    Function to create a table in the SQLite database.
    """
    try:
        sql = '''CREATE TABLE IF NOT EXISTS seasonflightplan (
                    ID integer PRIMARY KEY,
                    DATE datetime,
                    AC text,
                    ACTYPE text,
                    DEP text,
                    ARR text,
                    ROUTE text,
                    FLT_NO text,
                    STD integer,
                    STA integer,
                    FREQ text,
                    "FROM" integer,
                    "TO" integer
                );'''
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def create_connection_season_fpl():
    """
    Function to create a connection to the SQLite database.
    """
    conn = None
    try:
        # Creates a SQLite database named 'seasonflightplan.db'
        conn = sqlite3.connect('database/seasonflightplan.db') 
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def main():
    """
    Main function to create a database connection and table.
    """
    # Create a database connection
    conn = create_connection_season_fpl()

    # Create tables
    if conn is not None:
        create_table_with_cols(conn)  # Corrected function name
    else:
        print("Error! cannot create the database connection.")

    # Close the connection
    conn.close()

if __name__ == '__main__':
    main()