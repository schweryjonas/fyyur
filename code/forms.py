from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
from forms_choices import genres_options, state_options

# https://wtforms.readthedocs.io/en/2.3.x/validators/
def validate_genre_options(form, field):
    selected_genres = field.data
    for genre in selected_genres:
        genre_inside = False
        for possible_genre in genres_options:
            if genre == possible_genre[1]:
                genre_inside = True
                break
        if not genre_inside:
            raise ValidationError('The selected genre(s) is/are not valid!')


# def validate_date(form, field):
#     input_start_time = field.data
#     if input_start_time < datetime.today():
#         raise ValidationError('Start time has to be greater than today.')


def validate_phone(form, field):
    phone = field.data
    phone_parts = phone.split("-")
    if not phone_len_valid(phone_parts) or not phone_is_digit(phone_parts):
        raise ValidationError('Invalid phone number!')


def phone_len_valid(phone_parts):
    return len(phone_parts[0]) == 3 and len(phone_parts[1]) == 3 and len(phone_parts[2]) == 4 and len(phone_parts) == 3


def phone_is_digit(phone_parts):
    return phone_parts[0].isdigit() and phone_parts[1].isdigit() and phone_parts[2].isdigit()

# https://flask-wtf.readthedocs.io/en/stable/quickstart.html#creating-forms
class ShowForm(Form):

    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        [DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_options
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres',
        [DataRequired(), validate_genre_options],
        choices=genres_options
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
        'state', validators=[DataRequired()], choices=state_options
    )
    phone = StringField(
        # TODO implement validation logic for phone
        'phone', validators=[DataRequired(), validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), validate_genre_options], choices=genres_options
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
