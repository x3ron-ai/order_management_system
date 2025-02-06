from flask import request, jsonify
from db import get_db_connection
from auth import check_role

def get_all_users():
	_, error_response, status_code = check_role(['Администратор'])
	if error_response:
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

	return jsonify(user_list)


def update_user_balance(user_id):
	_, error_response, status_code = check_role(['Администратор'])
	if error_response:
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
		return jsonify({'error': 'Пользователь не найден'}), 404

	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Баланс обновлен'}), 200


def get_all_orders():
	_, error_response, status_code = check_role(['Администратор'])
	if error_response:
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

	return jsonify(order_list)

