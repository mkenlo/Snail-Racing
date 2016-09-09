import re
from google.appengine.ext import ndb
import endpoints
from models import Player

TRIPLE = (10, 20, 30, 40, 50, 60, 70, 80, 90)
DOUBLE = (5, 15, 25, 35, 45, 55, 65, 75, 85)
NULL = (7, 14, 21, 28, 42, 49, 56, 63, 77, 84)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def move(position, dice):
    print "move player"
    previous = position
    if position in TRIPLE:
        position += dice * 3
    elif position in DOUBLE:
        position += dice * 2
    elif position in NULL:
        if dice == 6:
            position += dice
    else:
        position += dice
    if position > 100:
        position = previous
    return position


def valid_username(username):
    return username and USER_RE.match(username)


def valid_password(password):
    return password and PASS_RE.match(password)


def valid_email(email):
    return not email or EMAIL_RE.match(email)


def get_by_username(username):
    player = Player.query(Player.username == username).get()
    if not player:
        raise endpoints.ConflictException(
            'No Player %s exists!' % username)
    return player
