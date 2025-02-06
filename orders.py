from flask import request, jsonify
from db import get_db_connection
from auth import authenticate

def create_order():
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	# Получаем корзину пользователя
	cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
	cart = cur.fetchone()

	if not cart:
		return jsonify({'error': 'Корзина пуста'}), 400
	
	cart_id = cart[0]

	# Получаем товары из корзины
	cur.execute("""
		SELECT products.id, products.price, cart_items.quantity
		FROM cart_items
		JOIN products ON cart_items.product_id = products.id
		WHERE cart_items.cart_id = %s
	""", (cart_id,))
	cart_items = cur.fetchall()

	if not cart_items:
		return jsonify({'error': 'Корзина пуста'}), 400

	# Рассчитываем общую сумму заказа
	total_amount = sum(item[1] * item[2] for item in cart_items)

	# Создаем заказ
	cur.execute("""
		INSERT INTO orders (user_id, total_amount) 
		VALUES (%s, %s) 
		RETURNING id
	""", (user_id, total_amount))
	order_id = cur.fetchone()[0]

	# Добавляем товары в заказ
	for product_id, price, quantity in cart_items:
		cur.execute("""
			INSERT INTO order_items (order_id, product_id, quantity, price)
			VALUES (%s, %s, %s, %s)
		""", (order_id, product_id, quantity, price))

	# Очищаем корзину
	cur.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))

	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Заказ оформлен', 'order_id': order_id}), 201


def get_orders():
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		SELECT id, total_amount, status, created_at
		FROM orders
		WHERE user_id = %s
		ORDER BY created_at DESC
	""", (user_id,))

	orders = cur.fetchall()
	cur.close()
	conn.close()

	order_list = [
		{'order_id': order[0], 'total_amount': float(order[1]), 'status': order[2], 'created_at': order[3].strftime('%Y-%m-%d %H:%M:%S')}
		for order in orders
	]

	return jsonify(order_list)


def get_order_details(order_id):
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	# Проверяем принадлежность заказа пользователю
	cur.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
	order = cur.fetchone()

	if not order:
		return jsonify({'error': 'Заказ не найден'}), 404

	# Получаем детали заказа
	cur.execute("""
		SELECT products.name, order_items.quantity, order_items.price
		FROM order_items
		JOIN products ON order_items.product_id = products.id
		WHERE order_items.order_id = %s
	""", (order_id,))

	items = cur.fetchall()
	cur.close()
	conn.close()

	order_details = [{'product_name': item[0], 'quantity': item[1], 'price': float(item[2])} for item in items]
	return jsonify(order_details)

