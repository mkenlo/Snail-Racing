
from protorpc import messages
from google.appengine.ext import ndb


class Player(ndb.Model):
    """ This class describes a player"""
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)


class Game(ndb.Model):
    """ This class describes an encounter between two players"""
    player = ndb.KeyProperty(kind='Player', required=True)
    opponent = ndb.KeyProperty(kind='Player')
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.StringProperty(default="start")

    def gameOver(self, winner):
        winner_score = Score.query(Score.game == self.key,
                                   Score.player == winner.player).get()
        winner_score.won = True
        winner_score.put()
        self.status = "over"
        self.put()


class Position(ndb.Model):
    """ This class describes a player"""
    game = ndb.KeyProperty(kind='Game')
    player = ndb.KeyProperty(kind='Player')
    position = ndb.IntegerProperty(default=0)
    isPlayingNow = ndb.BooleanProperty(default=False)


class Score(ndb.Model):
    """ This class records a player score"""
    game = ndb.KeyProperty(kind='Game')
    player = ndb.KeyProperty(kind='Player')
    score = ndb.IntegerProperty(default=0)
    won = ndb.BooleanProperty(default=False)

    def toForm(self):
        return HistoryForm(player=self.player.get().username,
                           score=self.score,
                           created="{}".format(self.game.get().created))


class GameHistory(ndb.Model):
    game = ndb.KeyProperty(kind='Game')
    message = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    def toForm(self):
        players = "%s VS %s" % (self.game.get().player.get(
        ).username, self.game.get().opponent.get().username)
        return GameHistoryForm(player_opponent=players,
                               message=self.message,
                               date=str(self.date))



# Messages classes for Request and Response

class PlayerForm(messages.Message):
    username = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class NewGameForm(messages.Message):
    player = messages.StringField(1, required=True)
    opponent = messages.StringField(2)
    urlsafekey = messages.StringField(3)


class GameForm(messages.Message):
    urlsafekey = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    player = messages.StringField(1, required=True)
    dice = messages.IntegerField(2, required=True)
    position = messages.IntegerField(3, required=True)
    score = messages.IntegerField(4, required=True)
    status = messages.StringField(5)


class MessageForm(messages.Message):
    message = messages.StringField(1, required=True)


class HistoryForm(messages.Message):
    player = messages.StringField(1)
    score = messages.IntegerField(2)
    created = messages.StringField(3)


class ListHistoryForm(messages.Message):
    history = messages.MessageField(HistoryForm, 1, repeated=True)


class GameHistoryForm(messages.Message):
    player_opponent = messages.StringField(1)
    message = messages.StringField(2)
    date = messages.StringField(3)


class ListGameHistory(messages.Message):
    history = messages.MessageField(GameHistoryForm, 1, repeated=True)


class RankingForm(messages.Message):
    player = messages.StringField(1)
    number_games = messages.IntegerField(2)
    won = messages.IntegerField(3)


class ListRanking(messages.Message):
    items = messages.MessageField(RankingForm, 1, repeated=True)
