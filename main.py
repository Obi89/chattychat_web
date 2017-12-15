#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

        user = users.get_current_user()
        params["user"] = user

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
        else:
            logged_in = False
            login_url = users.create_login_url('/chattychat')
            params["login_url"] = login_url

        params["logged_in"] = logged_in

        template = jinja_env.get_template(view_filename)

        return self.response.out.write(template.render(params))

class Message(ndb.Model):
    name = ndb.StringProperty()
    message = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("main.html")

class ChattyChat(BaseHandler):
    def get(self):
        messages = Message.query()

        params = {"messages": messages}

        return self.render_template("chattychat.html", params=params)

    def post(self):
        name = self.request.get("name")
        message = self.request.get("message")

        if not name:
            name = "Anonymous"

        if "<script>" in message:
            return self.write("Can't hack me!")

        msg_object = Message(name = name, message=message.replace("<script>", ""))
        msg_object.put()

        return self.redirect_to("chattychat-site")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/chattychat', ChattyChat, name="chattychat-site"),
], debug=True)