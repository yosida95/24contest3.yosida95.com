#-*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from deform import (
    Form,
    Button,
    ValidationFailure,
    )
from ..constants import LOGIN_SESSION_KEY
from . import View
from ..schemas.user import (
    Login as LoginSchema,
    Join as JoinSchema,
    )
from ..models import DBSession
from ..models.user import (
    User as UserModel,
    Login as LoginModel,
    )


@view_defaults(route_name=u'join', renderer=u'join.jinja2')
class Join(View):

    def __init__(self, request):
        super(Join, self).__init__(request)
        schema = JoinSchema().bind(request=self.request)
        self.form = Form(schema,
            buttons=(Button(title=u'Join!'), ),
            method=u'post',
            action=self.request.route_path('join'))

    @view_config(request_method=u'GET')
    def get(self):
        return {'form': self.form.render()}

    @view_config(request_method=u'POST')
    def post(self):
        try:
            controls = self.request.POST.items()
            captured = self.form.validate(controls)
        except ValidationFailure, why:
            response = {'form': why.render()}
        else:
            user = UserModel(captured.get(u'handle'))
            login = LoginModel(user)
            login.set_password(captured.get(u'password'))
            DBSession.add_all((user, login))

            self.session.clear()
            self.session[LOGIN_SESSION_KEY] = user.id
            response = HTTPFound(location=self.request.route_path('home'))

        return response


@view_defaults(route_name=u'login', renderer=u'login.jinja2')
class Login(View):

    def __init__(self, request):
        super(Login, self).__init__(request)
        schema = LoginSchema().bind(request=self.request)
        self.form = Form(schema,
            buttons=(Button(title=u'Login!'), ),
            method=u'post',
            action=self.request.route_path('login'))

    @view_config(request_method=u'GET')
    def get(self):
        return {'form': self.form.render()}

    @view_config(request_method=u'POST')
    def post(self):
        try:
            controls = self.request.POST.items()
            captured = self.form.validate(controls)
        except ValidationFailure, why:
            response = {'form': why.render()}
        else:
            user = DBSession.query(UserModel).filter(
                UserModel.handle == captured.get(u'handle'),
            ).first()

            if user is None:
                response = {'form': self.form.render()}
            else:
                if user.login.authenticate(captured.get(u'password')):
                    self.session.clear()
                    self.session[LOGIN_SESSION_KEY] = user.id
                    response = HTTPFound(
                        location=self.request.route_path(u'home'))
                else:
                    response = {'form': self.form.render()}

        return response


@view_defaults(route_name=u'logout', renderer=u'logout.jinja2')
class Logout(View):

    @view_config(request_method=u'GET')
    def get(self):
        self.session.clear()
        self.request.user = None

        return {}
