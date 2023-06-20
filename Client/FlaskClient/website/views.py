from flask import Blueprint, jsonify, request
from . import db
from .models import Owner,Message,Contact
from datetime import datetime
import json
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return 'hello there'