from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]
        labels = {
            "group": "Группа",
            "text": "Пост"
        }


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            "text": "Комментарий",
        }
