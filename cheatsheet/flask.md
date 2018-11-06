# FLASK

## pip:
	$ sudo apt-get install python3-pip
	$ pip install flask
	
## app:

### app.py:
	from flask import Flask, render_template
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
	
### exec:
	python3 app.py
