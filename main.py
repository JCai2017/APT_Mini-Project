from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

DEFAULT_NAME = 'default_connex'


def connex_key():
    return ndb.Key('Connex', DEFAULT_NAME)


class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=True)
    coverImage = ndb.StringProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)


class User(ndb.Model):
    identity = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    created = ndb.LocalStructuredProperty(Stream, repeated=True)
    subscribed = ndb.LocalStructuredProperty(Stream, repeated=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        createdStreams = []
        subscribedStreams = []
        if user:
            nickname = user.nickname()
            userId = user.user_id()
            logout_url = users.create_logout_url(self.request.uri)
            create_url = '/create_stream'
            greeting = 'Welcome, {}! <a href ="{}">Create a Stream</a> \
                       (<a href ="{}">Sign Out</a>)'.format(
                        nickname, create_url, logout_url)
            query = User.query(User.identity == userId)
            userData = query.get()
            if userData:
                createdStreams = userData.created
                subscribedStreams = userData.subscribed

        else:
            login_url = users.create_login_url(self.request.uri)
            greeting = '<a href="{}">Sign In</a>'.format(login_url)

        self.response.write(
                '<html><body>{}</body></html>'.format(greeting))


class CreateStream(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userId = user.user_id()
        greeting = '<a href="{}">Submit</a>'.format('/')
        self.response.write('<html><body>{}</body></html>'.format(greeting))

    def post(self):
        user = users.get_current_user()
        userId = user.user_id()
        query = User.query(User.identity == userId)
        userData = query.get()
        data = User(parent=connex_key())
        status = 0
        tagList = self.request.get('tags').split(",")

        if userData:
            userData.name = user.nickname()
            userData.created.append(Stream(
                name=self.request.get('name'),
                url=self.request.get('url'),
                coverImage=self.request.get('image'),
                tags=tagList))
            status = userData.put()

        else:
            data.identity = userID
            data.name = user.nickname()
            data.created.append(Stream(name=self.request.get('name'),
                                       url=self.request.get('url'),
                                       coverImage=self.request.get('image'),
                                       tags=tagList))
            status = data.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create_stream', CreateStream),
], debug=True)