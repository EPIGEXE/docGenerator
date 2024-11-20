from rest_framework import serializers
from .models import Document

class DocumentGenerationSerializer(serializers.Serializer):  # ModelSerializer에서 Serializer로 변경
    content = serializers.CharField(
        help_text="명세서 내용",
        style={'base_template': 'textarea.html'}  # 텍스트 영역으로 표시
    )
    output_types = serializers.MultipleChoiceField(
        choices=[
            ('excel', 'Excel'),
            ('word', 'Word'),
            ('pdf', 'PDF')
        ],
        help_text="생성할 문서 타입 (여러 개 선택 가능)"
    )
    template_file = serializers.FileField(
        required=False,
        help_text="Excel 템플릿 파일 (선택사항)"
    )

    class Meta:
        ref_name = 'DocumentGeneration'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'doc_type', 'status', 'file', 'created_at', 'error_message']
        ref_name = 'Document'