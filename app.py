from flask import Flask, render_template, request, jsonify, session
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# Sample products database
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    {"id": 2, "name": "Smartphone", "price": 499.99, "stock": 15},
    {"id": 3, "name": "Headphones", "price": 99.99, "stock": 20},
    {"id": 4, "name": "Tablet", "price": 299.99, "stock": 8},
]

@app.route('/')
def home():
    return render_template('index.html', products=PRODUCTS)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in PRODUCTS if query in p['name'].lower()]
    return jsonify(results)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    product_id = int(request.json.get('product_id'))
    quantity = int(request.json.get('quantity', 1))
    
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    cart_item = next((item for item in session['cart'] if item['product_id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] += quantity
    else:
        session['cart'].append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        })
    
    session.modified = True
    return jsonify(session['cart'])

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.json.get('product_id'))
    quantity = int(request.json.get('quantity'))
    
    cart_item = next((item for item in session['cart'] if item['product_id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] = quantity
        session.modified = True
    
    return jsonify(session['cart'])

@app.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('cart'):
        return jsonify({"error": "Cart is empty"}), 400
    
    # In a real application, you would process the payment and create an order here
    order = {
        'items': session['cart'],
        'total': sum(item['price'] * item['quantity'] for item in session['cart'])
    }
    
    session['cart'] = []
    session.modified = True
    
    return jsonify({"message": "Order placed successfully", "order": order})

if __name__ == '__main__':
    app.run(debug=True) 