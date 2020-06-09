#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()

def connect(app):
    app.config.from_object('config')
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    return db


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(300))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    artists = db.relationship('Show', back_populates='venue')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(300))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    venues = db.relationship('Show', back_populates='artist')


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# using the association object pattern, see: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_date = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', back_populates='artists')
    artist = db.relationship('Artist', back_populates='venues')