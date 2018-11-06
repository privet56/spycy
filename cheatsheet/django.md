# DJANGO
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
	$ python manage.py test myapp				# exec myapp/tests.test_*
	$ python manage.py shell				# you can write python on the shell
		# from myapp.models import Mymodel
		Mymodel.objects.filter(mymodel_text_startswith='my')
		q = Mymodel.objects.get(id=1)

## Create an app in your project:
	$ python manage.py startapp myapp	#creates new app with models, tests, views, admin
	# add to INSTALLED_APPS
	# extend urls.py:
		from django.conf.urls import url, include
		url(r'^myapp/', include('myapp.urls'))
	# create myapp/urls.py
		from django.conf.urls import url, include
		from . import views
		from django.urls import path
		app_name = "myapp"					# namespace!
		urlpatterns = [
			url(r'^$', views.index, name='index'),		#views.index -> views.py: def index(request):
			url(r'^details/(?P<id>\d+)/$', views.details, name='details')
			#path('', views.index)				# this syntax is for a newer django release
			#path('details/<int:id>/', views.details, name='details')
		]

	# edit myapp/views.py
		from django.http import HttpResponse, Http404, reverse
		from django.shortcuts import render, get_object_or_404
		from django.template import loader
		from .models import Mymodel			#from . import models
		def index(request):
			#return HttpResponse('hi')
			#mymodels = Mymodel.objects.filter(pub_date__year=year).order_by('-pub_date')
			#mymodels = Mymodel.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
			#mymodels = Mymodel.objects.order_by('-pub_date')[:5]
			mymodels = Mymodel.objects.all()[:10]
			context = {
				'title' = 'myapp',
				'mydatas' = mymodels,
				'output':', '.join([mymodel.name for mymodel in mymodels]) # list comprehension
			}
			return render(request, 'myapp/index.html', context)	#{'myapptitle':'myapp'})
			# Alternative:
			# loader.get_template('myapp/index.html')
			# return HttpResponse(template.render(context, request))
		def details(request, id):
			# Attention: this raises exception if not found or >1 found
			#mymodel = Mymodel.objects.get(full_name_startswith='name')
			try:
				mymodel = Mymodel.objects.get(id=id | pk=id)
			catch Mymodel.DoesNotExist:						# alternative: get_object_or_404
				raise Http404("not found")
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
						<li><a href="/myapp/details/{{mydata.id}}">{{mydata.title}} #better: {% url namespace
					{% endfor %}
			{% endblock %}
			<a href="{% url 'detail' mydata.id %}">{{mydata.title}}</a>
			<a href="{% url 'myapp:detail' mydata.id %}">{{mydata.title}}</a>	# namespace (->app_name)
	# myapp/models.py
		from django.db import models
		from datetime import datetime
		from django.utils import timezone
		class Mymodel(models.Model):				# pk (primary key) is created automatically by base
			title = models.CharField(max_length=222)
			body = models.TextField()			# there is also IntegerField
			created_at = models.DateTimeField(default=datetime.now, blank=True)		# or do TZ-aware!
			# relation to another model, you get access functions like mymodel.submymodel_set.all
			# submy = models.ForeignKey(SubMyModel, on_delete=models.CASCADE)
			def __str__(self):
				return self.title
			class Meta:
				verbose_name_plural = "Mymodels"
	# myapp/admin.py
		from .models import Mymodel
		admin.site.register(Mymodel)			# will be shown on the admin ui, editably
	$ python manage.py makemigrations myapp			# creates myapp/migrations/00001_initial.py
	$ python manage.py migrate				# creates the DB table

# Forms & Editing:
	myapp/urls.py:
		path('<int:id>/update', views.update, name='update'),

	myapp/views.py:
		def update(request, id):
			mymodel = get_object_or_404(Mymodel, pk=id)
			# Attention: raises KeyError if not found
			mymodel.dummySetPropFromPostRequest(request.POST['mysubval'])
			mymodel.save()
			return HttpResponseRedirect(reverse('myapp:index', args=(mymodel.id,)))	# avoiding resubmit
				
	myapp/templates/myapp/details.html:
		<form action={% url 'myapp:update' mymodel.id %} method=post>
			{% csrf_token %}
			{% for submy in mymodel.submymodel_set.all %}
				<input type=radio name=mysubval id=my{{forloop.counter}} value={{submy.id}}>
			{% endfor %}
			<input type=submit value=update>
		</form>
	
# Generic view:
	myapp/urls.py:
		path('', views.IndexView.as_view(), name='index')
		path('<int:pk>', views.DetailView.as_view(), name='detail')	#pk is a fix name
	myapp/views.py:
		class IndexView(generic.ListView):
			template_name = 'myapp/index.html'			#fix variable name
			context_object_name = 'latest_myapp_list'		#context variable override default: myapp_list
			def get_queryset(self):
				return Mymodel.objects.order_by('-pub_date')[:5]
		class DetailView(generic.DetailView):
			model = Mymodel						#fix variable name
			template_name = 'myapp/detail.html'
		def update(request, id):
			...

# Tests:
	myapp/tests.py
		import datetime
		from django.utils import timezone
		from django.test import TestCase
		from .models import Mymodel
		class MymodelTest(TestCase):
			def test_mymodel(self):					# start with test_ triggers unit test execution
				"""
				unit test case
				"""
				time = timezone.now() + datetime.timedelta(days=30)
				mymodel = Mymodel(pub_date=time)
				self.assertIs(mymodel.isSomeCalc(), False)
			def test_myui(self):
				url = reverse('myapp:detail', args=(mymodel.id,))
				response = self.client.get(reverse('myapp:index'))
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'mytext')
				self.assertQuerysetEqual(response.context['my_app_list'], [])
	# unit test execution:
		$ python manage.py test myapp
	# view test execution in the django shell:
		$ from django.test.utils import setup_test_environment
		$ setup_test_environment()
		$ from django.test import Client
		$ client = Client()
		$ response = client.get('/')
		#response has status_code & content & context['latest_myapp_list']
		$ response = client.get(reverse('myapp:index'))
	# integration / ui test of the complete app, incl. client side (js) code:
		use LiveServerTestCase & Selenium

# Static files:
	# myapp/static/myapp/{*.js,*.css}					# you can create subdirs, like js,css,img
	# INSTALLED_APPS = [ 'django.contrib.staticfiles', ...
	# reference in template as:
		{% load static %}
		<link rel=stylesheet type=text/css href="{% static myapp/*.css %}" />
