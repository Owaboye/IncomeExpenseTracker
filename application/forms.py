from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Email, Length, Regexp, EqualTo

class IncomeExpForm(FlaskForm):
    amount = DecimalField(
        'Amount',
        places=2, 
        validators=[
        DataRequired(),
        NumberRange(min=1, message="Amount must be greater than 0.")
                ])
    type = SelectField('Cashflow Type', choices=[('Income', 'Income'), ('Expenses', 'Expenses')])
    expense_category = SelectField(
        'Expense Category',
        validate_choice=True, 
        validators=[DataRequired()],
        choices=[
                ('Fuel', 'Fuel'),
                ('Rent', 'Rent'),
                ('Air time', 'Air time'),
                ('Data', 'Data'),
                ('Gas', 'Gas'),
                ('Transportation', 'Transportation'),
                ('Health', 'Health'),
                ('Kingdom Investment', 'Kingdom Investment'),
                ('Investment', 'Investment'),
                ('Savings', 'Savings'),
                ('Utility-Electricity', 'Utility-Electricity'),
                ('Utility-Water', 'Utility-Water'),
                ('Entertainmaet', 'Entertainmaet'),
                ('Food and Groceries', 'Food and Groceries'),
                ('Refund', 'Refund'),
                ('Miscellanous', 'Miscellanous')
                ]
              )
    description = StringField('Description')
    income_source = SelectField(
        'Income Source', 
        validate_choice=True, 
        validators=[DataRequired()],
        choices=[
                ('Excel', 'Excel'),
                ('Coding', 'Coding'),
                ('Web Development', 'Web Development'),
                ('Data Analysis', 'Data Analysis'),
                ('Earned Income', 'Earned Income'),
                ('Dividend/Interest', 'Dividend/Interest'),
                ('Capital Gains', 'Capital Gains'),
                ('Others', 'Others')
              ]
              )

# Sign up Ezekiel!@#$1
class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First name is required.")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last name is required.")])
    email = StringField('Email', validators=[
                DataRequired(message='Email is required'),
                Email(message='Enter a valid email address.')
                ])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, message="Password must be at least 8 characters."),
            Regexp(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*])(?=.*\d).+$',
                message="Password must contain at least one uppercase letter, one special character and one number."
            )
        ]
    )

# Sign up
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                DataRequired(message='Email is required')
                ])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required.")]
    )

# ResetPasswordForm
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, message="Password must be at least 8 characters."),
            Regexp(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*])(?=.*\d).+$',
                message="Password must contain at least one uppercase letter, one special character and one number."
            )
        ]
    )
    confirm_password = PasswordField('Confirm Password', 
                        validators=[DataRequired(), 
                        EqualTo('password', message='Passwords must match.')])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
                DataRequired(message='Email is required')
                ])

class IncomeTypeForm(FlaskForm):
    name = StringField(
        'Income Title',
        validators=[DataRequired()]
    )

class ExpenseTypeForm(FlaskForm):
    name = StringField(
        'Income Title',
        validators=[DataRequired()]
    )