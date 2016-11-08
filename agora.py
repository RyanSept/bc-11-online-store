import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'agora.db'),
    DEBUG=True,
    SECRET_KEY='@agorakey#1',
    USERNAME='admin',
    PASSWORD='password'
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

	return res[0][0]


@app.route('/')
def homepage():
	flash(str(get_current_user_id()))
	return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
    	res = check_password(request.form['username'],request.form['password'])
    	if res:
    		app.config['USERNAME'] = request.form['username']
        if not res:
        	error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('homepage'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
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
              username, user_email, user_password) values (?, ?, ?)''',
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

		flash('Congratulations on creating your first shop!')
	return render_template('create-store.html',error=error)

#returns view for shop
@app.route('/<shopurl>')
def view_shop(shopurl):
	shop_data = g.db.execute('SELECT shop_name,shop_desc,shop_location FROM shop WHERE shop_url=?',[shopurl]).fetchall()
	error = None
	if len(shop_data)<=0:
		abort(404)
	return render_template('shop.html',shop_data = shop_data, error = error)

if __name__ == '__main__':
	app.run()
