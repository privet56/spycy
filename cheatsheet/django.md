# DJANGO:
	Is an MVC, better said, an MTV (Model-Template-View) framework
	Editors: vscode, atom, ...

## conda
	$ conda create --name mysite python=3.6		# creates a virtual env
	$ source activate mysite

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
	$ python manage.py startapp myapp
	$ python manage.py shell					# you can write python on the shell
		#import ...
		Mymodel.objects.filter(mymodel_text_startswith='my')

## Create an app in your project:
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
			#path('details/<int:id>/' ...
		]

	# edit myapp/views.py
		from django.http import HttpResponse
		from django.shortcuts import render
		from .models import Mymodel			#from . import models
		def index(request):
			#return HttpResponse('hi')
			#mymodels = Mymodel.objects.filter(pub_date__year=year)
			#mymodels = Mymodel.objects.order_by('-pub_date')[:5]
			mymodels = Mymodel.objects.all()[:10]
			context = {
				'title' = 'myapp',
				'mydatas' = mymodels,
				'output':', '.join([mymodel.name for mymodel in mymodels])		# list comprehension
			}
			return render(request, 'myapp/index.html', context)	#{'myapptitle':'myapp'})
		def details(request, id):
			#mymodel = Mymodel.objects.get(full_name_startswith='name')			#attention: raises exception if not found or >1 found
			mymodel = Mymodel.objects.get(id=id | pk=id)
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
		from django.utils import timezone
		class Mymodel(models.Model):												# pk (primary key) is created automatically by base
			title = models.CharField(max_length=222)
			body = models.TextField()												# there is also IntegerField
			created_at = models.DateTimeField(default=datetime.now, blank=True)		# or do TZ-aware!
			#q = models.ForeignKey(Q, on_delete=models.CASCADE)						# reference to another model
			def __str__(self):
				return self.title
			class Meta:
				verbose_name_plural = "Mymodels"
	# myapp/admin.py
		from .models import Mymodel
		admin.site.register(Mymodel)			# will be shown on the admin ui, editably
	$ python manage.py makemigrations myapp			# creates myapp/migrations/00001_initial.py
	$ python manage.py migrate				# creates the DB table

