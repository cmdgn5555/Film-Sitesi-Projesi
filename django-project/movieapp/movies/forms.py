from django import forms
from .models import UserProfile, Rating, Yorum, YorumSikayet


class UserProfileForm(forms.ModelForm):
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'biography', 'email', 'city', 'country', 'birthday', 'occupation', 'education']







class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating"]
        
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10})
        }







class YorumForm(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ['yorum_text', "parent"]
        
        widgets = {
            'yorum_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Lütfen yorumunuzu yazınız...'}),
            'parent': forms.HiddenInput()
        }
        
        labels = {
            'yorum_text': 'Yorum',
        }







class SikayetFormu(forms.ModelForm):
    class Meta:
        model = YorumSikayet
        fields = ["neden"]


        