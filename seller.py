from flask import request, jsonify
from db import get_db_connection
from auth import check_role
from logger import log_action

def create_product():
	user_id, error_response, status_code = check_role(['Продавец', 'Администратор'])
	if error_response:
		log_action(None, 'create_product', 'failure', 'Authorization required')
		return error_response, status_code

	data = request.get_json()
	name = data.get('name')
	price = data.get('price')
	stock = data.get('stock')

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("""
		INSERT INTO products (name, price, stock, seller_id)
		VALUES (%s, %s, %s, %s)
		RETURNING id
	""", (name, price, stock, user_id))

	product_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'create_product', 'success', f'Product {product_id} created')
	return jsonify({'message': 'Товар добавлен', 'product_id': product_id}), 201

def update_product(product_id):
	user_id, error_response, status_code = check_role(['Продавец', 'Администратор'])
	if error_response:
		log_action(None, 'update_product', 'failure', 'Authorization required')
		return error_response, status_code

	data = request.get_json()
	name = data.get('name')
	price = data.get('price')
	stock = data.get('stock')

	conn = get_db_connection()
	cur = conn.cursor()

	cur.execute("SELECT id FROM products WHERE id = %s AND seller_id = %s", (product_id, user_id))
	if not cur.fetchone():
		log_action(user_id, 'update_product', 'failure', f'Product {product_id} not found or access denied')
		cur.close()
		conn.close()
		return jsonify({'error': 'Товар не найден или доступ запрещен'}), 404

	cur.execute("""
		UPDATE products
		SET name = %s, price = %s, stock = %s
		WHERE id = %s
	""", (name, price, stock, product_id))

	conn.commit()
	cur.close()
	conn.close()

	log_action(user_id, 'update_product', 'success', f'Product {product_id} updated')
	return jsonify({'message': 'Товар обновлен'}), 200

