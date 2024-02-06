#This is used by login manager
#And I wanted to keep classes different from my main prject
from flask_login import UserMixin,current_user
from functools import wraps
from flask import *

class User(UserMixin):
    def __init__( self, user_id):
        self.id = user_id

