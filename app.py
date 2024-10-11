from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'sadasdasdasdadwtdarggshgfbhsdbgfhdsgfvhdsgcnwidslkdcmsrbgt vdfeeytgryf'  
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

class ProductType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=False)
    type = db.relationship('ProductType', backref=db.backref('products', lazy=True))
    card_image = db.Column(db.String(100), nullable=False)
    images = db.Column(db.Text, nullable=False)  # Store as JSON string

class CustomerMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    products = Product.query.all()
    messages = CustomerMessage.query.all()
    product_types = ProductType.query.all()
    return render_template('index.html', products=products, messages=messages, product_types=product_types)

# CRUD for ProductType
@app.route('/product_types')
def product_types():
    types = ProductType.query.all()
    return render_template('product_types.html', types=types)

@app.route('/product_types/add', methods=['GET', 'POST'])
def add_product_type():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_type = ProductType(name=name, image=filename)
            db.session.add(new_type)
            db.session.commit()
            flash('Product type added successfully!', 'success')
            return redirect(url_for('product_types'))
        else:
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'error')
    return render_template('add_product_type.html')

@app.route('/product_types/edit/<int:id>', methods=['GET', 'POST'])
def edit_product_type(id):
    product_type = ProductType.query.get_or_404(id)
    if request.method == 'POST':
        product_type.name = request.form['name']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product_type.image = filename
        db.session.commit()
        flash('Product type updated successfully!', 'success')
        return redirect(url_for('product_types'))
    return render_template('edit_product_type.html', product_type=product_type)

@app.route('/product_types/delete/<int:id>')
def delete_product_type(id):
    product_type = ProductType.query.get_or_404(id)
    db.session.delete(product_type)
    db.session.commit()
    flash('Product type deleted successfully!', 'success')
    return redirect(url_for('product_types'))


@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        type_id = int(request.form['type'])
        card_image = request.files['card_image']
        product_images = request.files.getlist('images')

        if card_image and allowed_file(card_image.filename) and all(allowed_file(image.filename) for image in product_images):
            card_image_filename = secure_filename(card_image.filename)
            card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], card_image_filename))

            image_filenames = []
            for image in product_images:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                image_filenames.append(image_filename)

            new_product = Product(
                name=name,
                price=price,
                description=description,
                type_id=type_id,
                card_image=card_image_filename,
                images=json.dumps(image_filenames)
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('products'))
        else:
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'error')
    product_types = ProductType.query.all()
    return render_template('add_product.html', product_types=product_types)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form['description']
        product.type_id = int(request.form['type'])
        card_image = request.files['card_image']
        if card_image and allowed_file(card_image.filename):
            card_image_filename = secure_filename(card_image.filename)
            card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], card_image_filename))
            product.card_image = card_image_filename
        product_images = request.files.getlist('images')
        if product_images and all(allowed_file(image.filename) for image in product_images):
            image_filenames = []
            for image in product_images:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                image_filenames.append(image_filename)
            product.images = json.dumps(image_filenames)
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    product_types = ProductType.query.all()
    return render_template('edit_product.html', product=product, product_types=product_types)

@app.route('/products/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))


@app.route('/submit_message', methods=['POST'])
def submit_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    new_message = CustomerMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()
    flash('Message sent successfully!', 'success')
    return redirect(url_for('index'))

@app.template_filter('from_json')
def from_json(value):
    return json.loads(value)

@app.route('/product/<int:id>')
def product_details(id):
    product = Product.query.get_or_404(id)
    images =  product.images.split('"')[1::2]
    product_types = ProductType.query.all()
    return render_template('product_details.html', product=product, images=images, product_types=product_types)

if __name__ == '__main__':
    app.run(debug=True)