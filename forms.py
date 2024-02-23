from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, EqualTo, Email, Length
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField, BooleanField, SelectField


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    verify_email = BooleanField('Verify Email')
    submit = SubmitField("Register Me 😎")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login 🕵️‍♂️")


class CoffeeForm(FlaskForm):
    choices = [('1', 'No'), ('2', 'Little Much'), ('3', 'More'), ('4', 'According to yourself')]
    choices2 = [
        ('1', 'No'),
        ('2', 'Choco flavor'),
        ('3', 'Vanilla flavor'),
        ('4', 'Strawberry flavor'),
        ('5', 'Caramel flavor'),
        ('6', 'Hazelnut flavor'),
    ]
    choices3 = [('1', 'None'), ('2', 'Light'), ('3', 'Regular'), ('4', 'Extra')]
    choices4 = [('1', 'Small'), ('2', 'Medium'), ('3', 'Large')]

    name = StringField("Name of your coffee", validators=[DataRequired()])
    milk = BooleanField("Milk")
    water = BooleanField("Water")
    sugar = SelectField("Sugar", choices=choices)
    chocolate = SelectField("Chocolate", choices=choices)
    icecream = SelectField("Ice-Cream", choices=choices2)
    flavor = SelectField("Flavor", choices=choices2)
    whipped_cream = SelectField("Whipped Cream", choices=choices3)
    glass = SelectField("Quantity", choices=choices4)
    howmany = IntegerField("How many coffee? (1-10)", validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField("Create this one")


class ForgotPasswordForm(FlaskForm):
    email = EmailField("Enter your Registered Email", validators=[DataRequired()])
    submit = SubmitField("Send")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")