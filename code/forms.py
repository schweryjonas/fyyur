from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, RadioField
from wtforms.validators import DataRequired, AnyOf, URL
from forms_choices import genres_options, state_options

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators = [DataRequired()]
    )
    city = StringField(
        'city', validators = [DataRequired()]
    )
    state = SelectField(
        'state', validators = [DataRequired()],
        choices = state_options
    )
    address = StringField(
        'address', validators = [DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices = genres_options
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_description = StringField(
        'seeking_description', validators=[]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices = state_options
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices = genres_options
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_description = StringField(
        'seeking_description', validators=[]
    )

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
