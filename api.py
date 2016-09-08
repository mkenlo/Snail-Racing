import endpoints
import hashlib
import random
import utils
from itertools import groupby
from models import PlayerForm
from models import GameForm
from models import NewGameForm
from models import NewGameForm
from models import MakeMoveForm
from models import MessageForm
from models import GameHistoryForm
from models import HistoryForm
from models import ListHistoryForm
from models import ListGameHistory
from models import RankingForm
from models import ListRanking
from models import Player
from models import Game
from models import GameHistory
from models import Score
from models import Position
from protorpc import message_types
from protorpc import messages
from protorpc import remote

PLAYER_FORM_REQUEST = endpoints.ResourceContainer(
    PlayerForm,
    passwd=messages.StringField(2, required=True))

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    player=messages.StringField(1, required=True),
    opponent=messages.StringField(2),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    game_urlsafekey=messages.StringField(1, required=True),
    player=messages.StringField(2, required=True),
    dice=messages.IntegerField(3, required=True),)

FIRSTPLAYER_REQUEST = endpoints.ResourceContainer(
    game_urlsafekey=messages.StringField(1, required=True),
    player=messages.StringField(2, required=True),)
GAMEHISTORY_REQUEST = endpoints.ResourceContainer(
    game_urlsafekey=messages.StringField(1, required=True),)

diceValue = (1, 2, 3, 4, 5, 6)
TRIPLE = (10, 20, 30, 40, 50, 60, 70, 80, 90)
DOUBLE = (5, 15, 25, 35, 45, 55, 65, 75, 85)
NULL = (7, 14, 21, 28, 42, 49, 56, 63, 77, 84)


@endpoints.api(name='snailRacing', version='v1')
class SnailRacingApi(remote.Service):
    """
    Snail Race is a game with 2 players. The running distance is 100m.
    Each racer runs by rolling a dice. The number generated is used
    to change the player's position on the runway.
    The first player to arrive at position 100 has won.
    Each move computes a score for the player"""

    def _defaultPlayer(self):
        """ This function create a default player in order to have 2 players."""
        computer = Player(username='computer',
                          email="computer@snailRacing.com")
        computer.put()

    def _updateScore(self, game, player_position):
        """This function update a player's score during a game.
        Input: game in which the player is playing, the player and its score
        Output: The player's score is updated """
        player_score = Score.query(Score.game == game.key,
                                   Score.player == player_position.player).get()
        player_score.score += player_position.position
        player_score.put()

    @endpoints.method(PlayerForm, MessageForm, path="signin",
                      http_method="POST")
    def signIn(self, request):
        """ This function register a new user as player.
        Input: A unique username and email address"""
        username = request.username
        email = request.email
        if not utils.valid_username(username) or not utils.valid_email(email):
            raise endpoints.ConflictException(
                'Invalid Input')
        if Player.query(Player.username == request.username).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')

        Player(username=username, email=email).put()
        return MessageForm(message="Welcome Player %s. Enjoy racing!!! " % username)

    @endpoints.method(NEW_GAME_REQUEST, NewGameForm, path='new_game',
                      http_method='POST')
    def new_game(self, request):
        """This function creates a new game.
        Input: Two Usernames; Only The first is required,
        if the second is not given, the first player will be playing
        with an Automate (Computer)"""
        computer = Player.query(Player.username == "computer").get()
        if not computer:
            self._defaultPlayer()

        player = utils.get_by_username(request.player)

        if not request.opponent:
            opponent = Player.query(Player.username == "computer").get()
        else:
            opponent = utils.get_by_username(request.opponent)

        newgame = Game(player=player.key, opponent=opponent.key)
        newgame.put()
        # initialize players position
        Position(game=newgame.key, player=player.key, position=0).put()
        Position(game=newgame.key, player=opponent.key, position=0).put()

        # update score
        Score(game=newgame.key, player=player.key, score=0).put()
        Score(game=newgame.key, player=opponent.key, score=0).put()

        return NewGameForm(player=player.username, opponent=opponent.username,
                           urlsafekey=newgame.key.urlsafe())

    @endpoints.method(message_types.VoidMessage, MessageForm, path='roll_dice',
                      http_method="GET")
    def roll_dice(self, request):
        """ The function renders a random integer between 1 and 6.  """
        return MessageForm(message="{}".format(random.randint(1, 6)))

    @endpoints.method(FIRSTPLAYER_REQUEST, MessageForm, path='set_first_player',
                      http_method='PUT')
    def set_firstPlayer(self, request):
        """ This function sets the first player of a given game.
        Input: game safe url key, player username"""
        game = utils.get_by_urlsafe(request.game_urlsafekey, Game)
        player = utils.get_by_username(request.player)
        position = Position.query(
            Position.game == game.key, Position.player == player.key).get()
        position.isPlayingNow = True
        position.put()
        message = "Player %s token is set %s" % (player.username, "True")
        return MessageForm(message=message)

    @endpoints.method(MAKE_MOVE_REQUEST, MakeMoveForm, path='make_a_move',
                      http_method='PUT')
    def make_a_move(self, request):
        """ This function enables a player to move during the race.
        Input: game safe url key, player username, number render by the Dice"""

        if not request.dice in diceValue:
            raise endpoints.NotFoundException(
                'Invalid Dice Number')
        game = utils.get_by_urlsafe(request.game_urlsafekey, Game)
        if game.status != "start":
            raise endpoints.NotFoundException(
                'This game is either over or save!! Resume if saved')

        #player = utils.get_by_username(request.player)

        player = Position.query(Position.game == game.key,
                                Position.player == utils.get_by_username(request.player).key).get()
        if not player.isPlayingNow:
            raise endpoints.NotFoundException(
                'This player does not have token to play now')

        # Who is  Player and who is  Opponent ? Current user is always the
        # PLAYER
        if game.player == player.player:
            opponent = Position.query(
                Position.game == game.key, Position.player == game.opponent).get()
        elif game.opponent == player.player:
            opponent = Position.query(
                Position.game == game.key, Position.player == game.player).get()
        # opponent = Position.query(Position.game == game.key, Position.player == opp).get()

        # player and opponent are key objects in POSITION model

        # change position
        player.position = utils.move(player.position, request.dice)

        self._updateScore(game, player)

        # remove token
        player.isPlayingNow = False
        player.put()
        game_status = "Token False. Time for your opponent to play!"
        # Opponent is given token to play
        opponent.isPlayingNow = True

        msg = "Player %s played %s; Distance Moved:%s; Points earned: %s " % (
            request.player, request.dice, player.position, player.position)
        GameHistory(game=game.key, message=msg).put()

        # Opponent loose its position as first
        if player.position == opponent.position:
            opponent.position -= 1
        # GAME Over
        if player.position == 100:
            opponent.isPlayingNow = False
            game.gameOver(player)
            GameHistory(game=game.key, message="Player %s WON" %
                        request.player).put()
            game_status = "GAME OVER, YOU WON THE RACE!!!!!"

        opponent.put()
        return MakeMoveForm(player=request.player, dice=request.dice,
                            position=player.position,
                            score=Score.query(
                                Score.game == game.key, Score.player == player.player).get().score,
                            status=game_status)

    @endpoints.method(PlayerForm, ListHistoryForm, path="get_user_games",
                      http_method="GET")
    def get_user_games(self, request):
        """  This function returns all games of a given player."""
        player = utils.get_by_username(request.username)
        user_games = Score.query(Score.player == player.key)
        return ListHistoryForm(history=[games.toForm() for games in user_games])

    @endpoints.method(GameForm, MessageForm, path='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """This function delete a game.
        Input: Game safe url key"""
        game = utils.get_by_urlsafe(request.urlsafekey, Game)
        for hist in GameHistory.query(GameHistory.game == game.key):
        	hist.key.delete()
        game.key.delete()
        return MessageForm(message=" Game cancelled")

    @endpoints.method(GameForm, MessageForm, path='save_game',
                      http_method='PUT')
    def save_game(self, request):
        """ This function saves a game; The game can be played later.
        Input: Game safe url key"""
        game = utils.get_by_urlsafe(request.urlsafekey, Game)
        if game.status != "over":
            game.status = "save"
            game.put()
            return MessageForm(message=" The game has been save")
        else:
            raise endpoints.ConflictException(
                'Cannot save a Game over')

    @endpoints.method(GameForm, MessageForm, path='resume_game',
                      http_method='PUT')
    def resume_game(self, request):
        """ This function resumes a game that has been saved.
        Input: Game safe url key"""
        game = utils.get_by_urlsafe(request.urlsafekey, Game)
        if game.status == "save":
            game.status = "start"
            game.put()
            return MessageForm(message=" The game has been resume")
        else:
            raise endpoints.ConflictException(
                'Cannot resume a Game over')

    @endpoints.method(GAMEHISTORY_REQUEST, ListGameHistory, path='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """This function returns all moves in a game."""
        game = utils.get_by_urlsafe(request.game_urlsafekey, Game)
        return ListGameHistory(history=[game.toForm() for game in GameHistory.query(GameHistory.game == game.key)])

    @endpoints.method(message_types.VoidMessage, ListRanking,
                      path='get_user_ranking', http_method='GET')
    def get_user_rankings(self, request):
        """This function returns players and theirs ranks"""
        rankings = []
        players = Player.query().fetch()
        for player in players:
            performance = RankingForm()
            query = Score.query(Score.player == player.key)
            number_game = query.count()
            won = query.filter(Score.won == True).count()
            rankings.append(RankingForm(player=player.username,
                                        number_games=number_game, won=won))
        sorted(rankings, key=lambda rank: rank.won, reverse=True)
        return ListRanking(items=[rank for rank in rankings])

APPLICATION = endpoints.api_server([SnailRacingApi])
