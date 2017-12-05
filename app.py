# This Python file uses the following encoding: utf-8

import os
import json
from bottle import *
from firebase import firebase
from collections import OrderedDict

AUTH_TABLE_ADR = "/Auth"


def status_message(code, description=None):
    return json.dumps({'code': code, 'description': description})


class User:
    login = ""
    pwd = ""
    mail = ""
    telegram = ""
    subscriptions = {}

    def __init__(self, login, pwd, mail, telegram, subscriptions):
        self.login = login
        self.pwd = pwd
        self.mail = mail
        self.telegram = telegram
        self.subscriptions = subscriptions

    @staticmethod
    def get_from_auth(login):
        d = db.get(AUTH_TABLE_ADR, login)
        print("Thats the d", d)
        try:
            for i in d.values():
                print("The values id", d)
                return i
        except:
            return None


    @staticmethod
    def login_exists(login):
        res = User.get_from_auth(login) is not None
        return res

    def exists(self):
        print(self.login)
        return User.login_exists(self.login)

    @staticmethod
    def get(login):
        d = User.get_from_auth(login)
        return User(d['login'],
                    d['pwd'],
                    d.get('mail', None),
                    d.get('telegram', None),
                    d.get('subscriptions', {}))

    @staticmethod
    def register(user):
        if not user.exists():
            db.post(AUTH_TABLE_ADR + "/" + user.login, user.__dict__)
            return status_message(200, 'Registration success')
        return status_message(406, 'Username already taken')

    @staticmethod
    def delete(login):
        user = User.get(login)
        if user.exists():
            db.delete(AUTH_TABLE_ADR, login)

    def update(self):
        User.delete(self.login)
        User.register(self)

    def add_subscription(self, source, subscription):
        if not isinstance(self.subscriptions, dict):
            self.subscriptions = {}

        if source not in self.subscriptions.keys():
            print("NOT IN KEYS!")
            self.subscriptions[source] = []

        print(self.subscriptions)
        self.subscriptions[source].append(subscription)

        self.update()

    def delete_subscriptions(self, source, *subscriptions):
        for sub in subscriptions:
            subs = self.subscriptions.get(source, None)
            if subs is not None:
                if sub in subs:
                    subs.remove(sub)
                else:
                    return status_message(404, "Subscription not found")
            else:
                return status_message(404, "Source not found")
        self.update()


db = firebase.FirebaseApplication("https://jkdev-news.firebaseio.com/")


@get("/<login>/register")
def register(login):

    pwd = request.query['pwd']
    mail = request.query.get('mail', None)
    telegram = request.query.get('telegram', None)

    user = User(login, pwd, mail, telegram, {})
    return User.register(user)


@get("/<login>/addSubscription")
def add_sub(login):

    def add_multiple_subs(login, query):
        subs = json.loads(query['subscriptions'])
        user = User.get(login)
        for sub in subs:
            user.add_subscription(query['source'], sub)

    def add_single_sub(login, query):
        user = User.get(login)
        source = query.source
        user.add_subscription(source, query['subscriptions'])

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
        subs = query['subscriptions']
        source = request.query['source']
        user.delete_subscriptions(source, [subs])

    def delete_multiple_subs(login, query):
        user = User.get(login)
        subs = json.loads(query['subscriptions'])
        source = request.query['source']

        for sub in subs:
            user.delete_subscriptions(source, sub)

    multiple = 'multiple' in request.query
    if multiple:
        delete_multiple_subs(login, request.query)
    else:
        delete_single_sub(login, request.query)

    return status_message(200, 'Success deleting subscriptions')

@get("/<login>/uinfo")
def uinfo(login):
    return json.dumps(User.get(login).__dict__)


# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
