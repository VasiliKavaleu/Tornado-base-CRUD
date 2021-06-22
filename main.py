import tornado.ioloop
import tornado.web
from tornado.options import define, options
from tornado.httpserver import HTTPServer
import uuid

from app.views import MainHandler, PredictHandler, InfoView, TaskListView, UserListView

import os
from tornado_sqlalchemy import SQLAlchemy
from core.db import SQLALCHEMY_DATABASE_URL


define("port", default=8888, help="Run on thre given port", type=int)
# factory = make_session_factory(SQLALCHEMY_DATABASE_URL)
factory = SQLAlchemy(SQLALCHEMY_DATABASE_URL)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/getby/(\w+)", MainHandler),
            (r"/predict", PredictHandler),
            (r"/info", InfoView),
            (r"/user/(\w+)", TaskListView),
            (r"/users/([^/]+)?", UserListView),
        ]
        #db=factory,
        settings = dict(
            # xsrf_cookies=True,
            cookie_secret= uuid.uuid4().int,
            debug=True,
            db=SQLAlchemy(SQLALCHEMY_DATABASE_URL)
        )

        super(Application, self).__init__(handlers, **settings)


if __name__ == "__main__":
    app = Application()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print('Listening on http://localhost:%i' % options.port)
    tornado.ioloop.IOLoop.current().start()
