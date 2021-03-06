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
		] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
		
http://localhost:8000/admin/	#admin ui

## manage.py
	$ python manage.py migrate
	$ python manage.py runserver
	$ python manage.py createsuperuser --username=myname --email=my@my.com	#prompts for pwd
	$ python manage.py startapp myapp
	$ python manage.py cleanup --traceback
	$ python manage.py collectstatic
	$ python manage.py syncdb/flush/reset myapp
	$ python manage.py check				# togheter with from django.core.checks import ...
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
		url(r'^myapp/', include('myapp.urls'), namespace="myapp")
	# create myapp/urls.py
		from django.conf.urls import url, include
		from . import views
		from django.urls import path
		app_name = "myapp"					# namespace!
		urlpatterns = [
			#views.index -> views.py: def index(request):
			url(r'^$', views.index, name='index'),
			url(r"^$", lambda request: redirect("/home")),
			url(r'^details/(?P<id>\d+)/$', views.details, name='details')
			#path('', views.index)				# this syntax is for a newer django release
			#path('details/<int:id>/', views.details, name='details')
		]

	# edit myapp/views.py
		from django.http import HttpResponse, Http404, reverse
		from django.shortcuts import render, get_object_or_404, redirect
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
		from django.db.signals import post_save
		from datetime import datetime
		from django.utils import timezone
		from django.utils.text import slugify

		class Mymodel(models.Model):				# pk (primary key) is created automatically by base
			title = models.CharField(max_length=222, default='')
			image = models.ImageField(upload_to='img', blank=True) # you can refer to it with mymodel.image.url
			body = models.TextField()			# there is also IntegerField,URLField
			webs = models.URLField(default='')
			
			created_at = models.DateTimeField(default=datetime.now, blank=True)		# or do TZ-aware! possible param: auto_now_add=True, auto_now=True
			# relation to another model, you get access functions like mymodel.submymodel_set.all
			# submy = models.ForeignKey(SubMyModel, on_delete=models.CASCADE)
			# submy = models.OneToOneField(SubMyModel)
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
	
# Generic view = class based view:
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

## Most used pipes:
	safe
	linebreaksbr
	escape
	escapejs
	stringformat
	trans

## Most used 3rd party libs
	Pillow / PIL		# image editing package
	xhtml2pdf			# generates PDF from XHTML templates
	crispy				# better designable Forms (e.g. with Bootstrap 3)
	Whoosh & Haystack	# Indexing & Search capability
	json				# python object-to-json converter, json.dumps(...)
		(better: django or djangorestframework serializer)
	xlrd/xlwt			# reads/generates Excel
	django-mobile		# sets request.flavour =?= "mobile"
	python-memcached	# settings.py: CACHE @vary_on_cookie & @cache_page(60)
	selenium & mock		# unit & integration tests
	fabric				# depoyment script: fabfile.py
	dateparser			# dateparser.parse("1-jan/15")|.parse("1 week and 3 days ago")
	pymongo				# MongoDB parser
	urllib2/request		# urllib2.urlopen(url).read()

## Advanced Issues:
### Use nosql
	Most used implementation: MongoDB
### API (SOAP, REST or GraphQL)
	Simplifies server-side development, can serve different front-ends
	use djangorestframework (newer than tastypie)
### real-time updates
	Use websockets
### Microservices, Ajax & SPA, Responsive/Mobile Support
	Use JSON-API on the server
### Isomorphic JS development
	Brython, Skulpt or PyPy.js
		You need a compiler to convert PY to JS
	Batavia
		Can run python bytecode (.pyc) in the browser
		WASM as target can reach lightning fast execution
			(WASM has no GC, hard to access the DOM)

## Signals
### built-in Signals
	from django.db.signals import post_save
	
	def on_create_mymodel(sender, **kwargs):
		if kwargs['created']:
			p = Mymodel2.objects.create(mymodel=kwargs['instance'])
	
	post_save.connect(on_create_mymodel, sender=Mymodel)

### User-defined Signals
#### define Signal:
	from django.dispatch import Signal
	order_complete = Signal(providng_args=["customer","barista"])
	store_closed = Signal(providing_args=["employee"])
	
#### import at AppConfig:ready:
	from django.apps import AppConfig
	class MyAppConfig(AppConfig):
		name = "my"
		verbose_name = _("My")
		def ready(self):
			from .checks import settings_check
			
#### emit Signal:
	store_closed.send(sender=self.__class__, employee=employee)
	
#### receive Signal:
	@receiver(store_closed)
	def run_when_store_is_closed(sender,**kwargs):
		stdlogger.info("Start store_closed Store in signals.py under stores app")
		stdlogger.info("sender %s" % (sender))
		stdlogger.info("kwargs %s" % str(kwargs))
	
## Authentication & Authorization
	from django.contrib.auth.views import login, logout, password_reset
	urlpatterns = [
		url(r'^login/$', login, {'template_name':'accounts/login.html'}, name="login"),
		url(r'^logout/$', logout, {'template_name':'accounts/logout.html', 'post_reset_redirect':'myapp:password_reset_done'}, name="logout"),
		...
	in templates, 'form' is available
	
### you can inherit from the built-in UserCreationForm
	from django.contrib.auth.models import User
	from django.contrib.auth.forms import UserCreationForm
	class MyRegForm(UserCreationForm):				# we can use this form in your urlpatterns-route
		email = models.EmailField(required=True)		# we override this field and make it required
		class Meta:
			model = User
			fields = ('name', 'email', ...)
		def save(self, commit=True):				# we override the save function
			user = super(MyRegForm, self).save(commit=False)
			user.first_name = self.cleaned_data['first_name']
			if commit:
				user.save()
			return user

#### Auth Middleware:
	MIDDLEWARE_CLASSES = (
	# …
		"django.contrib.auth.middleware.AuthenticationMiddleware",
	)
			
#### Restrict access to protected pages:
	from django.contrib.auth.decorators import login_required
	@login_required
	@login_required(login_url="my_login_page")
	def data(request):
	
#### Apache configuration: deny direct access to data/templates:
	# data/.htaccess
	Order deny,allow
	Deny from all
		You can put the following content if you are using Apache 2.4:
	# data/.htaccess
	Require all denied
	
## User defined Tags and Filter
### Custom Template Tag
	# -*- coding: UTF-8 -*-
	from __future__ import unicode_literals
	from django import template
	from django.template.loader import get_template
	register = template.Library()
	@register.tag
	def try_to_include(parser, token):
		pass
		
### Custom Filter:
	# utils/templatetags/utility_tags.py
	@register.filter
	@register.filter(name="humanized_days_since") # you can name your filter
	def days_since(value):
		""" Returns number of days between today and value."""
		today = tz_now().date()
		if isinstance(value, datetime.datetime):
			value = value.date()
		diff = today - value
		if diff.days > 1:
			return _("%s days ago") % diff.days
		elif diff.days == 1:
			return _("yesterday")
		elif diff.days == 0:
			return _("today")
		else:
			# Date is in the future; return formatted date.
			return value.strftime("%B %d, %Y")

	@register.filter
	def humanize_url(url, letter_count):
		""" Returns a shortened human-readable URL """
		letter_count = int(letter_count)
		re_start = re.compile(r"^https?://")
		re_end = re.compile(r"/$")
		url = re_end.sub("", re_start.sub("", url))
		if len(url) > letter_count:
			url = "%s…" % url[:letter_count - 1]
		return url
		
	Usage:
	{% load utility_tags %}
	{{ object.published|days_since }}
	{{ object.website|humanize_url:30 }}

## i18n
### Pipe: trans (in Templates)
	{% load i18n %}
	{% load i18n utility_tags %}
	{% load i18n crispy_forms_tags utility_tags %} #with crispy forms
	{% trans "Save" %}

### in Python code:
	from django.conf.urls.i18n import i18n_patterns
	from django.utils.translation import ugettext_lazy as _
	...
	return _("yesterday")
	
## Do REST with djangorestframework
	# config apps:
	INSTALLED_APPS = ['rest_framework' ...
	# config routes:
	router = routers.DefaultRouter()
	router.register(r'stores', stores_views.StoreViewSet)
	urlpatterns = [
		url(r'^rest/', include(router.urls,namespace="rest")),
	# config Authentication:
	rest_framework.permissions
	REST_FRAMEWORK = {
		'DEFAULT_PERMISSION_CLASSES': (
			...
	
	# usage:
	from rest_framework import serializers
	from rest_framework import generics
	from rest_framework import viewsets
	from rest_framework import routers
	from rest_framework.decorators import api_view, permission_classes
	from rest_framework.permissions import IsAuthenticated
	from rest_framework.response import Response
	
	@api_view(['GET','POST','DELETE'])
	def rest_store(request):
		if request.method == 'GET':
			stores = Store.objects.all()
			serializer = StoreSerializer(stores, many=True)
			return Response(serializer.data)
		...

	# implement your REST API View class:
	class StoreList(APIView):
		permission_classes = (IsAuthenticated,)
		queryset = Store.objects.all()
		serializer_class = StoreSerializer
		def get(self, request, format=None):
			stores = Store.objects.all()
			serializer = StoreSerializer(stores, many=True)
			return Response(serializer.data)
		def post(self, request, format=None):
		...

	# implement your REST API View class:
	class RESTMyList(generics.ListCreateAPIView):
		#do!

## Model Relationships

### Model implementation: django.db
	MyModel.objects functions:
		.get_or_create(...)	# return: myModelObj, is_created
		.order_by('-title')
		.all()
		.exclude(id=request.user.id) # = all except me
		.filter(title=mytitleval, type=mytypeval, groups__name=mynameval).count()
		.get_for_model(obj)
		.get(id=myidval)	# throws if not found
		.create(...)
		.annotate(...)		# allows to add extra columns, eg. aggregations
		.count()
		
	models.F(colName)		# reference db field
	models.Case/.When/.Value

	# function get_next_by_{fieldname} available automatically:
	mymodel = MyModel.objects.all()[0]
	next_mymodel = mymodel.get_next_by_created().mymodel
	next_mymodel = mymodel.get_previous_by_created().mymodel

### define relationship:
	from django.db import models
	class MyModel(models.Model):
		mysub = models.ForeignKey(MySubModel) # optional: on_delete=models.CASCADE
		mysub = models.OneToOneField(MySubModel, on_delete=models.CASCADE|.DO_NOTHING, primary_key=True)
		mysubs = models.ManyToManyField(MySubModel,blank=True)
		#reference to the same model: use 'self'
		my = models.ForeignKey('self')
		mys = models.ManyToManyField('self')
### use relationship:
	all_mymodels_with_subs = MyModel.objects.filter(mysub=mysubval, (price__gt=1)
	# Reverse access through instance
	all_mymodels_with_subs = mysubval.mymodel_set.all()
	# output generated SQL
	stdlogger.debug("Query %s" % str(all_mymodels_with_subs.query))
	# You can also use print(all_mymodels_with_subs.query)

## Generic View = Class based Views with django Mixins:
	# useful Mixins:
	django.views.generic.detail.SingleObjectTemplateResponseMixin
	django.views.generic.base.TemplateResponseMixin
	django.views.generic.edit.BaseCreateView
	django.views.generic.edit.ModelFormMixin
	django.views.generic.edit.FormMixin
	django.views.generic.detail.SingleObjectMixin
	django.views.generic.edit.ProcessFormView
	from django.views.generic.list import ListView, UpdateView, DetailView
	django.views.generic.base.View
	# example mixin usage:
	from django.views.generic.edit import CreateView
	from django.contrib.messages.views import SuccessMessageMixin
	# in urlpatterns, use it as MyModelCreation.as_view()
	class MyModelCreation(SuccessMessageMixin,CreateView): # TemplateView also could be used as super
		template_name = 'my/my.html'
		model = MyModel
		form_class = MyModelForm
		success_url = reverse_lazy('mymodels:index')
		success_message = "MyModel %(name)s created successfully"

## Fake Email server for development purposes:
	$ python -m smtpd -n -c Debuggingserver localhost:1025
	# with mail settings:
	EMAIL_HOST = 'localhost'
	EMAIL_PORT = 1025

## Custom Middleware (settings.py MIDDLEWARE_CLASSES)
	from django.config import settings
	class MyMiddleware:
		def __init__(self, get_response):
			self.get_response = get_response
		def __call__(self, request):
			resp = self.get_response(request)
			return resp
		def process_view(self, request, view_func, view_args, view_kwargs):
			assert hasattr(request, 'user')
			if not request.user.is_authenticated():
				path = request.path_info.lstrip('/')
				if not any(url.match(path) for url in exempt_urls):
					return redirect(settings.LOGIN_URL)
			return None

## Command
	# -*- coding: UTF-8 -*-
	from __future__ import unicode_literals
	import csv
	from django.core.management.base import BaseCommand
	
	SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3

	# File: my_command.py
	class MyCommand(BaseCommand):
		help = (
			"My Command help text. "
			"My Command help text. "
		)
		def add_arguments(self, parser):
			# Positional arguments
			parser.add_argument(
				"file_path",
				nargs=1,
				type=unicode,
			)
		def handle(self, *args, **options):
			verbosity = options.get("verbosity", NORMAL)
			file_path = options["file_path"][0]
			
			if verbosity >= NORMAL:
				self.stdout.write("=== Working... ===")
			...
			
	# Call:
	python manage.py my_command data/my.csv

## Unit- & Integration Tests
	$ pip install selenium mock
	from django.test import LiveServerTestCase
	from django.test import SimpleTestCase
	class MyTest(SimpleTestCase):
		@classmethod
		def setUpClass(cls):
			super(MyTest, cls).setUpClass()
			# set up db ...
			
		@classmethod
		def tearDownClass(cls):
			super(MyTest, cls).tearDownClass()
			cls.mycreateddata.delete()

		def test_my(self):
			mock_request = mock.Mock()
			mock_request.user = self.superuser
			mock_request.method = "POST"
			response = call
			expected_result = json.dumps({
				"success": True
			})
			self.assertJSONEqual(
				response.content,
				expected_result
			)
### Test of API's
	from rest_framework.test import APITestCase
	class MyTest(APITestCase):								# has setUpClass & tearDownClass, too
		def test_my(self):
			self.client.force_authenticate(user=self.superuser)
			url = reverse("rest_list")
			data = {}
			response = self.client.get(url, data, format="json")
			self.assertEqual(
				response.status_code, status.HTTP_200_OK	# HTTP_201_CREATED, HTTP_403_FORBIDDEN etc.
			)
			self.assertEqual(
				response.data["count"], 3
			)
			self.client.force_authenticate(user=None)		# logout

## Forms
	from django import forms
	
	class MyForm(forms.Form):
		f1 = forms.CharField(required=True) # provides automatic validation

	# Form, connected to a Model:
	class MyForm(forms.ModelForm):
		f1 = forms.CharField(required=False)
		f2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'write...'}))
		class Meta:
			model = MyModel
			fields = ('f1',) # NOT ('f1')
		
### Use the form:
	class MyView(TemplateView):
		template_name = "my/my.html"

		def get(self, request):
			form = MyForm()
			mymodels = MyModel.objects.all().order_by('-created')
			return render(request, self.template_name, {'form':form, 'mymodels':mymodels})
			
		def post(self, request):
			form = MyForm(request.POST)
			if form.is_valid():
			
				## handling for ModelForm
				form.save() # possible if form is a ModelForm
				mymodel = form.save(commit=False)
				mymodel.user = request.user
				
				t = form.cleaned_data['f1']
				redirect('myappnamespace:myview') #avoid double submit possibility
			
			args = {'form':form, 'text':t}
			return render(request, self.template_name, args)

### Template:
	<form method=post>
		{% csrf_token %}
		{{ form.errors }}
		{{ form.as_p }}		# renders the whole form
		{{ form.f1 }}		# renders only the field
	</form>

## Configuration:
### Settings: use /settings/ instead of settings.py
	mkdir /settings/
		/settings/__init.py
		/settings/base.py		# put content of the old ../settings.py here & adjust paths if using __file__!
		/settings/local.py
		/settings/dev.py
			from myapp.settings.base import *
			try:
				from myapp.settings.local import *
			except:
				pass
			# override base.py settings here
			DEBUG = True
		/settings/prod.py
			from myapp.settings.base import *
			# override base.py settings here
			DEBUG = False
	$ export DJANGO_SETTINGS_MODULE=myapp.settings.dev
	/wsgi.py: os.environ.setdefault(DJANGO_SETTINGS_MODULE=myapp.settings.prod)

### Deployment: use env-variables & myapp.settings.prod, e.g. with new values for
	DEBUG = False # you HAVE to set ALLOWED_HOSTS
	SECRET_KEY
	DATABASES
	ALLOWED_HOSTS = ['*'] # = allow everything
	
	$ django-admin check --deploy

### Requirements: list dependencies
	mkdir /requirements/
		/requirements/base.txt
			Django==1.10.7				# example content
			Pillow==4.1.0				# needed, eg. for the ImageField
		/requirements/dev.txt			# env specific dependencies
			-r base.txt
		/requirements/prod.txt			# env specific dependencies
			-r base.txt

	$ pip install -r myapp/requirements/dev.txt
