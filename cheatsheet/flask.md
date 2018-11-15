# FLASK

## pip:
	$ sudo apt-get install python3-pip
	$ pip install flask
	$ pip install flask-mysqldb
	$ pip install flask-wtf
	$ pip install passlib
	
## app:

### app.py:
	from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, abort
	from functools import wraps
	from flask_mysqldb import MySQL
	from wtforms import Form, StringField, TextAreaField, PasswordField, validators
	from passlib.hash import sha256_crypt
	from data import Data
	from forms import MyForm
	
	app = Flask(__name__)
	app.debug = True	# reloads browser at change in py!
	
	app.config['MYSQL_HOST'] = 'localhost' # similarly _USER _PASSWORD, _DB
	app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
	mysql = MySQL(app)
	#generate safe key with: import secrets -> secrets.token_hex(16)
	app.config['SECRET_KEY'] = 'mysecret'
	
	@app.route('/')
	@app.route('/home')	#you can decorate twice!
	def index():
		page = request.args.get('page', 1, type=int)
		return render_template('index.html')
	@app.route('/about')
	def about():
		return render_template('about.html')
	@app.route('/alldata')
	def alldata():
		form = MyForm()
		return render_template('data.html', title='My Title', data = data, form=form)
	@app.route('/data/<string:id>/update')	# string|int	# or just @app.route('/data/<id>/')
	def data(id):
	
		d = MyModel.query.get_or_404(id)
		# or:
		d = MyModel.query.filter_by(name=name).first_or_404()
		#or: 
		d = MyModel.query.filter_by(name=name)\
			.order_by(MyModel.date.desc())\
			.paginate(page, per_page=5)
			
		if d.author != current_user:
			abort(403)
		# link to a data: <a href={{ url_for('data', id=d.id) }}>{{d.title}}</a>
		return render_template('data.html', title=d.title, id = id, data = d)
	@app.route('/myform', methods=['GET','POST'])
	@requires_roles('admin', 'user')
	def myform():
		form = MyForm(request.form)
		#Alternative: if form.validate_on_submit():
		if request.method == 'POST' and form.validate():
			name = form.name.data	# or request.form['name']
			pwd = sha256_crypt.encrypt(str(form.pwd.data)) # alternative: from flask_bcrypt import Bcrypt
			cur = mysql.connection.cursor()
			
			# query example start
			result = cur.execute('''SELECT * FROM users WHERE name = %s ''', [name])
			if result > 0:
				d = cur.fetchone() #cur.fetchall() would return a list
				p = d['pwd']	# ensure _CURSORCLASS = 'DictCursor' (default is tuple)
				if sha256_crypt.verify(p, request.form['pwd']):
					app.logger.info('OK!')
					session.clear()	# removes all session data
					session['user'] = name
			# query example end
			
			cur.execute("INSERT INTO users(name, pwd) VALUES(%s, %s)", (name, pwd))
			mysql.connection.commit()
			cur.close()
			flash('Done!', 'success')
			flash(f'Done! {form.name.data}', 'success') # f' is python version >= 3.6, otherwise use format
			return redirect(url_for('index'))			
		return render_template('myform.html', form = form)
		
	class MyForm(Form): # better: see below 'forms.py'
		name = StringField('First Field', [validators.Length(min=1,max=55)])
		pwd = PasswordField('Scnd Field', [validators.DataRequired(),validators.EqualTo('confirm',message='they do not match')])
		confirm = PasswordField('Th Field')
		# other possibilities, eg. TextAreaField
		
	def requires_roles(*roles):
		def wrapper(f):
			@wraps(f)
			def wrapped(*args, **kwargs):
				if get_current_user_role() not in roles or 'user' not in session:
					flash('not logged in', 'danger')
					return redirect(url_for('login'))
					return error_response()
				return f(*args, **kwargs)
			return wrapped
		return wrapper

	def is_logged_in(f):
		@wraps(f)
		def wrap(*args, **kwargs):
			if 'u' in session:
				return f(*args, **kwargs)
			else
				return redirect(url_for('login'))
		return wrap
	
	if __name__ == '__main__':
		app.secret_key = 'mysecret'	# session needs it
		app.run(port=5555, debug=True)

### forms.py
	from flask_ftw import FlaskForm
	from flask_ftw.file import FileField, FileAllowed
	from wtfforms import StringField, SubmitField, BooleanField
	from wtfforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
	class MyForm(FlaskForm):
		name = StringField('Name', validators=[DataRequired(), Length(min=2, max=22)])
		mail = StringField('Mail', validators=[DataRequired(), Email()])
		pwd1 = StringField('Pwd1', validators=[DataRequired()])
		pwd2 = StringField('Pwd2', validators=[DataRequired(), EqualTo('pwd1')]) # confirm
		pict = FileField('prfpic', validators=[FileAllowed(['jpg','png'])])
		remb = BooleanField('Remember Me')
		submit = SubmitField('Submit Form')
		def validate_name(self, name):
			mymodel = MyModel.query.filter_by(name=name.data).first()
			if mymodel:
				raise ValidationError('err msg')

### data.py
	def Data():
		data = [
			{
				'id':1,
				'title':'title',
				'body':'body'
			}
		]
		
### templates:
	templates/index.html
		{% extends 'layout.html %}				# jinja
		{% block body%}
			mycontent
		{% endblock body %}					# you can tell explicitely which block you close
		
	templates/includes/_navbar.html
		<header... <nav class="navbar navbar-default" ...	# bootstrap, responsive top area
		{% with messages = get_flashed_messages(with_categories=true) %}
			{% if messages %}
				{% for cat, msg in messages %}
					{{cat}} {{msg}}			# flash message
				{% endfor %}
			{% endif %}
		{% endwith %}
		
	templates/includes/_formhelpers.html
		{% macro render_field(field) %}
			{{ field.label }}
			{{ field(**kwargs)|safe }}
			{% if field.errors %}
				{% for e in field.errors %}
					{{e}}
				{% endfor %}
			{% endif %}
		{% endmacro %}
		
	templates/layout.html
		<html>
		 <body>
		  {% include 'includes/_navbar.html' %}
		  {% block body %}{% endblock %}
		  
	templates/data.html
		{% extends 'layout.html %}
		{% block body %}
		{% for d in data %}
			<a href="data/{{d.id}}">{{d.title | safe}}</a>	# safe allows html # better use url_for
		{% endfor %}
		{% endblock %}
		
	templates/myform.html
		{% extends 'layout.html %}
		{% block body %}
		{% from "includes/_formhelpers.html" import render_field %}
		<form method=post> # no action -> submits to same url # enctype=multipart/form-data if you upload file!
			{{ form.hidden_tag() }} # CSRF token is set here
			
			{{render_field(form.name, class_="form_control")}}
			# or:
			<input value="{{request.form.name}}">
			# or:
			# output label & input of the MyForm class member 'name':
			{{ form.name.label(class='form-control-label') }}
			{% if form.name.errors %}
				{{ form.name(class='form-control is-invalid') }}
				{% for e in form.name.errors %}
					{{ e }}
				{% endfor %}
			{% else %}
				{{ form.name(class='form-control') }}
			{% endif %}
			
			# file:
			 {{ form.picture.label() }}
			 {{ form.picture(class='form-control-file') }} # ...and errors as above
			
			{{ form.submit(class='btn') }}
			
			<input type=submit>
		</form>
		<a href="{{ url_for('login') }}"> # 'login' is the @app.route I link to
		{% endblock %}

### static files:
	place static files here:
		static/{*.js | *.css}		# you can make subdirs
	reference static files in the templates this way:
		<link rel=stylesheet type=text/css href="{{ url_for('static', filename='subdir/main.css') }}" />
		
### exec:
	$ python3 app.py
		or
	$ export FLASK_APP=app.py	# on windows: SET instead of export
	$ export FLASK_DEBUG=1		# don't need to restart server to see changes
	$ flask run

### ORM: SqlAlchemy
	$ pip install flask-sqlalchemy
	from flask_sqlachemy import SQlAlchemy
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my.db'
	db = SQlAlchemy(app)
#### Models
	from datetime import datetime
	class MyModel(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(22, unique=True, nullable=False, default='d')) # max len: 22
		date = db.Column(db.Datetime(nullable=False, default=datetime.utcnow))
		body = db.Column(db.Text(nullable=False))
		
		owner_id = db.Column(db.Integer, db.ForeignKey('owner.id', nullable=False))
		submy = db.relationship('SubMy', backref='mymodel', lazy=True)
		
		def __repr__(self):
			return f"MyModel('{self.name}')"
			
#### use SqlAlchemy-db in the shell
	$ python
	$> from app import db
	$> db.create_all()
	$> from app import MyModel
	$> mymodel = MyModel(name='name')
	$> db.sesssion.add(mymodel)
	$> db.session.delete(mymodel)
	$> db.sesssion.commit()
	$> MyModel.query.all()
	$> MyModel.query.paginate() # returns a flask_sqlachemy.Pagination object
	$> MyModel.query.paginate(per_page=5, page=2) # returns the 2. page
	# flask_sqlachemy.Pagination object can page, pages, per_page, total etc.
	# page = request.args.get('page', 1, type=int) # get page from url query param
	$> MyModel.query.first()
	$> MyModel.query.filter_by(name='name').all()
	$> mymodel = MyModel.query.filter_by(name='name').first()
	$> mymodel = MyModel.query.get(1) # get by id
	$> submy = SubMy(name='submy', owner_id = mymodel.id)
	$> db.session.add(submy)
	$> db.drop_all()
	
### Organize project in Packages (instead of Modules, as above til now) (package dirs have __init__.py)
	./							# my project
	
	./models.py
	
	./config.py						# contains all former app.config[*] entries
		class Config:
			SQLALCHEMY_DATABASE_URI = 'sqlite:///side.db'
			MAIL_USERNAME = os.environ.get('EMAIL_USER')
			...

	./myapp/						# Package of my project
		__init__.py					# import here flask, create app & app.config & db
		routes.py					# contains @.route's (import app from myapp)
			from flask import Blueprint
			main = Blueprint('main', __name__)
			@main.route("/home", ...
			
	./users/						# Example Package
		__init__.py
		routes.py					# contains @.route's of users
			from flask import Blueprint
			from myapp.users.utils import myutilfunction
			from myapp.models import MyModel
			users = Blueprint('users', __name__)
			@users.route("/login", ...
		forms.py
		utils.py
		
	./run.py						# the only purpose of this file is to start the app
		from flask import current_app
		from myapp import app
		from myapp.config import Config
		from myapp.main.routes import main		# 'main' is a Blueprint object
		from myapp.user.routes import users		# 'users' is a Blueprint object
		def create_app(config_class=Config):
			app = Flask(__name__)				# access 'app' later as current_app
			db.init_app(app)
			*.init_app(app)
			app.config.from_object(Config) 			# the Flask 'app' object uses the Config object
			app.register_blueprint(main)
			app.register_blueprint(users)
		if __name__ = '__main__':
			app = create_app()				# function call uses default param val
			current_app.run(port=5555, debug=True)			# debug provides helpful & detailed error pages on exception
			
	Attention: with Packages & Blueprint, you need to do your links by specifying the package name, e.g.:
		url_for("users.login")

### use Bcrypt to encrypt/decrypt (alternative to passlib.hash.sha256_crypt)
	$ pip install flask_bcrypt
	from flask_bcrypt import Bcrypt
	b = Bcrypt(app)
	hashed = b.generate_password_hash(form.pwd.data).decode('utf-8') # decodes binary into test
	b = b.check_password_hash(hashed, 'pwd')

### Custom Validation
	class MyForm(FlaskForm):
		name = StringField('Name', validators=[DataRequired(), Length(min=2, max=22)])
		def validate_name(self, name): # validation function pattern: validate_{fieldname}
			if name.data != current_user.username: # current user is from flask_login (see below)
				mymodel = MyModel.query.filter_by(name=name.data).first()
				if mymodel:
					raise ValidationError('err msg')

### flask-login: the LoginManager
	$ pip install flask-login
	from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
	import secrets
	login_manager = LoginManager(app)
	login_manager.login_view = 'login' 		# specify here the login route
	login_manager.login_message_category = 'info'
	
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))
	
	class UserModel(db.Model, UserMixin):
		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(22, unique=True, nullable=False, default='d')) # max len: 22
		...
	
	@app.route("./login", methods=['GET','POST'])
	def login():
		form = LoginForm()
		if(form.validate_on_submit():
			user = UserModel.query.filter_by(email=form.email.data).first()
			if user and bcrypt.check_password_hash(user.pwd, user.pwd.data):
				login_user(user, remember=form.remember.data)
				next = request.args.get('next')	# args['next'] would throw if key does not exist
				return redirect(url_for(next)) if next else return redirect(url_for('home'))
			flash('failed', 'danger')
		return render_template('login.html', title='Login', form=form)

	@app.route("./data")
	@login_required # if not logged in: redirect to login_manager.login_view
	def data():
		if !current_user.is_authenticated:
			return redirect(url_for('home'))
		return render_template('data.html', title='Secret Data', data=dataGotFromDB)
		
	def save_pic(pic):
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(pic.filename) # dont need first return value (=f_name)
		fn = random_hex + f_ext
		path = os.path.join(app.root_path, 'static/pix', fn) # better save in the cloud or db
		#pic.save(path)
		
		# $ pip install Pillow	#from PIL import Image
		output_size = (125, 125)
		i = Image.open(pic)
		i.thumbnail(output_size)	# resizes, scales down image
		i.save(path)		

		return fn
		
	@app.route("/updateuserinfo", methods=['GET','POST'])
	@login_required
	def updateuserinfo():
		form = UpdateUserInfoForm()
		if(form.validate_on_submit():
			if somedbvalue.author != current_user:
				abort(403)
			if form.picture.data:
				current_user.picfn = save_pic(form.picture.data)
			current_user.username = form.username.data
			current_user.email = form.email.data
			db.session.commit()
			flash('updated', 'success')
			return redirect(url_for('updateuserinfo')) # post-get-redirect pattern to avoid doubled submit
		elif request.method == 'GET':
			form.name = current_user.username
			form.email = current_user.email
			return render_template('updateuserinfo.html', form=form)

	@app.route("./logout")
	def logout():
		logout_user()
		return redirect(url_for('home'))

	In templates:
		{% if current_user.is_authenticated %}
			<a href="{{ url_for('logout') }}"> Logout {{ current_user.username }} </a>
			{{ current_user.logintime.strftime('%Y-%m-%d') }}
		{% else %}
			<a href="{{ url_for('login') }}">
		{% endif %}

### Pagination
#### SqlAlchemy pagination support:
	ps = MyModel.query.paginate() # returns a flask_sqlachemy.Pagination object
	ps = MyModel.query.order_by(MyModel.date.desc()).paginate(per_page=5, page=2) # returns the 2. page
	# flask_sqlachemy.Pagination object can page, pages, per_page, total etc.
		
#### in the route, calc page:
	page = request.args.get('page', 1, type=int) # get page from url query param
	
#### in templates:
	for p in ps.iter_pages():
		#returns: 1, 2, None, 3, 4. ...
	{% for page_num in ps.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
		{% if page_num %}
			{% if ps.page == page_num %}
				<a href={{ url_for('list', page=page_num) }} class="btn btn-info mb-4">{{ page_num }}</a>
			{% else %}
				<a href={{ url_for('list', page=page_num) }} class="btn btn-outline-info mb-4">{{ page_num }}</a>
			{% endif %}
		{% else %}
			...
		{% endif %}
	{% endfor %}

### Signatures & Email
#### Signature: with itsdangerous (installed with flask by default)
	from itsdangerous import TimedJSONWebSignatureSerializer as Ser
	s = Ser('secret', 30) # expiration: 30 seconds
	payload_in = {'user_id':user.id}
	token = s.dumps(payload_in).decode('utf-8') #token is a long string
	try:					# prepare for expired or wrong token input
		payload_out = s.loads(token)	# payload_out == payload_in
	except:
		return None

#### Email
	$ pip install flask-mail
	
	from flask_mail import Mail, Message
	app.config["MAIL_SERVER"] = 'smtp.google.com'
	app.config["MAIL_PORT"] = '587'
	app.config["MAIL_USE_TLS"] = True
	app.config["MAIL_USERNAME"] = os.environ.get('EMAIL_USER')
	app.config["MAIL_PASSWORD"] = os.environ.get('EMAIL_PASS')
	
	@staticmethod
	def sendemail(user):
		msg = Message('subject', sender='noreply@my.com', recipients=[user.email])
		msg.body = f''' email content {url_for('home', param=param, _external=True)} '''
		mail.send(msg)

### Custom Error Pages as Package
	./errors/
		__init__.py
		handlers.py
			from flask import Blueprint
			errors = Blueprint('errors', __name__)
			@errors.app_errorhandler(404)
			def error_404(error):					# in the template, you can use your layout
				return render_template('errors/404.html'), 404	# 404 is the response error code
				
	./__init__.py or main.py
		from myapp.errors.handlers import errors
		app.register_blueprint(errors)

## WSGI
### Install system packages (here, for ubuntu)
	$ sudo apt-get update
	$ sudo apt-get install python-pip
	$ pip install --user Flask
	$ sudo apt-get install apache2
	$ sudo apt-get install libapache2-mod-wsgi
	
	$ sudo chown -R tom /var/www		# set access rights
	$ sudo chown –R tom /etc/apache2
	
### myapp.wsgi
	import os, sys, site
	sys.path.insert(0, "/var/www/myapp")
	from myapp import app as application
	## django needs/can more!
	#site.addsitedir(other_path)
	#os.environ["DJANGO_SETTINGS_MODULE"] = "myproject.settings"
	#from django.core.wsgi import get_wsgi_application
	#application = get_wsgi_application()

###  /etc/apache2/sites-available/myapp.conf

	Options -Indexes
	AliasMatch ^/static/\d+/(.*) \
		"/home/myapp/app/myapp/static/$1"
	<FilesMatch "\.(ico|pdf|flv|jpe?g|png|gif|js|css|swf)$">
		ExpiresActive On
		ExpiresDefault "access plus 1 year"
	</FilesMatch>

	<VirtualHost *>
		 ServerName example.com
		 WSGIScriptAlias / /var/www/myapp/my.wsgi
		 WSGIDaemonProcess my
		 <Directory /var/www/myapp>
			 WSGIProcessGroup my
			 WSGIApplicationGroup %{GLOBAL}
			 Order deny,allow
			 Allow from all
		 </Directory>
	</VirtualHost>
	
	$ /etc/init.d/apache2 restart

#### /home/myapp/public_html/.htaccess - optional
	AddHandler wsgi-script .wsgi
	DirectoryIndex index.html
	RewriteEngine On
	RewriteBase /
	RewriteCond %{REQUEST_FILENAME} !-f
	RewriteCond %{REQUEST_FILENAME}/index.html !-f
	RewriteCond %{REQUEST_URI} !^/media/
	RewriteCond %{REQUEST_URI} !^/static/
	RewriteRule ^(.*)$ /my.wsgi/$1 [QSA,L]

###  MySQL settings: /etc/mysql/my.cnf
	[client]
	default-character-set = utf8
	[mysql]
	default-character-set = utf8
	[mysqld]
	collation-server = utf8_unicode_ci
	init-connect = 'SET NAMES utf8'
	character-set-server = utf8
	
	$ /etc/init.d/mysql restart

###
	$ sudo a2dissite 000-default.conf
	$ sudo a2ensite my.conf
	$ sudo service apache2 reload
	$ sudo tail –f /var/log/apache2/error.log
	
### advanced API: make_response
	from flask import make_response
	
	@app.route('/')
	def index():
		pubQueryA = request.args.get("publication")
		pubCookie = request.cookies.get("publication")
		response = make_response(render_template("home.html", articles=articles)
		expires = datetime.datetime.now() + datetime.timedelta(days=365)
		response.set_cookie("publication", publication, expires=expires)
		response.set_cookie("city", city, expires=expires)
		return response
