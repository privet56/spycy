# DJANGO:
is an MVC, better said, an MTV (Model-Template-View) framework
## pip
	$ pip install virtualenvwrapper(-win)	#venv support
 	$ mkvirtualenv myvenv
 	$ workon myvenv
 	$ pip install mysqlclient
 	$ pip install django
 	$ django-admin startproject myproject & cd ./mypr

	mypr/wsgi.py
	mypr/urls.py
	mypr/settings.py
		SECRET_KEY
		DEBUG
		ALLOWED_HOSTS
		INSTALLED_APPS
		MIDDLEWARE			#session,auth,...
		ROOT_URLCONF
		TEMPLATES
		DATABASES = {
			'default': {
				'ENGINE':'django.???', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT', ...
		urlpatterns = [
			url(r'^admin/', admin.site.urls),
			...
		
http://localhost:8000/admin/	#admin ui

## manage.py
	$ python manage.py migrate
	$ python manage.py runserver
	$ python manage.py createsuperuser --username=myname --email=my@my.com	#prompts for pwd
	$ python manage.py startup myapp
## create an app in your project:
$ python manage.py startup myapp	#creates new app with models, tests, views, 	admin

	# add to INSTALLED_APPS
	# extend urls.py:
		from django.conf.urls import url, include
		url(r'^myapp/', include('myapp.urls'))
	# create myapp/urls.py
		from django.conf.urls import url, include
		from . import views
		urlpatterns = [
			url(r'^$', views.index, name='index'),			#views.index -> views.py: def index(request):
			url(r'^details/(?P<id>\d+)/$', views.details, name='details')
		]

	# edit myapp/views.py
		from django.http import HttpResponse
		from django.shortcuts import render
		from .models import Mymodel
		def index(request):
			#return HttpResponse('hi')
			mymodels = Mymodel.objects.all()[:10]
			context = {
				'title' = 'myapp',
				'mydatas' = mymodels
			}
			return render(request, 'myapp/index.html', context)	#{'myapptitle':'myapp'})
		def details(request, id):
			mymodel = Mymodel.objects.get(id=id)
			context = {
				'mydata':mymodel
			}
			return render(request, 'myapp/details.html', context)
			
	# create in mypr/myapp/templates/myapp/					# default template engine: jinja
		# layout.html
			<html><body>
			{% block content %}
			{% endblock %}
		# index.html
			{% extends 'myapp/layout.html' %}
			{% block content %}
				{{myapptitle}}
				my app content
				<ul>
					{% for mydata in mydatas %}
						<li><a href="/myapp/details/{{mydata.id}}">{{mydata.title}}
					{% endfor %}
			{% endblock %}
	# myapp/models.py
		from django.db import models
		from datetime import datetime
		class Mymodel(models.Model):
			title = models.CharField(max_length=222)
			body = models.TextField()
			created_at = models.DateTimeField(default=datetime.now, blank=True)		#or do TZ-aware!
			def __str__(self):
				return self.title
			class Meta:
				verbose_name_plural = "Mymodels"
	# myapp/admin.py
		from .models import Mymodel
		admin.site.register(Mymodel)			# will be shown on the admin ui, editably
	$ python manage.py makemigrations myapp			# creates myapp/migrations/00001_initial.py
	$ python manage.py migrate				# creates the DB table

