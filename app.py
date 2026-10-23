from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'ecommerce_secure_admin_key'
DATABASE = 'ecommerce.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                image TEXT,
                description TEXT
            )
        ''')
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("স্মার্টওয়াচ Ultra", 2500.0, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500", "অসাধারণ ফিচার সমৃদ্ধ ওয়াচ"),
                ("ওয়্যারলেস ইয়ারবাড", 1200.0, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500", "এইচডি সাউন্ড ও নয়েজ ক্যানসেলেশন")
            ]
            cursor.executemany("INSERT INTO products (name, price, image, description) VALUES (?, ?, ?, ?)", sample_products)
            conn.commit()

@app.route('/')
def index():
    with get_db() as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0.0
    
    if cart:
        with get_db() as conn:
            for p_id, qty in cart.items():
                product = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
                if product:
                    subtotal = product['price'] * qty
                    total_price += subtotal
                    cart_items.append({
                        'id': product['id'],
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': qty,
                        'subtotal': subtotal
                    })
                    
    return render_template('cart.html', items=cart_items, total=total_price)

@app.route('/checkout', methods=['POST'])
def checkout():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    session.pop('cart', None)
    return f"<h2>ধন্যবাদ {name}! আপনার অর্ডার সফলভাবে কনফার্ম হয়েছে।</h2><p>মোবাইল: {phone}</p><p>ঠিকানা: {address}</p><a href='/' class='btn btn-primary mt-3'>হোমে ফিরে যান</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        image = request.form.get('image')
        description = request.form.get('description')
        
        with get_db() as conn:
            conn.execute("INSERT INTO products (name, price, image, description) VALUES (?, ?, ?, ?)", 
                         (name, price, image, description))
            conn.commit()
        return redirect(url_for('admin'))
        
    with get_db() as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    return render_template('admin.html', products=products)

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
