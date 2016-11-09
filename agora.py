import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'agora.db'),
    DEBUG=True,
    SECRET_KEY='@agorakey#1',
    USERNAME='admin',
    PASSWORD='password',
    SHOP_IN_VIEW='',  #id of shop currently being viewed
    UPLOAD_FOLDER = 'uploads/',
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
))
app.config.from_envvar('AGORA_SETTINGS', silent=True)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
	

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def check_password(username, password):
	res = g.db.execute('SELECT * FROM users WHERE user_name=? AND user_password=?',\
    	[username, password]).fetchall()
	if len(res)>0:
		return True
	else:
		return False

def user_exists(username):
	res = g.db.execute('SELECT * FROM users WHERE user_name=?',[username]).fetchall()
	if len(res)>0:
		return True
	else:
		return False
def shop_exists(shop_name):
	res = g.db.execute('SELECT * FROM shops WHERE shop_name=?',[shop_name]).fetchall()
	if len(res)>0:
		return True
	else:
		return False

def get_current_user_id():
	res = g.db.execute('SELECT user_id FROM users WHERE user_name=?',
		[app.config['USERNAME']]).fetchall()
	if len(res)<=0:
		return False
	return res[0][0]

def get_current_user_shops():
	res = g.db.execute('''
		SELECT * FROM shop
		INNER JOIN users_shop
		ON
		shop.shop_id=users_shop.shop_id
		WHERE users_shop.user_id=?
		''',
		[get_current_user_id()]).fetchall()

	if len(res)<=0:
		return False

	return res

#gets products for specified shop
def get_shop_products(shop_id):
	res = g.db.execute('''
		SELECT * FROM products
		INNER JOIN shop_products
		ON
		products.product_id=shop_products.product_id
		WHERE shop_products.shop_id=?
		''',
		[shop_id]).fetchall()

	if len(res)<=0:
		return False

	return res

#checks if user owns a specific shop
def owns_shop_in_view(shop_id):
	user_id = get_current_user_id()
	res = g.db.execute('SELECT user_id FROM users_shop WHERE shop_id=?',[shop_id]).fetchall()

	for row in res:
		if row[0] == user_id: #row[0]=user_id
			return True
	return False

#check if product in shop
def product_in_shop(shop_url,product_url):
	shop_id = g.db.execute('SELECT shop_id FROM shop WHERE shop_url=?',[shop_url]).fetchall()[0][0]
	product_id = g.db.execute('SELECT product_id FROM products WHERE product_url=?',[product_url]).fetchall()[0][0]

	if not shop_id or not product_id:
		return False

	res = g.db.execute('SELECT * FROM shop_products WHERE shop_id=? AND product_id=?',[shop_id,product_id]).fetchall()

	if len(res)<=0:
		return False
	return True

#returns url of specified shop
def get_shop_url(shop_id):
	res = g.db.execute('SELECT shop_url from shop WHERE shop.shop_id=?',[shop_id]).fetchall()
	return res

@app.route('/')
def homepage():
	user_shops = get_current_user_shops()
	return render_template('home.html',user_shops=user_shops)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
    	res = check_password(request.form['username'],request.form['password'])

        if not res:
        	error = 'Invalid username or password'
        else:
			app.config['USERNAME'] = request.form['username']
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('homepage'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    app.config['USERNAME'] = ''
    flash('You were logged out')
    return redirect(url_for('homepage'))

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """Registers the user."""
    if session.get('logged_in'):
        return redirect(url_for('homepage'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif user_exists(request.form['username']):
            error = 'The username is already taken'
        if not error:
            g.db.execute('''insert into users (
              user_name, user_email, user_password) values (?, ?, ?)''',
              [request.form['username'], request.form['email'],
               request.form['password']])
            g.db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/create-store', methods=['GET','POST'])
def create_store():
	if not session.get('logged_in'):
		return redirect(url_for('homepage'))
	error = None
	if request.method == 'POST':
		form = request.form

		if not form['shopname']:
			error = 'You have to enter a shop name'
		elif user_exists(form['shopname']):
			error = 'A shop with this name already exists.'
		elif not form['shoplocation']:
			error = 'You did not enter the location of the shop'
		elif not form['shopdescription']:
			form['shopdescription'] = ''

		else:
			g.db.execute('INSERT INTO shop (shop_name, shop_desc, shop_location,shop_url) values(?,?,?,?)',\
				[form['shopname'],form['shopdescription'],form['shoplocation'],form['shopname'].lower().replace(' ','-')])

			shop_id = g.db.execute('SELECT * FROM shop ORDER BY shop_id DESC LIMIT 1').fetchall()[0][0]

			g.db.execute('INSERT INTO users_shop(shop_id,user_id) values(?,?)',[shop_id, get_current_user_id()])
			g.db.commit()

		flash('Congratulations! Your store has been created!')
	return render_template('create-store.html',error=error)

#returns view for shop
@app.route('/<shopurl>')
def view_shop(shopurl):
	shop_data = g.db.execute('SELECT shop_name,shop_desc,shop_location,shop_id FROM shop WHERE shop_url=?',[shopurl]).fetchall()
	error = None
	if len(shop_data)<=0:
		abort(404)
	shop_id = app.config['SHOP_IN_VIEW'] = shop_data[0][3]

	products = get_shop_products(shop_id)

	owns_shop = owns_shop_in_view(shop_id)

	return render_template('shop.html',shop_data = shop_data, error = error, products = products, owns_shop = owns_shop, shop_url = shopurl)

@app.route('/add-product', methods=['GET','POST'])
def add_product():
	if not session.get('logged_in'):
		return redirect(url_for('homepage'))

	error = None
	user_shops = get_current_user_shops()

	if request.method == 'POST':
		form = request.form
		filename = 'base.png'

		if not form['producttitle']:
			error = 'You have to enter a product title.'
		elif not form['productprice'] :
			error = 'You did not fill in the product price'
		elif not form['productdescription']:
			form['productdescription'] = ''

		else:
			if 'file' not in request.files:
				uploaded = upload_file(request)
				if uploaded[0]:
					filename = uploaded[1]
				else:
					error = uploaded[1]
			product_url = form['producttitle'].lower().replace(' ','-')
			g.db.execute('INSERT INTO products (product_title, product_desc, product_price,product_image,creation_date,product_url) values(?,?,?,?,datetime(),?)',\
				[form['producttitle'],form['productdescription'],form['productprice'],filename,product_url])

			product_id = g.db.execute('SELECT * FROM products ORDER BY product_id DESC LIMIT 1').fetchall()[0][0]

			g.db.execute('INSERT INTO shop_products(product_id,shop_id) values(?,?)',[product_id, form['productshop']])
			g.db.commit()

			flash('Your product has been published!')
	
	return render_template('add-product.html',error=error, user_shops=user_shops)

@app.route('/<shopurl>/<producturl>')
def view_product(shopurl, producturl):
	if product_in_shop(shopurl, producturl):
		product_data = g.db.execute('SELECT product_title,product_image,product_desc,product_price,product_id,product_url FROM products WHERE product_url=?',[producturl]).fetchall()
		error = None

		product_id = product_data[0][4]
		return render_template('product.html',product_data = product_data, error = error, shop_url = shopurl)

	else:
		abort(404)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def upload_file(request):
    # check if the post request has the file part

    file = request.files['productimage']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return (False,'No file selected')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return (True,filename)
    return (False,'Upload error')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
	app.run()


