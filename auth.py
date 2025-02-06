import hashlib
import random
import string
from db import get_db_connection
from flask import request, jsonify
from psycopg2.extras import RealDictCursor
from logger import log_action

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
		log_action(user_id, 'register', 'success', f'User {email} registered')
		return jsonify({'message': 'Пользователь зарегистрирован', 'user_id': user_id}), 201
	except psycopg2.IntegrityError:
		conn.rollback()
		log_action(None, 'register', 'failure', f'Email {email} уже зарегистрирован')
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
		log_action(None, 'login', 'failure', f'Неудачный вход для {email}')
		return jsonify({'error': 'Неверный email или пароль'}), 401

	session_token = generate_session_token()
	cur.execute(
		"INSERT INTO sessions (user_id, session_token) VALUES (%s, %s)",
		(user['id'], session_token)
	)
	conn.commit()

	log_action(user['id'], 'login', 'success', f'User {email} logged in')

	cur.close()
	conn.close()

	response = jsonify({'message': 'Успешный вход'})
	response.set_cookie('session_token', session_token)
	return response

def authenticate():
	session_token = request.cookies.get('session_token')

	if not session_token:
		log_action(None, 'authenticate', 'failure', 'No session token provided')
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
		log_action(session['user_id'], 'authenticate', 'success', 'User authenticated via session')
		return session['user_id']
	
	log_action(None, 'authenticate', 'failure', 'Invalid session token')
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
		log_action(user_id, 'check_role', 'success', f'Role {role[0]} verified')
		return user_id, None, None
	else:
		log_action(user_id, 'check_role', 'failure', f'Access denied for role {role[0] if role else "None"}')
		return None, jsonify({'error': 'Доступ запрещен'}), 403

