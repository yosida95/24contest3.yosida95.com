#-*- coding: utf-8 -*-

from colander import (
    Date,
    SchemaNode,
    String,
    )
from pyramid_deform import CSRFSchema
from deform.widget import HiddenWidget


class Plan(CSRFSchema):
    plan = SchemaNode(String(), title=u'やりたいこと')
    date = SchemaNode(Date(),
        widget=HiddenWidget())
