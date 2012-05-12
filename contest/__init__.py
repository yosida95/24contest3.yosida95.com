#-*- coding: utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from .models import DBSession

session_factory = UnencryptedCookieSessionFactoryConfig(
    'TDKb7XQ3SdgafTBEVrsXC325TYaXpEM3')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings,
                          session_factory=session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
