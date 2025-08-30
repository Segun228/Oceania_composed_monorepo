from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from api.models import Post, Category
from api.serializers import PostSerializer, CategorySerializer, CategoryReadSerializer
from backend.authentication import TelegramAuthentication # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http.response import HttpResponseBadRequest
from . import handlers
from rest_framework import status

class AddPostsFile(APIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "Файл не передан"}, status=400)
        result = handlers.add_posts_file(data = excel_file, request= request)
        if not result:
            return HttpResponseBadRequest()
        if result['errors']:
            return Response(
                {
                    "success": result['success'],
                    "errors": result['errors']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"success": result['success']},
                status=status.HTTP_200_OK
            )


class ReplacePostsFile(APIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "Файл не передан"}, status=400)
        result = handlers.replace_posts_file(data = excel_file, request= request)
        if not result:
            return HttpResponseBadRequest()
        if result['errors']:
            return Response(
                {
                    "success": result['success'],
                    "errors": result['errors']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"success": result['success']},
                status=status.HTTP_200_OK
            )


class GetPostsFile(APIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().values()
        categories = Category.objects.all().values()
        return handlers.get_xlsx_report(
            posts = posts,
            categories = categories
        )

