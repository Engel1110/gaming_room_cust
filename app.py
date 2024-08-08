from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_room.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    items = [
        {'name': 'Gaming Chair', 'variants': [('Brand A Chair', 100), ('Brand B Chair', 120), ('Brand C Chair', 150), ('Brand D Chair', 200)]},
        {'name': 'Gaming Desk', 'variants': [('Brand A Desk', 200), ('Brand B Desk', 250), ('Brand C Desk', 300), ('Brand D Desk', 350)]},
        {'name': 'Gaming Monitor', 'variants': [('Brand A Monitor', 200), ('Brand B Monitor', 250), ('Brand C Monitor', 300), ('Brand D Monitor', 350)]},
        {'name': 'Gaming Headphones', 'variants': [('Brand A Headphones', 200), ('Brand B Headphones', 250), ('Brand C Headphones', 300), ('Brand D Headphones', 350)]},
        {'name': 'Gaming Keyboard', 'variants': [('Brand A Keyboard', 200), ('Brand B Keyboard', 250), ('Brand C Keyboard', 300), ('Brand D Keyboard', 350)]},
        {'name': 'Gaming Mouse', 'variants': [('Brand A Mouse', 200), ('Brand B Mouse', 250), ('Brand C Mouse', 300), ('Brand D Mouse', 350)]},
        {'name': 'Gaming Microphone', 'variants': [('Brand A Microphone', 200), ('Brand B Microphone', 250), ('Brand C Microphone', 300), ('Brand D Microphone', 350)]},
        {'name': 'Gaming Computer', 'variants': [('Brand A Computer', 200), ('Brand B Computer', 250), ('Brand C Computer', 300), ('Brand D Computer', 350)]},
        # Add more items similarly...
    ]
    return render_template('dashboard.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_to_cart/<item_name>/<float:item_price>', methods=['POST'])
@login_required
def add_to_cart(item_name, item_price):
    new_item = CartItem(item_name=item_name, item_price=item_price, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.item_price for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get(item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
