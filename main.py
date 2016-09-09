#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import webapp2
from google.appengine.api import mail, app_identity
from models import Game
import utils


class Handler(webapp2.RequestHandler):

    def send_mail(self, body, subject, email):
        app_id = app_identity.get_application_id()
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       email,
                       subject,
                       body)


class SendReminderEmail(Handler):

    def get(self):
        """Send a reminder email to each player with an email about games.
        Called every hour using a cron job"""
        games = Game.query(Game.status != "over")
        subject = 'This is a reminder!'
        body = 'Hello {}, You have a race waiting. Try to win your race!'
        for game in games:
            body.format(game.player.get().username)
            self.send_mail(body, subject, game.player.get().username)
            if game.opponent.get().username != "computer":
                body.format(game.opponent.get().username)
                self.send_mail(body, subject, game.opponent.get().email)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)

], debug=True)
