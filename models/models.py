from app import db, login, app


@login.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


drug_class = db.Table("drug_class",
                      db.Column("id_drug", db.Integer, db.ForeignKey("drugs.id")),
                      db.Column("id_class", db.Integer, db.ForeignKey("classdrugs.id")),
                      )


class Years(db.Model):
    __tablenmae__ = "years"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)

    drugs = db.relationship("Drugs", backref="years")

    def __repr__(self):
        return f"Years: {self.year}"


class ClassDrugs(db.Model):
    __tablename__ = "classdrugs"

    id = db.Column(db.Integer, primary_key=True)
    drugs_class = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"{self.drugs_class}"


class Drugs(db.Model):
    __tablename__ = "drugs"

    id = db.Column(db.Integer, primary_key=True)
    colloquial_name = db.Column(db.String(32), nullable=False)
    sicenc_name = db.Column(db.String(32), nullable=False)
    opening_year = db.Column(db.Integer, db.ForeignKey("years.year"))
    formula = db.Column(db.String(64), unique=True, nullable=False)
    discoverer = db.Column(db.String(120), nullable=True)
    user = db.Column(db.String(32), db.ForeignKey("users.username"), nullable=False)

    drugs = db.relationship("ClassDrugs", secondary=drug_class, backref="drugs")

    def __repr__(self):
        return f"{self.colloquial_name}, {self.sicenc_name}, {self.formula}, {self.discoverer}"


### User Model
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    hash_password = db.Column(db.String(120), nullable=False)

    drugs = db.relationship(Drugs, backref="users")

    def get_reset_token(self, expires_sec=1800):
        serializer = Serializer(app.config["SECRET_KEY"], expires_sec)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    def verify_reset_token(token):
        serializer = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = serializer.load(token)["user_id"]
        except:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return f"User: {self.id}, {self.username}, {self.email}"
