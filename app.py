#
#	♠ ЗАВИСИМОСТИ ♠
#

from flask import Flask, jsonify
from auth import register, login, authenticate
from products import create_product, edit_product, delete_product, get_products
from cart import get_cart, add_to_cart, remove_from_cart
from orders import create_order, get_orders, get_order_details
from seller import create_product, update_product
from delivery import get_pending_deliveries, update_order_status
from admin import get_all_users, update_user_balance, get_all_orders
from payment import process_payment

app = Flask(__name__) # ойойой

@app.route('/register', methods=['POST'])
def register_user():
	return register()

@app.route('/login', methods=['POST'])
def login_user():
	return login()

@app.route('/products', methods=['GET'])
def list_products():
	return get_products()

@app.route('/products', methods=['POST'])
def add_product():
	return create_product()

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
	return edit_product(product_id)

@app.route('/products/<int:product_id>', methods=['DELETE'])
def remove_product(product_id):
	return delete_product(product_id)

@app.route('/cart', methods=['GET'])
def view_cart():
	return get_cart()

@app.route('/cart', methods=['POST'])
def add_item_to_cart():
	return add_to_cart()

@app.route('/cart/<int:product_id>', methods=['DELETE'])
def delete_item_from_cart(product_id):
	return remove_from_cart(product_id)

@app.route('/orders', methods=['POST'])
def make_order():
	return create_order()

@app.route('/orders', methods=['GET'])
def list_orders():
	return get_orders()

@app.route('/orders/<int:order_id>', methods=['GET'])
def order_details(order_id):
	return get_order_details(order_id)

@app.route('/seller/products', methods=['POST'])
def add_product():
	return create_product()

@app.route('/seller/products/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
	return update_product(product_id)

@app.route('/delivery/orders', methods=['GET'])
def pending_orders():
	return get_pending_deliveries()

@app.route('/delivery/orders/<int:order_id>', methods=['PATCH'])
def change_order_status(order_id):
	return update_order_status(order_id)

@app.route('/admin/users', methods=['GET'])
def list_users():
	return get_all_users()

@app.route('/admin/users/<int:user_id>/balance', methods=['PUT'])
def edit_user_balance(user_id):
	return update_user_balance(user_id)

@app.route('/admin/orders', methods=['GET'])
def list_all_orders():
	return get_all_orders()

@app.route('/payment/<int:order_id>', methods=['POST'])
def pay_order(order_id):
	return process_payment(order_id)

if __name__ == '__main__':
	app.run('0.0.0.0', 8228, debug=True)

