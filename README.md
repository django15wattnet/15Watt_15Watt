# Wsgi
A slim, fast and comfortable WSGI-Framework for Python 3.x.  
Uses https://github.com/defnull/multipart for handling the multipart/form-data requests instaed of cgi.FieldStorage.

## Installation
For now, no [pip-package](https://pypi.org/) is available.  
You can clone the [repository](https://github.com/django15wattnet/Wsgi) and
install the package in a directory, from where you can import
python packages. 
```
    cd /path/to/your/import/able/python/packages
    git clone git@github.com:django15wattnet/Wsgi.git
```

## Usage

### The Apache2 Configuration
Read the [mod_wsgi docu](https://modwsgi.readthedocs.io/en/master/configuration.html).
```
    <VirtualHost x.x.x.x:port>
        ServerName your.server.name
        DocumentRoot /path/to/static/files                          # Where your static html-files are stored
        
        WSGIScriptAlias / /path/to/python/files/application.py      # Where your application.py is stored and invoked by calling http[s]://your.server.name/
        WSGIProcessGroup name_of_your_wsgi_daemon_process           # The name of your WSGIDaemonProcess
        
        # For development, each request loads a new python interpreter / application.py, no need the reload the web server
        WSGIDaemonProcess name_of_your_wsgi_daemon_process user=yourUnixYuser group=yourUnixGroup processes=1 threads=1 maximum-requests=1 home=/path/to/python/files python-path=/path/to/python/files
        
        # For a production enviroment change processes, threads and maximum-requests to your needes
        
        # The confiuration for the static files
        <Directory /path/to/static/files/>
        # Read the Apache2 docu https://httpd.apache.org/docs/2.4/mod/core.html#directory
           Options -Indexes -FollowSymLinks -MultiViews -Includes
           AllowOverride None
           Require all granted
           allow from all
        </Directory>
        
        # The configuration for the application directory
        <Directory /path/to/python/files/>
        # Read the Apache2 docu https://httpd.apache.org/docs/2.4/mod/core.html#directory
            Require all granted
            Options FollowSymLinks
            AllowOverride None
            Header set Access-Control-Allow-Origin '*'          # I'm not sure if this is needed
        </Directory>
        
        # Alias for the static, directly by the web server, deliveryed files and directories
        Alias /favicon.ico /path/to/static/files/favicon.ico
        Alias /css/ /path/to/static/files/css/
        Alias /js/ /path/to/static/files/js/
        Alias /img/ /path/to/static/files/img/ 
        
        ...
        
        # Your other Apache configurations
        
        </VirtualHost>
```

### Project Layout

### The Application
Create a ```application.py``` file in ```/path/to/python/files```:
```  
#!/usr/bin/env python
from Wsgi.Kernel import Kernel

kernel = None

def application(env: dict, start_response):
	global kernel

	if kernel is None:
		kernel = Kernel()

	return kernel.run(env=env, startResponse=start_response)
```
All requests are handled by the Kernel.run method.  ```WSGIScriptAlias / /path/to/python/files/application.py```  
The Kernel is a singleton and is created only once per lifetime of the application. By this, the configuration und the routes are loaded only once.  
**Only files and / or directories definded by Apache Alias directives are delivered by the web server drircetly!**

### Routes
The routes definitions tells the Kernel witch request path ist mapped to witch controller and method.  
Create a ```routes.py``` file in ```/path/to/python/files```:

#### Example routes without parameters in the path
```
from Wsgi.Route import Route, HttpMethods

routes = [
	Route(
		path='/',
		nameController='Controllers.AggregationController.AggregationController',
		nameMethod='staticPageAction',
		httpMethod=HttpMethods.GET
	),
	Route(
		path='/qcell',
		nameController='QCell.StaticPagesController.StaticPagesController',
		nameMethod='indexAction',
		httpMethod=HttpMethods.GET
	),
]
```
A request to ```/``` will be handled by ```from Controllers.AggregationController import AggregationController```  ```staticPageAction``` method.  
A request to ```/qcell``` will be handled by ```from QCell.StaticPagesController import StaticPagesController```  ```indexAction``` method.

#### Example routes with parameters in the path
```
from Wsgi.Route import Route, HttpMethods

routes = [
	Route(
		path='/do/{id}//{what}',
		nameController='Controllers.DoWiredStuffController.DoWiredStuffController',
		nameMethod='doStuffAction',
		httpMethod=HttpMethods.GET,
		params = {
                    'id': 'int',
                    'what': 'str'
                }
	),
    ...
]
```
A request to ```/do/42/machWas``` will be handled by ```from Controllers.DoWiredStuffController import DoWiredStuffController```  ```doStuffAction``` method with the parameters ```id=42``` and ```what='machWas'```.  
The types of the parameters in the path can be python types ``ìnt`` or ```str```.

### The Request Class
represents the request from the client.  
Have a look at the, hopefully, well documented code.

### The Response Class
represents the response send to the client.  
Have a look at the, hopefully, well documented code.

### Controllers
The controllers orchestrate the work to be done. Receive the request, do the work and return the response.

#### A very simple example Controller
```
from Wsgi.BaseController import BaseController
from Wsgi.Request import Request
from Wsgi.Response import Response


class TimeController(BaseController):

	def __init__(self, config: dict):
		super().__init__(config=config)


	def getAction(self, request: Request, response: Response):
		response.stringContent = 'Hello World'
		response.contentType = 'text/plain
		response.returnCode = 200
		return
```
Will send the string 'Hello World' with the content type 'text/plain' and the return code 200 to the client.  
Do what ever you want in the getAction method 😊.

### Templates
I use [Cheetah3](https://cheetahtemplate.org/) for the templates.  
Use what ever you like as your template engine.  
At this moment (2024-06-01) I'm not shure the BaseTplController is necessary.

### Models
Have a look at the DoDos.  
Use what ever you like as your ORM or database access.

## ToDos
- Make the use of [SqlObject](https://www.sqlobject.org/) optional
- Change the language of the comments and documentation from german to english
- Make a [pip-package](https://pypi.org/)
- Write and test a configuration for [nginx](https://nginx.org/)