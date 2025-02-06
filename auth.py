import hashlib
import random
import string
from db import get_db_connection
from flask import request, jsonify

def hash_password(password):
	return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
	chars = string.ascii_lowercase + string.digits
	return ''.join(random.choices(chars, k=128))

def register():
	data = request.get_json()
	name = data.get('name')
	email = data.get('email')
	password = hash_password(data.get('password'))
	
	conn = get_db_connection()
	cur = conn.cursor()
	
	try:
		cur.execute(
			"INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
			(name, email, password)
		)
		user_id = cur.fetchone()[0]
		conn.commit()
		return jsonify({'message': 'Пользователь зарегистрирован', 'user_id': user_id}), 201
	except psycopg2.IntegrityError:
		conn.rollback()
		return jsonify({'error': 'Email уже зарегистрирован'}), 400
	finally:
		cur.close()
		conn.close()

def login():
	data = request.get_json()
	email = data.get('email')
	password = hash_password(data.get('password'))

	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
	user = cur.fetchone()
	
	if not user or user['password_hash'] != password:
		return jsonify({'error': 'Неверный email или пароль'}), 401
	
	session_token = generate_session_token()
	cur.execute(
		"INSERT INTO sessions (user_id, session_token) VALUES (%s, %s)",
		(user['id'], session_token)
	)
	conn.commit()
	
	cur.close()
	conn.close()
	
	response = jsonify({'message': 'Успешный вход'})
	response.set_cookie('session_token', session_token)
	return response

def authenticate():
	session_token = request.cookies.get('session_token')
	
	if not session_token:
		return None

	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	cur.execute(
		"SELECT user_id FROM sessions WHERE session_token = %s",
		(session_token,)
	)
	session = cur.fetchone()
	
	cur.close()
	conn.close()

	if session:
		return session['user_id']
	return None

def check_role(required_roles):
	user_id = authenticate()
	if not user_id:
		return None, jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT roles.name 
		FROM users 
		JOIN roles ON users.role_id = roles.id 
		WHERE users.id = %s
	""", (user_id,))
	role = cur.fetchone()

	cur.close()
	conn.close()

	if role and role[0] in required_roles:
		return user_id, None, None
	else:
		return None, jsonify({'error': 'Доступ запрещен'}), 403
