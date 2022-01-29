from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {"text": "Текст поста", "group": "Сообщество"}

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Наличие поста обязательно!")
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Текст комментария"}
