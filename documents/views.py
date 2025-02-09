from django.shortcuts import render

# Create your views here.

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny


from .models import Document
from .serializers import DocumentSerializer

import pdfplumber, pytesseract
import docx  # Library to handle Word files (.docx)
import pandas as pd  # Library to handle Excel files (.xlsx, .csv)
from transformers import pipeline



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Load NLP models globally
summarizer = pipeline("summarization")
qa_model = pipeline("question-answering")


@method_decorator(csrf_exempt, name='dispatch')
class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]  # Allow unauthenticated requests


    def post(self, request, *args, **kwargs):
        """Handles document upload and returns the extracted summary"""
        file_serializer = DocumentSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            document = file_serializer.instance
            text = extract_text(document.file.path)
            summary = summarize_text(text)

            # Store extracted text and summary in the database
            document.text = text
            document.summary = summary
            document.save()

            return Response({"document_id": document.id, "summary": summary})
        return Response(file_serializer.errors, status=400)

class QuestionAnswerView(APIView):
    def post(self, request, *args, **kwargs):
        document_id = request.data.get("document_id")
        question = request.data.get("question")

        if not document_id or not question:
            return Response({"error": "Both document_id and question are required"}, status=400)

        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        answer = answer_question(document.text, question)
        return Response({"answer": answer})

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif file_path.endswith((".png", ".jpg", ".jpeg")):
        return pytesseract.image_to_string(file_path)
    else:
        with open(file_path, 'r', encoding="utf-8") as f:
            return f.read()

def summarize_text(text):
    return summarizer(text[:1024])[0]['summary_text']

def answer_question(text, question):
    return qa_model(question=question, context=text)['answer']

def index(request):
    return render(request, 'index.html')

