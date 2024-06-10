from flask import Flask, request, redirect, jsonify, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import os
app = Flask(__name__, static_folder='public')
port = 8000

mongo_url = "mongodb://localhost:27017/"
db_name = "mydatabase"
client = MongoClient(mongo_url)
db = client[db_name]
print(f"Connected to MongoDB: {db_name}")

@app.route('/')
def landing():
    return send_from_directory(app.static_folder, 'landing.html')

@app.route('/buy')
def buy():
    return send_from_directory(app.static_folder, 'buy.html')

@app.route('/signin')
def signin():
    return send_from_directory(app.static_folder, 'signin.html')

@app.route('/signup')
def signup():
    return send_from_directory(app.static_folder, 'signup.html')

@app.route('/error')
def error():
    return send_from_directory(app.static_folder, 'error.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form['email']
    password = request.form['pass']
    try:
        db.items.insert_one({'email': email, 'pass': password})
        print("User inserted successfully")
        return redirect('/signin')
    except Exception as e:
        print(f"Error inserting user data: {e}")
        return "Failed to sign up", 500

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['pass']
    try:
        user = db.items.find_one({'email': email, 'pass': password})
        if user:
            print("User authenticated successfully")
            return redirect('/buy')
        else:
            print("Authentication failed")
            return redirect('/error')
    except Exception as e:
        print(f"Error during authentication: {e}")
        return "Failed to login", 500
    
@app.route('/order', methods=['POST'])
def order_post():
    data = request.get_json()
    meal_name = data.get('mealName')
    price = data.get('price')
    if not meal_name or not price:
        return jsonify({'status': 'failure', 'reason': 'Invalid input'}), 400
    try:
        order = {'mealName': meal_name, 'price': price}
        result = db.orders.insert_one(order)
        order['_id'] = str(result.inserted_id)
        print("Order placed successfully")
        return jsonify({'status': 'success', 'order': order}), 200
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({'status': 'failure', 'reason': str(e)}), 500

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = list(db.orders.find())
        for order in orders:
            order['_id'] = str(order['_id'])
        return jsonify({'status': 'success', 'orders': orders}), 200
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({'status': 'failure', 'reason': str(e)}), 500

@app.route('/summary')
def summary():
    return send_from_directory(app.static_folder, 'summary.html')

# @app.route('/order', methods=['POST'])
# def order_post():
#     data = request.get_json()
#     meal_name = data['mealName']
#     rate = int(data['rate'])
#     print(f"Received order: {meal_name} with rate: {rate}")
#     try:
#         db.orders.insert_one({'mealName': meal_name, 'rate': rate})
#         print("Order placed successfully")
#         return jsonify({'status': 'success'}), 200
#     except Exception as e:
#         print(f"Error placing order: {e}")
#         return jsonify({'status': 'failure'}), 500

if __name__ == "__main__":
    app.run(port=port)
