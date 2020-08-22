from django.contrib import admin

# Register your models here.
from .models import Question, Choice


class ChoiceInline(admin.StackedInline):
    model = Choice


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question_text','created','is_active','anonymously')
    list_display_links = ('title', )
    inlines = [ChoiceInline]

