from db import get_db_connection 

def log_action(user_id, action, status, details=''):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("""
		INSERT INTO logs (user_id, action, status, details)
		VALUES (%s, %s, %s, %s)
	""", (user_id, action, status, details))
	conn.commit()
	cur.close()
	conn.close()

