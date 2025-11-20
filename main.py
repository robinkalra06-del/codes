import os
import secrets
from pathlib import Path
from flask import (
    Flask, render_template, redirect, url_for, request, flash,
    jsonify, abort, current_app, send_from_directory
)
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, User, Site, Subscription, Notification
from config import Config
from notifications import send_notification_to_subscription

# Allowed upload types
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif", "svg", "ico"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def detect_device_group(user_agent: str):
    ua = user_agent.lower() if user_agent else ""
    if "android" in ua:
        return "android"
    if "iphone" in ua or "ipad" in ua or "ipod" in ua:
        return "ios"
    if "mobile" in ua and ("android" not in ua and "iphone" not in ua):
        return "phone"
    if "safari" in ua and "chrome" not in ua:
        return "safari"
    if "mobile" in ua:
        return "phone"
    return "desktop"

def detect_browser(user_agent: str):
    ua = user_agent.lower() if user_agent else ""
    if "chrome" in ua and "edg" not in ua:
        return "chrome"
    if "firefox" in ua:
        return "firefox"
    if "safari" in ua and "chrome" not in ua:
        return "safari"
    if "edg" in ua or "edge" in ua:
        return "edge"
    return "other"

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)

    # Uploads configuration
    app.config.setdefault("UPLOAD_FOLDER", os.path.join(app.root_path, "static", "uploads"))
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # CORS - allow API calls from any origin (adjust origins list for security)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    migrate = Migrate(app, db)

    login = LoginManager(app)
    login.login_view = 'login'

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------------------------
    # LOGIN / LOGOUT
    # -------------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            # NOTE: change to hashed check in production
            if user and user.password_hash == password:
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # -------------------------
    # DASHBOARD
    # -------------------------
    @app.route('/')
    @login_required
    def dashboard():
        sites = Site.query.filter_by(owner_id=current_user.id).all()
        return render_template('dashboard.html', sites=sites)

    # -------------------------
    # CREATE SITE
    # -------------------------
    @app.route('/sites/create', methods=['POST'])
    @login_required
    def create_site():
        name = request.form['name']
        origin = request.form['origin']
        api_key = secrets.token_urlsafe(32)
        site = Site(owner_id=current_user.id, name=name, origin=origin, api_key=api_key)
        db.session.add(site)
        db.session.commit()
        flash('Site created. Use the integration snippet to subscribe visitors.', 'success')
        return redirect(url_for('dashboard'))

    # -------------------------
    # SITE DETAIL & INTEGRATION
    # -------------------------
    @app.route('/sites/<int:site_id>')
    @login_required
    def site_detail(site_id):
        site = Site.query.get_or_404(site_id)
        if site.owner_id != current_user.id:
            abort(403)
        subscriptions = Subscription.query.filter_by(site_id=site.id).all()
        # group counts
        counts = {}
        groups = ["all", "desktop", "safari", "android", "ios", "phone"]
        for g in groups:
            if g == "all":
                counts[g] = Subscription.query.filter_by(site_id=site.id).count()
            else:
                counts[g] = Subscription.query.filter_by(site_id=site.id, device_type=g).count()
        return render_template(
            'site_detail.html',
            site=site,
            subscriptions=subscriptions,
            vapid_public=app.config.get('VAPID_PUBLIC_KEY'),
            group_counts=counts
        )

    # -------------------------
    # API: SUBSCRIBE (public)
    # -------------------------
    @app.route('/api/subscribe', methods=['POST'])
    def api_subscribe():
        data = request.get_json() or {}
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'missing api_key'}), 400
        site = Site.query.filter_by(api_key=api_key).first()
        if not site:
            return jsonify({'error': 'invalid api_key'}), 403
        sub = data.get('subscription')
        if not sub:
            return jsonify({'error': 'missing subscription'}), 400

        ua = request.headers.get('User-Agent', '')
        device_type = detect_device_group(ua)
        browser = detect_browser(ua)

        endpoint = sub.get('endpoint')
        keys = sub.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        existing = Subscription.query.filter_by(site_id=site.id, endpoint=endpoint).first()
        if existing:
            existing.device_type = device_type
            existing.browser = browser
            db.session.commit()
            return jsonify({'ok': True})

        s = Subscription(
            site_id=site.id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            browser=browser,
            device_type=device_type
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({'ok': True})

    # -------------------------
    # UPLOAD FILE (admin AJAX)
    # -------------------------
    @app.route('/sites/<int:site_id>/upload', methods=['POST'])
    @login_required
    def upload_file(site_id):
        site = Site.query.get_or_404(site_id)
        if site.owner_id != current_user.id:
            abort(403)
        if 'file' not in request.files:
            return jsonify({'error': 'no file'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'empty filename'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name = f"{secrets.token_hex(8)}_{filename}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], name)
            file.save(save_path)
            public_path = url_for('static', filename=f"uploads/{name}", _external=True)
            return jsonify({'ok': True, 'url': public_path})
        return jsonify({'error': 'invalid file type'}), 400

    # -------------------------
    # SEND NOTIFICATION (form + handler)
    # -------------------------
    @app.route('/sites/<int:site_id>/send', methods=['GET', 'POST'])
    @login_required
    def send_notification(site_id):
        site = Site.query.get_or_404(site_id)
        if site.owner_id != current_user.id:
            abort(403)

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')
            url_to_open = request.form.get('url')
            target_group = request.form.get('target_group', 'all')

            icon = request.form.get('icon') or None
            image = request.form.get('image') or None

            notification = Notification(
                site_id=site.id,
                title=title,
                body=body,
                url=url_to_open,
                icon=icon,
                image=image,
                target_group=target_group
            )
            db.session.add(notification)
            db.session.commit()

            if target_group == 'all':
                subs = Subscription.query.filter_by(site_id=site.id).all()
            else:
                subs = Subscription.query.filter_by(site_id=site.id, device_type=target_group).all()

            payload = {
                'title': title,
                'body': body,
                'url': url_to_open,
                'icon': icon,
                'image': image
            }

            for sub in subs:
                try:
                    send_notification_to_subscription(sub, payload, app)
                except Exception as e:
                    app.logger.exception("Push send failed: %s", e)

            flash(f"Sent to {len(subs)} subscribers (queued/sent).", "success")
            return redirect(url_for('site_detail', site_id=site.id))

        groups = ['all', 'desktop', 'safari', 'android', 'ios', 'phone']
        return render_template('send_notification.html', site=site, groups=groups)

    # -------------------------
    # Serve service worker file (for direct registration on the same origin)
    # -------------------------
    @app.route('/sw.js')
    def sw_js():
        return app.send_static_file('sw.js')

    # -------------------------
    # Download sw.js (owner-only)
    # -------------------------
    @app.route('/download/sw/<int:site_id>')
    @login_required
    def download_sw(site_id):
        site = Site.query.get_or_404(site_id)
        if site.owner_id != current_user.id:
            abort(403)
        return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js', as_attachment=True)

    # -------------------------
    # AUTO CREATE DB ON STARTUP
    # -------------------------
    with app.app_context():
        db.create_all()

    return app

# -------------------------
# RUN (local + Render friendly)
# -------------------------
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
