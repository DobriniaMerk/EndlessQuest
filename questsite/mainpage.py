from questsite import librarian
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

bp = Blueprint('mainpage', __name__)


@bp.route('/')
def mainpage():
    return redirect(url_for('paragraph.show', id=1))
