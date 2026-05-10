import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Giomama27.",
        port="5432"
    )