from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired


class CodeRegistrForm(FlaskForm):
    code = IntegerField('Введите код подтверждения', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
