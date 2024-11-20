from asgiref.sync import sync_to_async
from .ai_service import AIService
from .ppt_service import PPTService
from .excel_service import ExcelService
from ..models import Document
from pathlib import Path
from django.core.files import File

class DocumentService:
    def __init__(self):
        self.ai_service = AIService()
        self.ppt_service = PPTService()
        self.excel_service = ExcelService()

    async def generate_documents(self, spec_content: str, output_types: list, template_path: str = None):
        try:
            results = []
            for doc_type in output_types:
                # Document 생성을 비동기로 처리
                document = await sync_to_async(Document.objects.create)(
                    spec_content=spec_content,
                    doc_type=doc_type,
                    status='processing'
                )
                
                try:
                    # 문서 타입별 생성 로직
                    if doc_type == 'excel':
                        # 템플릿 분석 및 AI 컨텐츠 생성
                        template_info = None
                        if template_path:
                            template_info = await self.excel_service.analyze_and_generate(template_path, spec_content)
                        
                        # AI로 명세서 분석
                        analyzed_content = await self.ai_service.analyze_specification(spec_content, template_info)
                        
                        # Excel 파일 생성
                        file_path = await self.excel_service.generate_excel(analyzed_content)
                        
                        # 파일 저장
                        await sync_to_async(self._update_document)(
                            document,
                            file_path=file_path,
                            status='completed'
                        )
                        
                    elif doc_type == 'ppt':
                        # AI로 명세서 분석
                        analyzed_content = await self.ai_service.analyze_specification(spec_content)
                        
                        # PPT 파일 생성
                        file_path = await self.ppt_service.generate_ppt(analyzed_content)
                        
                        # 파일 저장
                        await sync_to_async(self._update_document)(
                            document,
                            file_path=file_path,
                            status='completed'
                        )
                    
                    result = {
                        "type": doc_type,
                        "status": "success",
                        "document_id": document.id
                    }
                    
                except Exception as e:
                    await sync_to_async(self._update_document)(
                        document,
                        status='failed',
                        error_message=str(e)
                    )
                    result = {
                        "type": doc_type,
                        "status": "failed",
                        "error": str(e)
                    }
                
                results.append(result)
            
            return {
                "message": "문서 생성 요청이 성공적으로 처리되었습니다.",
                "results": results
            }
                
        except Exception as e:
            raise Exception(f"문서 생성 중 오류 발생: {str(e)}")

    def _update_document(self, document, file_path=None, status=None, error_message=None):
        if file_path:
            with open(file_path, 'rb') as f:
                document.file.save(
                    f'{document.doc_type}_{document.id}{Path(file_path).suffix}',
                    File(f),
                    save=False
                )
        if status:
            document.status = status
        if error_message:
            document.error_message = error_message
        document.save()