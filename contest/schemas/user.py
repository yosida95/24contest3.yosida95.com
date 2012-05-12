#-*- coding: utf-8 -*-

from pyramid_deform import CSRFSchema
from colander import (
    SchemaNode,
    String,
    )
from deform.widget import (
    CheckedPasswordWidget,
    PasswordWidget,
    )


class Join(CSRFSchema):
    handle = SchemaNode(String(), title=u'ハンドル')
    password = SchemaNode(String(), title=u'パスワード',
        widget=CheckedPasswordWidget())


class Login(CSRFSchema):
    handle = SchemaNode(String(), title=u'ハンドル')
    password = SchemaNode(String(), title=u'パスワード',
        widget=PasswordWidget())
