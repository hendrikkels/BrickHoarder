from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class SearchSetForm(FlaskForm):
    # no = StringField('Set Number', validators=[InputRequired()])
    no = StringField('Set Number', validators=[InputRequired()])
