from flask import request, jsonify
from db import get_db_connection
from auth import authenticate
from logger import log_action

def get_cart():
	user_id = authenticate()
	if not user_id:
		log_action(None, 'get_cart', 'failure', 'Authentication required')
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
	cart = cur.fetchone()

	if not cart:
		cur.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (user_id,))
		cart_id = cur.fetchone()[0]
		conn.commit()
	else:
		cart_id = cart[0]

	cur.execute("""
		SELECT products.id, products.name, products.price, cart_items.quantity
		FROM cart_items
		JOIN products ON cart_items.product_id = products.id
		WHERE cart_items.cart_id = %s
	""", (cart_id,))

	items = cur.fetchall()
	cur.close()
	conn.close()

	cart_items = [{'product_id': item[0], 'name': item[1], 'price': float(item[2]), 'quantity': item[3]} for item in items]
	log_action(user_id, 'get_cart', 'success', f'Retrieved cart with {len(cart_items)} items')
	return jsonify(cart_items)

def add_to_cart():
	user_id = authenticate()
	if not user_id:
		log_action(None, 'add_to_cart', 'failure', 'Authentication required')
		return jsonify({'error': 'Необходима авторизация'}), 401

	data = request.get_json()
	product_id = data.get('product_id')
	quantity = data.get('quantity')

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
	cart = cur.fetchone()

	if not cart:
		cur.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (user_id,))
		cart_id = cur.fetchone()[0]
	else:
		cart_id = cart[0]

	cur.execute("""
		INSERT INTO cart_items (cart_id, product_id, quantity)
		VALUES (%s, %s, %s)
		ON CONFLICT (cart_id, product_id)
		DO UPDATE SET quantity = cart_items.quantity + %s
	""", (cart_id, product_id, quantity, quantity))

	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'add_to_cart', 'success', f'Added product {product_id} (quantity: {quantity}) to cart')
	return jsonify({'message': 'Товар добавлен в корзину'}), 201

def remove_from_cart(product_id):
	user_id = authenticate()
	if not user_id:
		log_action(None, 'remove_from_cart', 'failure', 'Authentication required')
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
	cart = cur.fetchone()

	if not cart:
		log_action(user_id, 'remove_from_cart', 'failure', 'Cart not found')
		return jsonify({'error': 'Корзина пуста'}), 404

	cart_id = cart[0]
	cur.execute("DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))

	if cur.rowcount == 0:
		log_action(user_id, 'remove_from_cart', 'failure', f'Product {product_id} not found in cart')
		return jsonify({'error': 'Товар не найден в корзине'}), 404

	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'remove_from_cart', 'success', f'Removed product {product_id} from cart')
	return jsonify({'message': 'Товар удален из корзины'}), 200

