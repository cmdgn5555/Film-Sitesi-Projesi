from django import forms
from django_recaptcha.fields import ReCaptchaField


class LoginForm(forms.Form):
    username = forms.CharField( 
        max_length=100,
        widget = forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Kullanıcı adınızı giriniz...",
            "style": "font-family: cursive;"
        })
        )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Şifrenizi giriniz...",
            "style": "font-family: cursive;"
        })
        )
    
    # Captcha'yı dinamik olarak eklemek için
    def __init__(self, *args, **kwargs):
        show_captcha = kwargs.pop('show_captcha', False)  # Captcha'yı göstermek için bir kontrol ekliyoruz
        super().__init__(*args, **kwargs)
        if show_captcha:
            self.fields['captcha'] = ReCaptchaField()  # Yalnızca show_captcha True olduğunda Captcha'yı ekliyoruz