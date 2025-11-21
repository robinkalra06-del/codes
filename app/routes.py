from flask import Blueprint, render_template, session, redirect, url_for

dashboard = Blueprint('dashboard', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper


@dashboard.route('/dashboard')
@login_required
def overview():
    return render_template('dashboard/overview.html')


@dashboard.route('/dashboard/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html')


@dashboard.route('/dashboard/subscribers')
@login_required
def subscribers():
    return render_template('dashboard/subscribers.html')


@dashboard.route('/dashboard/send')
@login_required
def send():
    return render_template('dashboard/send.html')
