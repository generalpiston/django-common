import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.conf import settings

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi


DEFAULT_STATIC_PATH = os.path.join(os.getcwd(), 'static')


class Command(BaseCommand):
    args = ''
    option_list = BaseCommand.option_list + (
        make_option('--port',
            action='store',
            dest='port',
            default='80',
            help='Port to run on'),
        make_option('--static-path',
            action='store',
            dest='static-path',
            default=DEFAULT_STATIC_PATH,
            help='Location of static path'),
    )
    help = 'Start tornado server'

    def handle(self, *args, **options):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        container = tornado.wsgi.WSGIContainer(get_wsgi_application())
        application = tornado.web.Application([
            ('.*', tornado.web.FallbackHandler, dict(fallback=container))
        ], **{
            'static_path': options['static-path'],
            'debug': settings.DEBUG
        })
        server = tornado.httpserver.HTTPServer(application)
        server.listen(options['port'])
        tornado.ioloop.IOLoop.instance().start()
