# note: taken from https://github.com/conradho/dashingdemo
import sys

# add your project directory to the sys.path
project_home = u"/home/sborms/findasimilarprocyclist"
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# need to pass the Flask app as "application" for WSGI to work
# for a Dash app, that is at app.server
# see https://plot.ly/dash/deployment
from app import app
application = app.server