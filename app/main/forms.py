from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length

class NameForm(FlaskForm):
    name = StringField('input you name: ',validators=[DataRequired()])
    submit = SubmitField('submit')


class EditProfile(FlaskForm):
    name = StringField('input you name: ',validators=[Length(0,20)])
    location = StringField('Location: ', validators=[DataRequired(),Length(0,64)])
    about_me = TextAreaField('About me: ')
    submit = SubmitField('Submit')