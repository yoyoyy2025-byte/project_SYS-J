import os
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import datetime

load_dotenv()

if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class CareerAI:
    def __init__(self):
        if not os.getenv("GOOGLE_API_KEY"):
            return
        
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="career_collection", 
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def load_data(self, data_list):
        if not os.getenv("GOOGLE_API_KEY"): return
        if self.collection.count() > 0: return 
        
        ids = [str(i) for i in range(len(data_list))]
        documents = [item['content'] for item in data_list]
        metadatas = [{"source": item['source'], "category": item['category']} for item in data_list]

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print("✅ 초기 데이터 로드 완료")

    def add_new_tip(self, category, source, content):
        if not os.getenv("GOOGLE_API_KEY"): return False
        new_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            self.collection.add(
                documents=[content],
                metadatas=[{"category": category, "source": source}],
                ids=[new_id]
            )
            return True
        except Exception as e:
            print(f"학습 실패: {e}")
            return False

    def get_coaching(self, user_text):
        if not os.getenv("GOOGLE_API_KEY"):
            return "API 키가 없습니다.", [], None

        # RAG 검색
        results = self.collection.query(query_texts=[user_text], n_results=2)
        
        found_tips = ""
        sources = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                source_info = f"{meta['category']} - {meta['source']}"
                found_tips += f"- {source_info}: {doc}\n"
                sources.append(source_info)

        # ------------------------------------------------------------------
        # Step 1: 팩트 체크 (냉정한 현실 인식)
        # ------------------------------------------------------------------
        draft_prompt = f"""
        당신은 냉철한 채용 평가관입니다.
        감정을 배제하고 오직 [작성 가이드]와 채용 현실을 기준으로 지원자의 글을 평가하세요.
        "무조건 가능하다"는 판단을 내리지 말고, 부족한 점이나 리스크를 찾아내세요.

        [작성 가이드]
        {found_tips}

        [사용자 자소서 내용]
        {user_text}
        """
        
        try:
            draft_response = self.model.generate_content(draft_prompt)
            draft_text = draft_response.text
        except Exception as e:
            return f"분석 중 에러: {str(e)}", [], None

        # ------------------------------------------------------------------
        # Step 2: 진정성 있는 상담 (Counseling) - 희망 고문 금지
        # ------------------------------------------------------------------
        refine_prompt = f"""
        당신은 의뢰인의 고민을 깊이 들어주는 '진로 상담 전문가'입니다.
        앞선 [분석 내용]을 바탕으로 의뢰인에게 답변을 해주세요.

        [분석 내용]
        {draft_text}

        [사용자 원문]
        {user_text}

        [상담 가이드 - 중요]
        1. **무조건적인 긍정 금지**: "합격합니다", "완벽합니다" 같은 말 대신 "현재 상태에서는 ~한 부분이 우려됩니다"라고 솔직하게 말하세요.
        2. **공감과 경청**: 의뢰인이 쓴 글에서 느껴지는 노력이나 고민을 먼저 읽어주고 공감하세요 ("~라고 쓰신 부분에서 고민이 많이 느껴지네요").
        3. **현실적 대안 제시**: 단순히 고치라는 말보다는, "채용 담당자는 이 부분을 이렇게 오해할 수 있으니, 차라리 ~한 경험을 더 강조하는 게 전략적으로 좋습니다"라고 조언하세요.
        4. **질문 유도**: 의뢰인이 스스로 생각할 수 있도록 "~한 경험은 없으신가요?", "이 부분을 좀 더 구체적으로 설명해주실 수 있나요?"라고 되물어보세요.
        5. **말투**: "~해요"체를 사용하여 옆에서 차분하게 이야기하듯 작성하세요.
        """

        try:
            final_response = self.model.generate_content(refine_prompt)
            return final_response.text, sources, draft_text 
        except Exception as e:
            return f"코칭 중 에러: {str(e)}", [], None