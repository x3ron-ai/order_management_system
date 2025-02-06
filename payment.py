from flask import request, jsonify
from db import get_db_connection
from auth import authenticate
from logger import log_action

def process_payment(order_id):
	user_id = authenticate()
	if not user_id:
		log_action(None, 'process_payment', 'failure', 'Authentication required')
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT total_amount, status
		FROM orders
		WHERE id = %s AND user_id = %s
	""", (order_id, user_id))
	order = cur.fetchone()

	if not order:
		log_action(user_id, 'process_payment', 'failure', f'Order {order_id} not found')
		return jsonify({'error': 'Заказ не найден'}), 404

	total_amount, status = order

	if status == 'Оплачен':
		log_action(user_id, 'process_payment', 'failure', f'Order {order_id} already paid')
		return jsonify({'error': 'Заказ уже оплачен'}), 400

	cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
	balance = cur.fetchone()[0]

	if balance < total_amount:
		log_action(user_id, 'process_payment', 'failure', f'Insufficient balance for order {order_id}')
		return jsonify({'error': 'Недостаточно средств на балансе'}), 400

	cur.execute("""
		UPDATE users
		SET balance = balance - %s
		WHERE id = %s
	""", (total_amount, user_id))

	cur.execute("""
		UPDATE orders
		SET status = 'Оплачен'
		WHERE id = %s
	""", (order_id,))

	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'process_payment', 'success', f'Order {order_id} paid successfully')
	return jsonify({'message': 'Оплата успешна'}), 200

