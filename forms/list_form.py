from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ListForm(FlaskForm):
    feast = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": "День рождения"})
    date = DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"placeholder": "2000.01.01"})
    time = TimeField('Время', validators=[DataRequired()], format='%H:%M', render_kw={"placeholder": "13:30"})
    notification = BooleanField('Уведомление')
    submit = SubmitField('Добавить вишлист')
