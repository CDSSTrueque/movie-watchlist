from email import message
from flask_wtf import FlaskForm , RecaptchaField
from wtforms import (
    IntegerField, 
    StringField, 
    SubmitField, 
    TextAreaField, 
    URLField,
    PasswordField
)
from wtforms.validators import (
    InputRequired, 
    NumberRange, 
    Email, 
    Length,
    EqualTo,
)


# validators=[InputRequired() ] -> no acepta campos en blanco

class MovieForms(FlaskForm):
    
    title = StringField("Title" , validators = [ InputRequired() ])
    director = StringField("Director" , validators = [ InputRequired() ])
    
    year = IntegerField("Year" , 
        validators=[
            InputRequired(), 
            NumberRange(
                min=1878, 
                message="Please enter a year in the formart YYYY.")
            ]  #max = 2022 example
    )
    
    submit = SubmitField("Add Movie")
    

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
    
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []
    
class ExtendedMovieForm(MovieForms):
    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description = TextAreaField("Description")
    video_link = URLField("Video link")

    submit = SubmitField("Submit")



class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired() , Email()])
    password = PasswordField(
        "Password", 
        validators=[ 
            InputRequired(),
            Length(
                min=3, max=20,
                message = "Your password must be between 3 and 20 characters long."
            ),
        ]
    )
    
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message= "This password did not match the one in the password field."
            )
        ]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Register")





class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired() , Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Login")
    