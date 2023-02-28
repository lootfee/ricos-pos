from flask_wtf import FlaskForm
from app import app, photos
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, \
    FloatField, HiddenField, DateField, DateTimeField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, InputRequired
from app.models import User
from flask_wtf.file import FileField, FileRequired, FileAllowed


def validate_select(form, field):
    if field.data == 0:
        raise ValidationError("Please select from choice list")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit_login = SubmitField('Sign In')


class AddItemForm(FlaskForm):
    item_name = StringField('Item name', validators=[InputRequired()])
    description = StringField('Description')
    barcode = StringField('Barcode', validators=[InputRequired()])
    # purchase_price = FloatField('Purchase price', validators=[DataRequired()])
    retail_price = FloatField('Retail price', validators=[InputRequired()])
    submit = SubmitField('Save')


class EditItemForm(FlaskForm):
    item_name = StringField('Item name', validators=[InputRequired()])
    description = StringField('Description')
    barcode = StringField('Barcode', validators=[InputRequired()])
    submit = SubmitField('Save')


class EditRetailPriceForm(FlaskForm):
    retail_price = FloatField('New Retail Price', validators=[InputRequired()])
    submit = SubmitField('Save')


class AddInventoryForm(FlaskForm):
    item = SelectField('Item', coerce=int, validators=[InputRequired(), validate_select])
    quantity = IntegerField('Quantity', validators=[InputRequired()])
    purchase_price = FloatField('Purchase total price', validators=[InputRequired()])
    date_received = DateField('Date Received', validators=[InputRequired()])
    submit = SubmitField('Submit')


class EditSaleDateForm(FlaskForm):
    date = DateTimeField('Transaction date', validators=[DataRequired()], render_kw={"type": "datetime-local"},
                                           format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Save')


class EditSaleItemForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[InputRequired()])
    retail_price = FloatField('Retail price', validators=[DataRequired()], render_kw={'readonly': 'true'})
    total_cost = FloatField('Total cost', validators=[DataRequired()], render_kw={'readonly': 'true'})
    submit = SubmitField('Save')


# class RegistrationForm(FlaskForm):
#     username = StringField('Full name', validators=[DataRequired(), Length(min=4, max=15)])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     contact_info = StringField('Contact number', validators=[DataRequired()], default="+639")
#     address = StringField('Address', validators=[DataRequired()])
#     birthday = DateField('Birthday', validators=[DataRequired()], format='%Y-%m-%d')
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')
#
#     '''def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different username.')'''
#
#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different email address.')
#
#
# class EditProfileForm(FlaskForm):
#     username = StringField('Full name', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     submit = SubmitField('Submit')
#
#     def __init__(self, original_email, *args, **kwargs):
#         super(EditProfileForm, self).__init__(*args, **kwargs)
#         # self.original_username = original_username
#         self.original_email = original_email
#
#     '''def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username=self.username.data).first()
#             if user is not None:
#                 raise ValidationError('Please use a different username.')'''
#
#     def validate_email(self, email):
#         if email.data != self.original_email:
#             user = User.query.filter_by(email=self.email.data).first()
#             if user is not None:
#                 raise ValidationError('Email is already registered!')
#
#
# class ResetPasswordRequestForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     submit = SubmitField('Request Password Reset')
#
#
# class ResetPasswordForm(FlaskForm):
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Request Password Reset')
