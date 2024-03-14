from flask import (
    Flask,
    session,
    g,
)
from .static import static_page
from .api import api
from . import db
import os


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="dev",
            DATABASE=os.path.join(app.instance_path, "plaid-investments.sqlite"),
        )
    else:
        app.config.from_mapping(test_config)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")

        if user_id is None:
            g.user = None
        else:
            g.user = (
                db.get_db()
                .execute(
                    "SELECT * FROM user WHERE id = ?",
                    (user_id,),
                )
                .fetchone()
            )

    app.register_blueprint(static_page)
    app.register_blueprint(api)

    db.init_app(app)

    return app
