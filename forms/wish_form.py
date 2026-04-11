from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed


class WishForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": "Сумочка"})
    bio = StringField('Описание', validators=[DataRequired()])
    url = StringField('Ссылка')
    img = FileField('Изображение', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'])
    ])
    submit = SubmitField('Добавить желание')
