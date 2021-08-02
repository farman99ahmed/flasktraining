import configparser
from flask import Flask

class App():
    def __init__(self, config_file):
        self.parms = self.__read_config(config_file)
        app = Flask(self.parms['app_name'])
        app.config.update(
            DEBUG = self.parms['app_debug'],
            SECRET_KEY = self.parms['app_secret'],
            SQLALCHEMY_DATABASE_URI = self.parms['sqlalchemy_uri'],
            SQLALCHEMY_ECHO = self.parms['sqlalchemy_echo'],
            SQLALCHEMY_TRACK_MODIFICATIONS = self.parms['sqlalchemy_trackmodifications'],
        )
        self.app = app

    def __read_config(self, config_file):
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            parms = {}
            parms['app_name'] = config.get('app', 'name')
            parms['app_debug'] = config.getboolean('app', 'debug')
            parms['app_secret'] = config.get('app', 'secret')
            parms['endpoint_host'] = config.get('endpoint', 'host')
            parms['endpoint_port'] = config.get('endpoint', 'port')
            parms['sqlalchemy_uri'] = config.get('sqlalchemy', 'uri')
            parms['sqlalchemy_echo'] = config.getboolean('sqlalchemy', 'echo')
            parms['sqlalchemy_trackmodifications'] = config.getboolean('sqlalchemy', 'trackmodifications')

        except Exception as e:
            raise(e)
        return parms