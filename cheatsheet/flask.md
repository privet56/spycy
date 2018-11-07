# FLASK

## pip:
	$ sudo apt-get install python3-pip
	$ pip install flask
	$ pip install flask-mysqldb
	$ pip install flask-WTF
	$ pip install passlib
	
## app:

### app.py:
	from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
	from functools import wraps
	from flask_mysqldb import MySQL
	from wtforms import Form, StringField, TextAreaField, PasswordField, validators
	from passlib.hash import sha256_crypt
	from data import Data
	
	app = Flask(__name__)
	app.debug = True	# reloads browser at change in py!
	
	app.config['MYSQL_HOST'] = 'localhost' # similarly _USER _PASSWORD, _DB
	app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
	mysql = MySQL(app)
	
	@app.route('/')
	def index():
		return render_template('index.html')
	@app.route('/about')
	def about():
		return render_template('about.html')
	@app.route('/alldata')
	def alldata():
		return render_template('data.html', data = data)
	@app.route('/data/<string:id>/')
	def data(id):
		return render_template('data.html', id = id)
	@app.route('/myform', methods=['GET','POST'])
	@requires_roles('admin', 'user')
	def myform():
		form = MyForm(request.form)
		if request.method == 'POST' and form.validate():
			name = form.name.data	# or request.form['name']
			pwd = sha256_crypt.encrypt(str(form.pwd.data))
			cur = mysql.connection.cursor()
			
			# query example start
			result = cur.execute('''SELECT * FROM users WHERE name = %s ''', [name])
			if result > 0:
				d = cur.fetchone()
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
			return redirect(url_for('index'))			
		return render_template('myform.html', form = form)
		
	class MyForm(Form):
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
		{% endblock %}
		
	templates/includes/_navbar.html
		<nav class="navbar navbar-default" ...			# bootstrap, responsive top area
		{% with messages = get_flashed_messages(with_categories=true) %}
			{% if messages%}
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
			<a href="data/{{d.id}}">{{d.title}}</a>
		{% endfor %}
		{% endblock %}
		
	templates/myform.html
		{% extends 'layout.html %}
		{% block body %}
		{% from "includes/_formhelpers.html" import render_field %}
		<form method=post>
			{{render_field(form.name, class_="form_control")}}
			# or:
			# <input value="{{request.form.name}}">
			<input type=submit>
		</form>
		{% endblock %}

### exec:
	python3 app.py
