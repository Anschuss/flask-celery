from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, Flags, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from models import Users, Drugs


class RegForm(FlaskForm):
    email = StringField("email",
                        validators=[DataRequired(), Email()])
    username = StringField("username", validators=[DataRequired(),
                                                   Length(min=4, max=20)])
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField("confirm_password",
                                     validators=[EqualTo("password"), DataRequired()])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = Users.query.filter(Users.username == username.data).first()
        if user:
            raise ValidationError("That name is taken.Pleas Choose different one!")

    def validate_email(self, email):
        user_email = Users.query.filter(Users.email == email.data).first()
        if user_email:
            raise ValidationError("That emil is taken.Pleas Choose different one!")


class LoginForm(FlaskForm):
    email = StringField("email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("password",
                             validators=[DataRequired()])
    remember = BooleanField("Remember me")

    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField("username",
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("email",
                        validators=[DataRequired(), Email()])

    submit = SubmitField("Update")

    def vaslidate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter(Users.username == username.data).first()
            if user:
                raise ValidationError("That name is taken.Pleas Choose different one!")

    def validate_email(self, email):
        if email.data != current_user.email:
            user_email = Users.query.filter(Users.email == email.data).first()
            if user_email:
                raise ValidationError("That email is taken.Pleas Choose different one!")


class DrugsForm(FlaskForm):
    colloquial_name = StringField("name_1", validators=[DataRequired()])
    sicenc_name = StringField("name_2", validators=[DataRequired()])
    opening_year = SelectField("year", choices=[], validators=[DataRequired()])
    formula = StringField("formula", validators=[DataRequired()])
    discoverer = StringField("discoverer", validators=[DataRequired()])
    class_drugs = SelectField("class_drugs", choices=[], validators=[DataRequired()])

    submit = SubmitField("Submit")

    def validate_name(self, colloquial_name, sicenc_name):
        drug = Drugs.query.filter(
            Drugs.colloquial_name == colloquial_name.data and Drugs.sicenc_name == sicenc_name.data).first()
        if drug:
            raise ValidationError("That drug is taken.Pleas Choose different one!")

    def validate_formula(self, formula):
        drug = Drugs.query.filter(Drugs.formula == formula.data).first()
        if drug:
            raise ValidationError("That formula is taken.Pleas Choose different one!")


class RequestEmailForm(FlaskForm):
    email = StringField("email",
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Request")

    def validate_email(self, email):
        user = Users.query.filter(Users.email == email.data).first()
        if user:
            raise ValidationError("There is no account with that email. You must register first")


class RequestPasswordForm(FlaskForm):
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField("confirm_password",
                                     validators=[EqualTo("password"), DataRequired()])

    submit = SubmitField("Request")
