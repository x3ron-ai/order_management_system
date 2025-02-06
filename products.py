from flask import request, jsonify
from db import get_db_connection
from auth import authenticate

def create_product():
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401
	
	data = request.get_json()
	name = data.get('name')
	description = data.get('description')
	price = data.get('price')
	quantity = data.get('quantity')

	conn = get_db_connection()
	cur = conn.cursor()
	
	cur.execute(
		"INSERT INTO products (seller_id, name, description, price, quantity) VALUES (%s, %s, %s, %s, %s) RETURNING id",
		(user_id, name, description, price, quantity)
	)
	product_id = cur.fetchone()[0]
	conn.commit()
	
	cur.close()
	conn.close()

	return jsonify({'message': 'Товар создан', 'product_id': product_id}), 201

def edit_product(product_id):
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	data = request.get_json()
	name = data.get('name')
	description = data.get('description')
	price = data.get('price')
	quantity = data.get('quantity')

	conn = get_db_connection()
	cur = conn.cursor()
	
	cur.execute(
		"UPDATE products SET name = %s, description = %s, price = %s, quantity = %s WHERE id = %s AND seller_id = %s",
		(name, description, price, quantity, product_id, user_id)
	)
	
	if cur.rowcount == 0:
		conn.rollback()
		return jsonify({'error': 'Товар не найден или нет прав на редактирование'}), 404
	
	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Товар обновлен'}), 200

def delete_product(product_id):
	user_id = authenticate()
	if not user_id:
		return jsonify({'error': 'Необходима авторизация'}), 401

	conn = get_db_connection()
	cur = conn.cursor()
	
	cur.execute("DELETE FROM products WHERE id = %s AND seller_id = %s", (product_id, user_id))
	
	if cur.rowcount == 0:
		conn.rollback()
		return jsonify({'error': 'Товар не найден или нет прав на удаление'}), 404

	conn.commit()
	cur.close()
	conn.close()

	return jsonify({'message': 'Товар удален'}), 200

def get_products():
	conn = get_db_connection()
	cur = conn.cursor()
	
	cur.execute("SELECT id, name, description, price, quantity FROM products")
	products = cur.fetchall()
	
	cur.close()
	conn.close()

	product_list = [{'id': p[0], 'name': p[1], 'description': p[2], 'price': float(p[3]), 'quantity': p[4]} for p in products]
	return jsonify(product_list)

