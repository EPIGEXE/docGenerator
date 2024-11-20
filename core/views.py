from django.shortcuts import render
from rest_framework.views import APIView  # 이 줄 추가
from rest_framework import status  # 이 줄 추가
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentGenerationSerializer
from .services import DocumentService
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from django.core.files.storage import default_storage
from asgiref.sync import async_to_sync

# Create your views here.
class GenerateDocumentView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_description="명세서 내용과 템플릿 파일을 기반으로 문서를 생성합니다.",
        request_body=DocumentGenerationSerializer,
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'document_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = DocumentGenerationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            content = serializer.validated_data['content']
            output_types = serializer.validated_data['output_types']
            template_file = serializer.validated_data.get('template_file')

            # 템플릿 파일 처리
            template_path = None
            if template_file:
                file_name = default_storage.save(
                    f'templates/{template_file.name}',
                    template_file
                )
                template_path = default_storage.path(file_name)

            # 비동기 문서 생성 서비스 호출을 동기적으로 변환
            document_service = DocumentService()
            result = async_to_sync(document_service.generate_documents)(
                content,
                output_types,
                template_path
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentStatusView(APIView):
    def get(self, request, doc_id):
        """문서 상태 확인"""
        document = get_object_or_404(Document, id=doc_id)
        return Response({
            'status': document.status,
            'file': document.file.url if document.file else None,
            'error': document.error_message
        })