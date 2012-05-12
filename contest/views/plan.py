#-*- coding: utf-8 -*-

import re
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
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from deform import (
    Form,
    ValidationFailure,
    )
from . import (
    View,
    login_required,
    )
from ..models import DBSession
from ..schemas.plan import Plan as PlanSchema
from ..models.plan import (
    Plan as PlanModel,
    PlanList as PlanListModel,
    )


@view_defaults(route_name='plan', renderer='json')
class Plan(View):

    def __init__(self, request):
        super(Plan, self).__init__(request)
        schema = PlanSchema().bind(request=self.request)
        self.form = Form(schema)

        now = datetime.now()
        if 0 <= now.hour < 12:
            self.day_for_new_plan = date.today()
            self.day_for_evaluate_plan = date.today() - timedelta(days=1)
        elif 21 <= now.hour <= 24:
            self.day_for_new_plan = date.today() + timedelta(days=1)
            self.day_for_evaluate_plan = date.today()
        else:
            self.day_for_new_plan = None
            self.day_for_evaluate_plan = None

    @view_config(request_method='POST')
    def post(self):
        if self.request.user is not None:
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except ValidationFailure:
                result = False
                message = u'入力内容に誤りがあります'
            else:

                if captured.get('date') == self.day_for_new_plan:
                    list = DBSession.query(PlanListModel).filter(
                        PlanListModel.user == self.request.user,
                        PlanListModel.date == self.day_for_new_plan,
                    ).first()
                    if list is None:
                        list = PlanListModel(
                            self.request.user, self.day_for_new_plan)
                        DBSession.add(list)

                    plan = captured.get('plan')
                    _plan = DBSession.query(PlanModel).filter(
                        PlanModel.plan_list == list,
                        PlanModel.subject == plan,
                    ).first()
                    if _plan is None:
                        _plan = PlanModel(plan)
                        list.plans.append(_plan)
                    else:
                        _plan.deleted = False

                    result = True
                    message = u'登録しました。帰宅後が楽しみですね！'

                else:
                    result = False
                    message = u'やりたいことの登録は、前日の20時以降または当日の10時以前のみ可能です。'
        else:
            result = True
            message = u'ログインしてください'

        return {'result': result, 'message': message}

    @view_config(request_method='PUT')
    def put(self):
        csrf_token = self.request.params.get(u'csrf_token', '')
        plan_id = self.request.params.get(u'plan_id', '')

        if self.request.user is None:
            result = False
            message = u'ログインしてください'
        else:
            plan = DBSession.query(PlanModel).filter(
                PlanModel.id == plan_id,
            ).first()

            if csrf_token == self.session.get_csrf_token() and\
            plan is not None and\
            plan.plan_list.user == self.request.user and\
            plan.plan_list.date == self.day_for_evaluate_plan:
                result = True
                message = u''

                if self.request.params.get(u'done') == u'true':
                    plan.check_as_done()
                    message += u'おめでとうございます。楽しめましたか？\n'
            else:
                result = False
                message = u'不正なリクエストです'

        return {u'result': result, u'message': message}

    @view_config(request_method='DELETE')
    def delete(self):
            csrf_token = self.request.params.get(u'csrf_token', '')
            plan_id = self.request.params.get(u'plan_id', '')

            if self.request.user is None:
                result = False
                message = u'ログインしてください'
            else:
                if csrf_token == self.session.get_csrf_token():
                    plan = DBSession.query(PlanModel).filter(
                        PlanModel.id == plan_id,
                    ).first()

                    if plan is not None and\
                    plan.plan_list.user == self.request.user and\
                    plan.plan_list.date == self.day_for_new_plan:
                        plan.check_as_delete()
                        result = True
                        message = u'削除しました'
                    else:
                        result = False
                        message = u'不正なリクエストです'
                else:
                    result = False
                    message = u'不正なリクエストです'

            return {'result': result, 'message': message}


@view_defaults(route_name=u'history', renderer=u'history.jinja2')
class History(View):

    @view_config(request_method=u'GET')
    @login_required()
    def get(self):
        match = re.match(r'^([0-9]{4})-([01][0-9])-([0-3][0-9])$',
                self.request.matchdict.get(u'date'))
        if match is None:
            raise HTTPNotFound()

        now = datetime.now()
        if 0 <= now.hour < 12:
            today_on_history = date.today() - timedelta(days=1)
        else:
            today_on_history = date.today()

        year, month, day = (
            int(match.group(1)), int(match.group(2)), int(match.group(3)))
        try:
            day = date(year, month, day)
        except Exception:
            raise HTTPBadRequest()
        else:
            if day > today_on_history:
                raise HTTPNotFound()

        list = DBSession.query(PlanListModel).filter(
            PlanListModel.date == day,
            PlanListModel.user == self.request.user,
        ).first()

        calendar = (
            date(year, month, 1),
            Calendar(6).monthdatescalendar(year, month),
            date(year, month, monthrange(year, month)[1]),
        )

        return {u'list': list, u'calendar': calendar,
                u'today_on_history': today_on_history}
