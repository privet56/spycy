# FLASK

## pip:
	$ sudo apt-get install python3-pip
	$ pip install flask
	$ pip install flask-mysqldb
	$ pip install flask-wtf
	$ pip install passlib
	
## app:

### app.py:
	from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
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
		return render_template('index.html')
	@app.route('/about')
	def about():
		return render_template('about.html')
	@app.route('/alldata')
	def alldata():
		form = MyForm()
		return render_template('data.html', title='My Title', data = data, form=form)
	@app.route('/data/<string:id>/')
	def data(id):
		return render_template('data.html', id = id)
	@app.route('/myform', methods=['GET','POST'])
	@requires_roles('admin', 'user')
	def myform():
		form = MyForm(request.form)
		#Alternative: if form.validate_on_submit():
		if request.method == 'POST' and form.validate():
			name = form.name.data	# or request.form['name']
			pwd = sha256_crypt.encrypt(str(form.pwd.data))
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
		app.run(debug=True)

### forms.py
	from flask_ftw import FlaskForm
	from wtfforms import StringField, SubmitField, BooleanField
	from wtfforms.validators import DataRequired, Length, Email, EqualTo
	class MyForm(FlaskForm):
		name = StringField('Name', validators=[DataRequired(), Length(min=2, max=22)])
		mail = StringField('Mail', validators=[DataRequired(), Email()])
		pwd1 = StringField('Pwd1', validators=[DataRequired()])
		pwd2 = StringField('Pwd2', validators=[DataRequired(), EqualTo('pwd1')]) # confirm
		remb = BooleanField('Remember Me')
		submit = SubmitField('Submit Form')

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
			<a href="data/{{d.id}}">{{d.title | safe}}</a>	# safe allows html
		{% endfor %}
		{% endblock %}
		
	templates/myform.html
		{% extends 'layout.html %}
		{% block body %}
		{% from "includes/_formhelpers.html" import render_field %}
		<form method=post> # no action -> submits to same url
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
			{{ form.submit(class='btn') }}
			
			<input type=submit>
		</form>
		<a href="{{ url_for('login') }}"> # 'login' is the @app.route I link to
		{% endblock %}

### static files:
	place static files here:
		static/{*.js | *.css}
	reference static files in the templates this way:
		<link rel=stylesheet type=text/css href="{{ url_for('static', filename='main.css') }}" />
		
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
	$> db.sesssion.commit()
	$> MyModel.query.all()
	$> MyModel.query.first()
	$> MyModel.query.filter_by(name='name').all()
	$> mymodel = MyModel.query.filter_by(name='name').first()
	$> mymodel = MyModel.query.get(1) # get by id
	$> submy = SubMy(name='submy', owner_id = mymodel.id)
	$> db.session.add(submy)
	$> db.drop_all()
	
### Organize project in Packages (instead of Moduls, as above til now)
	./							# my project
	myapp/							# package of my project
		__init__.py					# import here flask, create app & app.config & db
		routes.py					# contains @app.route's (import app from myapp)
	./run.py						# the only purpose of this file is to start the app
		from myapp import app
		if __name__ = '__main__':
			app.run(debug=True)
