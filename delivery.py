from flask import jsonify, request
from db import get_db_connection
from auth import check_role
from logger import log_action

def get_pending_deliveries():
	user_id, error_response, status_code = check_role(['Доставка', 'Администратор'])
	if error_response:
		log_action(None, 'get_pending_deliveries', 'failure', 'Access denied')
		return error_response, status_code

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT orders.id, users.username, orders.total_amount, orders.status
		FROM orders
		JOIN users ON orders.user_id = users.id
		WHERE orders.status = 'Ожидает подтверждения'
	""")

	deliveries = cur.fetchall()
	cur.close()
	conn.close()

	delivery_list = [
		{'order_id': delivery[0], 'username': delivery[1], 'total_amount': float(delivery[2]), 'status': delivery[3]}
		for delivery in deliveries
	]

	log_action(user_id, 'get_pending_deliveries', 'success', f'Retrieved {len(delivery_list)} pending deliveries')
	return jsonify(delivery_list)

def update_order_status(order_id):
	user_id, error_response, status_code = check_role(['Доставка', 'Администратор'])
	if error_response:
		log_action(None, 'update_order_status', 'failure', 'Access denied')
		return error_response, status_code

	data = request.get_json()
	new_status = data.get('status')

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		UPDATE orders
		SET status = %s
		WHERE id = %s
	""", (new_status, order_id))

	if cur.rowcount == 0:
		log_action(user_id, 'update_order_status', 'failure', f'Order {order_id} not found')
		return jsonify({'error': 'Заказ не найден'}), 404

	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'update_order_status', 'success', f'Order {order_id} status updated to {new_status}')
	return jsonify({'message': 'Статус заказа обновлен'}), 200

