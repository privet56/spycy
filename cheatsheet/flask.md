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
	from flask_mysqldb import MySQL
	from wtforms import Form, StringField, TextAreaField, PasswordField, validators
	from passlib.hash import sha256_crypt
	from data import Data
	
	app = Flask(__name__)
	app.debug = True	# reloads browser at change in py!
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
	def myform():
		form = MyForm(request.form)
		if(request.method == 'POST' and form.validate():
			pass
		return render_template('myform.html', form = form)
		
	class MyForm(Form):
		field1 = StringField('First Field', [validators.Length(min=1,max=55)])
		field2 = PasswordField('Snd Field', [validators.DataRequired(),validators.EqualTo('confirm',message='they do not match')])
		confirm = PasswordField('Th Field')
	
	if __name__ == '__main__':
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
		<nav class="navbar navbar-default" ...			# bootstrap
		
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
		<form method=post>
			{{render_field(form.field1, clas_="form_control")}}
			<input type=submit>
		</form>
		{% endblock %}
		
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

### exec:
	python3 app.py
