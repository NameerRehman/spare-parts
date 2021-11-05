# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 10:38:17 2021

@author: nrehman
"""

from configparser import ConfigParser
import psycopg2
from typing import Dict
from spare_list import SparesList


class Db():
    def __init__(self,odoo,dfspares): #TODO: pass variable number of parameters in class
        self.df_purchprice = odoo.getPurchasePrice()
        self.df_spares = dfspares
        #print(self.df_spares)
        #print(self.df_purchprice)
        

    def load_connection_info(ini_filename: str) -> Dict[str, str]:
        parser = ConfigParser()
        parser.read(ini_filename)
        print(parser.items("postgresql"))
        # Create a dictionary of the variables stored under the "postgresql" section of the .ini
        setup_info = {param[0]: param[1] for param in parser.items("postgresql")}
        return setup_info
    
        
    def create_db(conn_info: Dict[str, str],) -> None:
        # Connect just to PostgreSQL with the user loaded from the .ini file
        psql_connection_string = f"user={conn_info['user']} password={conn_info['password']}"
        conn = psycopg2.connect(psql_connection_string)
        cur = conn.cursor()
    
        # "CREATE DATABASE" requires automatic commits
        conn.autocommit = True
        q_createdb = f"CREATE DATABASE {conn_info['database']}"
    
        try:
            cur.execute(q_createdb)
        except Exception as e:
            print(f"{type(e).__name__}: {e} when executing create_db")
            print(f"Query: {cur.query}")
            #cur.close()
        else:
            # Revert autocommit settings
            conn.autocommit = False
    
    
    def query(sql_query: str, conn: psycopg2.extensions.connection,
                     cur: psycopg2.extensions.cursor) -> None:
        try:
            # Execute the table creation query
            cur.execute(sql_query)
        except Exception as e:
            print(f"{type(e).__name__}: {e} when executing create_table")
            print(f"Query: {cur.query}")
            conn.rollback()
            cur.close()
        else:
            # To take effect, changes need be committed to the database
            conn.commit()
    
    