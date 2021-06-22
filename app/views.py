from tornado.web import HTTPError, RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future
from tornado.gen import coroutine

import json
import datetime

from app.models import User, Task


class BaseView(RequestHandler, SessionMixin):
    """Base view for this application."""

    def prepare(self):
        self.form_data = {
            key: [val.decode('utf8') for val in val_list]
            for key, val_list in self.request.arguments.items()
        }

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        self.set_status(status)
        self.write(json.dumps(data))


class TaskListView(BaseView):
    """View for reading and adding new tasks."""
    SUPPORTED_METHODS = ("GET", "POST",)

    @coroutine
    def get(self, username):
        """Get all tasks for an existing user.
        GET http://localhost:8888/user/somename
        """
        with self.make_session() as session:
            profile = yield as_future(session.query(User).filter(User.username == username).first)
            if profile:
                tasks = [task.to_dict() for task in profile.tasks]
                self.send_response({
                    'username': profile.username,
                    'tasks': tasks
                })
            else:
                self.send_response({
                    'username': username,
                    'tasks': 'No data availeble by this username!'
                })


    @coroutine
    def post(self, username):
        """Create a new task."""
        with self.make_session() as session:
            profile = yield as_future(session.query(User).filter(User.username == username).first)
            if profile:
                due_date = self.form_data['due_date'][0]
                task = Task(
                    name=self.form_data['name'][0],
                    note=self.form_data['note'][0],
                    creation_date=datetime.now(),
                    due_date=datetime.strptime(due_date, '%d/%m/%Y %H:%M:%S') if due_date else None,
                    completed=self.form_data['completed'][0],
                    profile_id=profile.id,
                    profile=profile
                )
                session.add(task)
                self.send_response({'msg': 'posted'}, status=201)


class UserListView(BaseView):
    """View for reading and adding new tasks."""
    SUPPORTED_METHODS = ("GET", "POST", "DELETE")

    @coroutine
    def get(self, id=None):
        """Get users"""
        with self.make_session() as session:
            profiles = session.query(User).all()
            users = [profile.as_dict() for profile in profiles]
            self.send_response({'users': users})

    @coroutine
    def post(self, id=None):
        """Create a new user."""
        with self.make_session() as session:
            print(self.form_data)
            user = User(
                username=self.form_data['name'][0],
                password=self.form_data['password'][0]
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            self.send_response({'Created user': user.as_dict()}, status=201)

    @coroutine
    def delete(self, id):
        with self.make_session() as session:
            user = yield as_future(session.query(User).filter(User.id == id).first)
            if not user:
                raise HTTPError(404)
            session.delete(user)
            session.commit()
            self.set_status(204)

                

class MainHandler(RequestHandler):

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self, id):
        response = {
            'id': id
        }
        self.write(response)


class PredictHandler(RequestHandler):

    def prepare(self):
        self.form_data = {
            key: val_list[0].decode('utf8')
            for key, val_list in self.request.arguments.items()
        }


    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        self.set_status(status)
        self.write(json.dumps(data))


    def post(self):
        # data = self.get_argument('key')
        data = self.form_data
        print(self.request.body)
        # self.set_status(201)
        # self.write({"Send data": data})
        self.send_response(data, status=201)


class InfoView(BaseView):
    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def get(self):
        """List of routes for this API."""
        routes = {
            'info': 'GET /api/v1',
            'register': 'POST /api/v1/accounts',
            'single profile detail': 'GET /api/v1/accounts/<username>',
            'edit profile': 'PUT /api/v1/accounts/<username>',
            'delete profile': 'DELETE /api/v1/accounts/<username>',
            'login': 'POST /api/v1/accounts/login',
            'logout': 'GET /api/v1/accounts/logout',
            "user's tasks": 'GET /api/v1/accounts/<username>/tasks',
            "create task": 'POST /api/v1/accounts/<username>/tasks',
            "task detail": 'GET /api/v1/accounts/<username>/tasks/<id>',
            "task update": 'PUT /api/v1/accounts/<username>/tasks/<id>',
            "delete task": 'DELETE /api/v1/accounts/<username>/tasks/<id>'
        }
        self.send_response(routes)
