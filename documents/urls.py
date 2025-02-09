from django.urls import path
from .views import DocumentUploadView, QuestionAnswerView, index

urlpatterns = [
    path('', index, name='index'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('qa/', QuestionAnswerView.as_view(), name='question-answer'),
]
