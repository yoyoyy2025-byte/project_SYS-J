import streamlit as st
import streamlit.components.v1 as components
from pyngrok import ngrok
from rag_system import CareerAI
from career_data import CAREER_TIPS
from monitor.gsheet_logger import RealTimeLogger
from user_db import init_user_db, save_message, get_all_history 
import time

# -------------------------------------------------------------------------
# 1. 기본 설정
# -------------------------------------------------------------------------
ADMIN_PASSWORD = "1234"
st.set_page_config(page_title="Job-Navigator Plus", page_icon="🎓", layout="centered")

# 💄 스타일 설정
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 화면 바닥 여백 */
    .block-container {
        padding-bottom: 250px !important;
    }

    /* 입력창 디자인 (Gemini 스타일 + 하단 고정) */
    .stChatInput {
        position: fixed;
        bottom: 40px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100% !important;
        max-width: 700px !important;
        z-index: 9999;
        background-color: transparent !important;
    }

    /* 입력 박스 */
    div[data-testid="stChatInput"] {
        background-color: #f0f4f9 !important;
        border-radius: 30px !important;
        border: 1px solid transparent !important;
        padding: 10px 20px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    }
    
    div[data-testid="stChatInput"]:focus-within {
        border: 1px solid #d0d7de !important;
        background-color: white !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1) !important;
    }

    /* 텍스트 영역 */
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        border: none !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        color: #1f1f1f !important;
        height: auto !important;
        min-height: 24px !important; 
        max-height: 200px !important;
        padding: 0px !important;
        margin-top: 5px !important;
    }
    
    [data-testid="stChatInputSubmitButton"] {
        background-color: transparent !important;
        color: #555 !important;
        border: none !important;
        padding-right: 10px !important;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 화면 스크롤 내리기
def scroll_to_bottom():
    js = """
    <script>
        var body = window.parent.document.querySelector(".main");
        body.scrollTop = body.scrollHeight;
    </script>
    """
    components.html(js, height=0)

# -------------------------------------------------------------------------
# 2. 시스템 초기화
# -------------------------------------------------------------------------
@st.cache_resource
def init_system():
    init_user_db() 
    ai = CareerAI()
    ai.load_data(CAREER_TIPS)
    logger = RealTimeLogger('monitor/service_key.json', 'CareerLog')
    return ai, logger

try:
    ai_system, logger = init_system()
except Exception as e:
    st.error(f"시스템 오류: {e}")
    st.stop()

@st.cache_resource
def init_connection():
    try:
        ngrok.kill()
        # 8502 포트로 터널 생성
        return ngrok.connect("127.0.0.1:8502").public_url
    except:
        return None
public_url = init_connection()

# -------------------------------------------------------------------------
# 3. 메인 UI
# -------------------------------------------------------------------------
st.title("🎓 Job-Navigator")

# 🔥 [핵심 추가] 접속 주소 표시 (화면 최상단)
if public_url:
    st.success("👇 친구들에게 이 주소를 보내세요!")
    st.code(public_url, language="text") # 복사하기 쉬운 코드 박스

tab1, tab2 = st.tabs(["📝 자소서 첨삭", "⚙️ 관리자"])

# =========================================================================
# 탭 1: 자소서 첨삭
# =========================================================================
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 자소서 내용을 입력해주시면 분석해 드립니다."}]

    for msg in st.session_state.messages:
        avatar = "🎓" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
    
    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("내용을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        logger.log("User", "REQ_COACHING", prompt[:30])

        with st.chat_message("assistant", avatar="🎓"):
            with st.status("분석 중...", expanded=True) as status:
                st.write("🔍 데이터베이스 조회...")
                time.sleep(0.5)
                
                response_text, sources, draft_text = ai_system.get_coaching(prompt)
                
                st.write("✨ 답변 작성 중...")
                time.sleep(0.5)
                status.update(label="완료!", state="complete", expanded=False)

            st.markdown(response_text)

        save_message(prompt, response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        scroll_to_bottom()

# =========================================================================
# 탭 2: 관리자 모드
# =========================================================================
with tab2:
    st.subheader("⚙️ 관리자")
    input_pw = st.text_input("비밀번호", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        st.success("인증됨")
        
        st.markdown("##### 📥 사용자 데이터")
        history_df = get_all_history()
        st.dataframe(history_df, use_container_width=True)
        
        st.divider()
        
        st.markdown("##### 🧠 지식 추가")
        col1, col2 = st.columns([1, 2])
        with col1:
            new_category = st.selectbox("카테고리", ["첨삭예시", "합격자소서", "직무역량", "면접질문"])
            new_source = st.text_input("제목", placeholder="예: 우수 사례")
        with col2:
            new_content = st.text_area("학습 내용", height=100)

        if st.button("💾 학습시키기"):
            if new_source and new_content:
                success = ai_system.add_new_tip(new_category, new_source, new_content)
                if success:
                    st.toast("학습 완료!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("내용 입력 필요")
    else:
        if input_pw: st.error("오류")