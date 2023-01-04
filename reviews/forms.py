from django import forms
from .models import Review

#Customer Review Form    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['uname','email', 'review', 'rating']
