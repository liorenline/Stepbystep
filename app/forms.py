from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.utils import validate_password_strength


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Register")

    def validate_password(self, field):
        errors = validate_password_strength(field.data)
        if errors:
            raise ValidationError(" ".join(errors))


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class VerifyCodeForm(FlaskForm):
    code = StringField("6-digit code", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Code")


class ResetPasswordForm(FlaskForm):
    code = StringField("Verification Code", validators=[DataRequired(), Length(min=6, max=6)])
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Reset Password")

    def validate_password(self, field):
        errors = validate_password_strength(field.data)
        if errors:
            raise ValidationError(" ".join(errors))


class ChangePasswordForm(FlaskForm):
    code = StringField("Verification Code", validators=[DataRequired(), Length(min=6, max=6)])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")]
    )
    submit = SubmitField("Change Password")

    def validate_new_password(self, field):
        errors = validate_password_strength(field.data)
        if errors:
            raise ValidationError(" ".join(errors))


class ChangeEmailForm(FlaskForm):
    new_email = StringField("New Email", validators=[DataRequired(), Email()])
    submit_request = SubmitField("Send Verification Code")

    code = StringField("Verification Code", validators=[Length(min=0, max=6)])
    submit_confirm = SubmitField("Confirm New Email")


class DeckForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Length(max=500)])
    submit = SubmitField("Save")


class CardForm(FlaskForm):
    question = TextAreaField("Question", validators=[DataRequired()])
    answer = TextAreaField("Answer", validators=[DataRequired()])
    submit = SubmitField("Save")
