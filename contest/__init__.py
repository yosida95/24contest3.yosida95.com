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
    config.add_route('home', '/home')
    config.add_route('join', '/join')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
