from flask import request, jsonify
from db import get_db_connection
from auth import check_role

def create_product():
	user_id, error_response, status_code = check_role(['Продавец', 'Администратор'])
	if error_response:
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
	""", (name, price, stock, user_id))

	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Товар добавлен'}), 201


def update_product(product_id):
	user_id, error_response, status_code = check_role(['Продавец', 'Администратор'])
	if error_response:
		return error_response, status_code

	data = request.get_json()
	name = data.get('name')
	price = data.get('price')
	stock = data.get('stock')

	conn = get_db_connection()
	cur = conn.cursor()

	# Проверка, что товар принадлежит продавцу
	cur.execute("SELECT id FROM products WHERE id = %s AND seller_id = %s", (product_id, user_id))
	if not cur.fetchone():
		return jsonify({'error': 'Товар не найден или доступ запрещен'}), 404

	cur.execute("""
		UPDATE products 
		SET name = %s, price = %s, stock = %s 
		WHERE id = %s
	""", (name, price, stock, product_id))

	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Товар обновлен'}), 200

