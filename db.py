import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
	return psycopg2.connect(
		host=os.getenv('DB_HOST'),
		database=os.getenv('DB_NAME'),
		user=os.getenv('DB_USER'),
		password=os.getenv('DB_PASSWORD')
	)

def execute_query(query, params=None):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute(query, params)
	conn.commit()
	cur.close()
	conn.close()

def fetch_all(query, params=None):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute(query, params)
	results = cur.fetchall()
	cur.close()
	conn.close()
	return results

def fetch_one(query, params=None):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute(query, params)
	result = cur.fetchone()
	cur.close()
	conn.close()
	return result

