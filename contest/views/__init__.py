#-*- coding: utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )
from ..constants import LOGIN_SESSION_KEY
from ..models import DBSession
from ..models.user import User as UserModel


class View(object):

    def __init__(self, request):
        if LOGIN_SESSION_KEY in request.session:
            request.user = DBSession.query(UserModel).filter(
                UserModel.id == request.session[LOGIN_SESSION_KEY],
            ).first()

        self.request = request
        self.session = request.session


@view_defaults(route_name=u'home', renderer=u'home.jinja2')
class Home(View):

    @view_config(request_method=u'GET')
    def get(self):
        return {}
