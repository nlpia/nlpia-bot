from django import forms


class SignupForm(forms.Form):
    name = forms.CharField(label='Enter your name', max_length=127)
    email = forms.EmailField(label='Enter your email', max_length=255)


class ChatForm(forms.Form):
    message = forms.TextField(label='Hi!')
    at_user = forms.CharField(label='@user', max_length=255)
