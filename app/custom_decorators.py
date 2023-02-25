from functools import wraps
from flask import flash, abort, redirect, url_for
from flask_login import current_user


def user1_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if current_user.id > 1:
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_user.is_admin():
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function