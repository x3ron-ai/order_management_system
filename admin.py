from flask import request, jsonify
from db import get_db_connection
from auth import check_role
from logger import log_action

def get_all_users():
	admin_id, error_response, status_code = check_role(['Администратор'])
	if error_response:
		log_action(admin_id, 'get_all_users', 'failure', 'Access denied')
		return error_response, status_code

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT users.id, users.username, users.email, roles.name AS role, users.balance
		FROM users
		JOIN roles ON users.role_id = roles.id
		ORDER BY users.id
	""")

	users = cur.fetchall()
	cur.close()
	conn.close()

	user_list = [
		{'id': user[0], 'username': user[1], 'email': user[2], 'role': user[3], 'balance': float(user[4])}
		for user in users
	]

	log_action(admin_id, 'get_all_users', 'success', 'All users retrieved')
	return jsonify(user_list)

def update_user_balance(user_id):
	admin_id, error_response, status_code = check_role(['Администратор'])
	if error_response:
		log_action(admin_id, 'update_user_balance', 'failure', f'Access denied for updating user {user_id}')
		return error_response, status_code

	data = request.get_json()
	new_balance = data.get('balance')

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		UPDATE users
		SET balance = %s
		WHERE id = %s
	""", (new_balance, user_id))

	if cur.rowcount == 0:
		log_action(admin_id, 'update_user_balance', 'failure', f'User {user_id} not found')
		return jsonify({'error': 'Пользователь не найден'}), 404

	conn.commit()
	cur.close()
	conn.close()

	log_action(admin_id, 'update_user_balance', 'success', f'Updated balance for user {user_id} to {new_balance}')
	return jsonify({'message': 'Баланс обновлен'}), 200

def get_all_orders():
	admin_id, error_response, status_code = check_role(['Администратор'])
	if error_response:
		log_action(admin_id, 'get_all_orders', 'failure', 'Access denied')
		return error_response, status_code

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT orders.id, users.username, orders.total_amount, orders.status, orders.created_at
		FROM orders
		JOIN users ON orders.user_id = users.id
		ORDER BY orders.created_at DESC
	""")

	orders = cur.fetchall()
	cur.close()
	conn.close()

	order_list = [
		{
			'order_id': order[0],
			'username': order[1],
			'total_amount': float(order[2]),
			'status': order[3],
			'created_at': order[4].strftime('%Y-%m-%d %H:%M:%S')
		}
		for order in orders
	]

	log_action(admin_id, 'get_all_orders', 'success', 'All orders retrieved')
	return jsonify(order_list)

