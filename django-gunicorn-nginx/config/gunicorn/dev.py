import os.path

from project.settings import BASE_DIR

"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "project.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = "0.0.0.0:8000"
# Restart workers when code changes (development only!)
reload = True
# Write access and error info to /var/log
accesslog = os.path.join(BASE_DIR, "logs/gunicorn-dev-access.log")
errorlog = os.path.join(BASE_DIR, "logs/gunicorn-dev-error.log")
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = os.path.join(BASE_DIR, "logs/gunicorn-dev.pid")
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
