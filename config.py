import os
basedir= os.path.abspath(os.path.dirname(__name__))

class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    BLOGPOLE_MAIL_SUBJECT_PREFIX='Blogpole'
    FLASK_MAIL_SENDER='Blogpole Admin'
    BLOGPOLE_ADMIN=os.environ.get('BLOGPOLE_ADMIN')
    BLOGPOLE_MAIL_SENDER=os.environ.get('BLOGPOLE_MAIL_SENDER')
    BLOGPOLE_POSTS_PER_PAGE=20
    BLOGPOLE_FOLLOWERS_PER_PAGE=10
    BLOGPOLE_COMMENTS_PER_PAGE=10

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER= 'smtp.googlemail.com'
    MAIL_PORT= 587
    MAIL_USE_TLS= True
    MAIL_USERNAME= os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD= os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///'+ os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    Testing=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///'+ os.path.join(basedir, 'data-test.sqlite')
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+ os.path.join(basedir, 'data.sqlite')
config={
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}
