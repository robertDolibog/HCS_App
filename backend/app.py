import os
from flask import Flask
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Ensure models are imported
import models.file  # noqa
import models.file_locations  # noqa

# Register Blueprints (lazy import)
def register_blueprints(app):
    from controllers.sync_controller import sync_bp
    app.register_blueprint(sync_bp)

register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)