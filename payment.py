from flask import request, jsonify
from db import get_db_connection
from auth import authenticate

def process_payment(order_id):
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	# Проверка, принадлежит ли заказ пользователю и не оплачен ли он уже
	cur.execute("""
		SELECT total_amount, status 
		FROM orders 
		WHERE id = %s AND user_id = %s
	""", (order_id, user_id))
	order = cur.fetchone()

	if not order:
		return jsonify({'error': 'Заказ не найден'}), 404

	total_amount, status = order

	if status == 'Оплачен':
		return jsonify({'error': 'Заказ уже оплачен'}), 400

	# Проверка баланса пользователя
	cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
	balance = cur.fetchone()[0]

	if balance < total_amount:
		return jsonify({'error': 'Недостаточно средств на балансе'}), 400

	# Списание средств и обновление статуса заказа
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

	return jsonify({'message': 'Оплата успешна'}), 200

