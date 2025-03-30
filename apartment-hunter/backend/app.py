from flask import Flask
from models import db
from routes import routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///apartments.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.Model.metadata.reflect(db.engine)

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)