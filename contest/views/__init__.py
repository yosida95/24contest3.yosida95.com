#-*- coding: utf-8 -*-

import re
import functools
from calendar import (
    Calendar,
    monthrange,
    )
from datetime import (
    date,
    datetime,
    timedelta,
    )
from pyramid.view import (
    view_defaults,
    view_config,
    )
from pyramid.httpexceptions import HTTPFound
from deform import (
    Form,
    Button,
    )
from ..constants import LOGIN_SESSION_KEY
from ..models import DBSession
from ..models.plan import PlanList
from ..models.user import User as UserModel
from ..schemas.plan import Plan as PlanSchema


def login_required():
    def receive_view(view):
        @functools.wraps(view)
        def decorator(self):

            if hasattr(self.request, u'user') and self.request.user is not None:
                return view(self)
            return HTTPFound(location=self.request.route_path('login'))
        return decorator
    return receive_view


class View(object):

    def __init__(self, request):
        if LOGIN_SESSION_KEY in request.session:
            request.user = DBSession.query(UserModel).filter(
                UserModel.id == request.session[LOGIN_SESSION_KEY],
            ).first()
        else:
            request.user = None

        self.request = request
        self.session = request.session


@view_defaults(route_name=u'home', renderer=u'home.jinja2')
class Home(View):

    def __init__(self, request):
        super(Home, self).__init__(request)
        schema = PlanSchema().bind(request=self.request)
        self.plan_form = Form(schema,
            buttons=(Button(title=u'登録'), ),
            method='post',
            action=self.request.route_path('plan'),
        )

    @view_config(request_method=u'GET')
    def get(self):
        if self.request.user is not None:
            now = datetime.now()
            if 0 <= now.hour < 12:
                day_for_new_plan = date.today()
                day_for_evaluate_plan = date.today() - timedelta(days=1)
            elif 21 <= now.hour <= 24:
                day_for_new_plan = date.today() + timedelta(days=1)
                day_for_evaluate_plan = date.today()
            else:
                day_for_new_plan = None
                day_for_evaluate_plan = None

            if day_for_new_plan is not None:
                list_of_new_plan = DBSession.query(PlanList).filter(
                    PlanList.user == self.request.user,
                    PlanList.date == day_for_new_plan,
                ).first()
                if list_of_new_plan is None:
                    list_of_new_plan = PlanList(
                        self.request.user, day_for_new_plan)
                    DBSession.add(list_of_new_plan)
            else:
                list_of_new_plan = None

            if day_for_evaluate_plan is not None:
                list_of_evaluate_plan = DBSession.query(PlanList).filter(
                    PlanList.user == self.request.user,
                    PlanList.date == day_for_evaluate_plan,
                ).first()
                if list_of_evaluate_plan is None:
                    list_of_evaluate_plan = PlanList(
                        self.request.user, day_for_evaluate_plan)
                    DBSession.add(list_of_evaluate_plan)
            else:
                list_of_new_plan = None

            if u'cal' in self.request.GET:
                match = re.match(r'^([0-9]{4})-([01][0-9])$',
                                 self.request.GET.get(u'cal', u''))
                if match:
                    year, month = int(match.group(1)), int(match.group(2))
                else:
                    today = date.today()
                    year, month = today.year, today.month
            else:
                today = date.today()
                year, month = today.year, today.month
            calendar = (
                date(year, month, 1),
                Calendar(6).monthdatescalendar(year, month),
                date(year, month, monthrange(year, month)[1]),
            )

            now = datetime.now()
            if 0 <= now.hour < 12:
                today_on_history = date.today() - timedelta(days=1)
            else:
                today_on_history = date.today()

            return {
                'day_for_new_plan': day_for_new_plan,
                'list_of_new_plan': list_of_new_plan,
                'day_for_evaluate_plan': day_for_evaluate_plan,
                'list_of_evaluate_plan': list_of_evaluate_plan,
                'add_plan_form': self.plan_form.render({
                    'date': day_for_new_plan}),
                'calendar': calendar,
                'today_on_history': today_on_history,
            }
        return {}
