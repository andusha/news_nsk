from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
from api.config import photos

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default = False)
    submit = SubmitField("Войти")

class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")

class addPostForm(FlaskForm):
    title = StringField("Заголовок статьи: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    photo = FileField("Загрузите фото:", validators=[FileAllowed(photos, 'Только изображения!')])
    text = TextAreaField("Статья:",validators=[DataRequired(), Length(min=10, max=10000, message="Минимум 10 символов, максимум 10000")])
    submit = SubmitField('Опубликовать')
    

