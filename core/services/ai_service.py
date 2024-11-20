import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from .excel_service import ExcelAnalyzer

class AIService:
    def __init__(self):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_excel_template(self, template_path: str) -> dict:
        """Excel 템플릿 분석"""
        try:
            excel_analyzer = ExcelAnalyzer()
            template = await excel_analyzer.analyze_template(template_path)
            
            template_structure = {
                "columns": template.columns,
                "sample_data": template.sample_data,
                "data_types": template.data_types
            }

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """
                    주어진 Excel 템플릿의 구조와 샘플 데이터를 분석하여 
                    비슷한 형식과 스타일의 새로운 컨텐츠를 생성해주세요.
                    각 열의 의미와 샘플 데이터의 패턴을 파악하여 일관된 형식의 데이터를 생성해야 합니다.
                    데이터 타입 정보를 참고하여 적절한 형식의 데이터를 생성해주세요.
                    """},
                    {"role": "user", "content": f"템플릿 구조: {json.dumps(template_structure, ensure_ascii=False)}"}
                ]
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"템플릿 분석 중 오류 발생: {str(e)}")

    async def analyze_specification(self, content: str, template_structure: dict = None) -> dict:
        """명세서 분석 및 구조화"""
        try:
            if template_structure:
                system_prompt = f"""
                주어진 명세서를 분석하여 Excel 템플릿 구조에 맞는 데이터를 JSON 형식으로 생성해주세요.

                템플릿 구조:
                {json.dumps(template_structure, ensure_ascii=False)}

                데이터에는 content의 내용으로 유추할 수 있는 내용 외에는 포함하지 않아야 합니다.
                알 수 없는 열은 비워두어야 합니다.
                응답은 반드시 유효한 JSON 객체여야 하며, 데이터는 배열 형태로 제공해주세요.
                예시 응답 형식:
                {{"data": [{{"column1": "value1", "column2": "value2", ...}}]}}
                """
            else:
                system_prompt = """
                명세서를 분석하여 JSON 형식으로 응답해주세요.

                데이터에는 content의 내용으로 유추할 수 있는 내용 외에는 포함하지 않아야 합니다.
                알 수 없는 열은 비워두어야 합니다.
                응답은 반드시 유효한 JSON 객체여야 하며, 최소 1개 이상의 데이터를 포함해야 합니다.
                예시 응답 형식:
                {{"data": [{{"column1": "value1", "column2": "value2", ...}}]}}
                """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"AI 분석 중 오류 발생: {str(e)}")
