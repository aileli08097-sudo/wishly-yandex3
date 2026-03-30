from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class WishForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": "Сумочка"})
    bio = StringField('Описание', validators=[DataRequired()])
    url = StringField('Ссылка')
    submit = SubmitField('Добавить желание')
