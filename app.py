# This Python file uses the following encoding: utf-8

import os
import json
from bottle import *
from firebase import firebase

AUTH_TABLE_ADR = "/Auth"


def status_message(code, description=None):
    return json.dumps({'code': code, 'description': description})


class User:
    login = ""
    pwd = ""
    mail = ""
    telegram = ""
    subscriptions = {}

    def __init__(self, login, pwd, mail, telegram):
        self.login = login
        self.pwd = pwd
        self.mail = mail
        self.telegram = telegram
        self.subscriptions = {}

    @staticmethod
    def get_from_auth(login):
        return db.get(AUTH_TABLE_ADR, login)

    @staticmethod
    def login_exists(login):
        res = User.get_from_auth(login) is not None
        return res

    def exists(self):
        return User.login_exists(self.login)

    @staticmethod
    def get(login):
        d = User.get_from_auth(login)
        return User(d['login'],
                    d['pwd'],
                    d.get('mail', None),
                    d.get('telegram', None))

    @staticmethod
    def register(user):
        if not user.exists():
            db.post(AUTH_TABLE_ADR + "/" + user.login, user.__dict__)
            return status_message(200, 'Registration success')
        return status_message(406, 'Username already taken')

    @staticmethod
    def delete(login):
        if User.exists(login):
            db.delete(AUTH_TABLE_ADR, login)

    def update(self):
        User.delete(self.login)
        User.register(self)

    def add_subscriptions(self, source, *subscriptions):
        if source not in self.subscriptions.keys():
            self.subscriptions[source] = []

        for sub in subscriptions:
            self.subscriptions[source].append(sub)

        self.update()

    def delete_subscriptions(self, source, *subscriptions):
        for sub in subscriptions:
            self.subscriptions.get(source, []).remove(sub)
        self.update()


db = firebase.FirebaseApplication("https://jkdev-news.firebaseio.com/")


@get("/<login>/register")
def register(login):

    pwd = request.query['pwd']
    mail = request.query.get('mail', None)
    telegram = request.query.get('telegram', None)

    user = User(login, pwd, mail, telegram)
    return User.register(user)


@get("/<login>/addSubscription")
def add_sub(login):

    def add_multiple_subs(login, query):
        subs = json.loads(query['subscriptions'])
        user = User.get(login)
        user.add_subscriptions(query['source'], subs)

    def add_single_sub(login, query):
        user = User.get(login)
        user.add_subscriptions([query['subscriptions']])

    multiple = 'multiple' in request.query
    if multiple:
        add_multiple_subs(login, request.query)
    else:
        add_single_sub(login, request.query)

    return status_message('200', 'Success adding subscriptions')


@get("/<login>/deleteSubscription")
def delete_sub(login):

    def delete_single_sub(login, query):
        user = User.get(login)
        subs = query['subs']
        source = request.query['source']
        user.delete_subscriptions(source, [subs])

    def delete_multiple_subs(login, query):
        user = User.get(login)
        subs = json.loads(query['subs'])
        source = request.query['source']

        for sub in subs:
            user.delete_subscriptions(source, sub)

    multiple = 'multiple' in request.query
    if multiple:
        delete_multiple_subs(login, request.query)
    else:
        delete_single_sub(login, request.query)

    return status_message(200, 'Success deleting subscriptions')


# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
