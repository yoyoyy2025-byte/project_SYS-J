import streamlit as st
from rag_system import CareerAI
from career_data import CAREER_TIPS
# 구글 시트 로거 대신 에러 방지를 위해 로컬 DB만 사용하는 설정으로 변경할 수도 있으나, 
# 일단 기존 import 유지하되 try-except로 감쌉니다.
from user_db import init_user_db, save_message, get_all_history 
from file_utils import extract_text_from_file
import time
import os

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
    [data-testid="stHeader"] { display: none; }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 250px !important;
        max-width: 700px !important;
    }

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
# 2. 시스템 초기화 및 예외 처리
# -------------------------------------------------------------------------

# 🔥 [핵심 수정] Ngrok은 로컬에서만 씁니다. (클라우드에선 에러 안 나게 처리)
public_url = None
try:
    from pyngrok import ngrok
    # 로컬 환경일 때만 ngrok 실행
    if os.environ.get("STREAMLIT_SERVER_ADDRESS") != "localhost": 
        # Streamlit Cloud 등에서는 실행 안 함
        pass
    else:
        # 로컬에서 실행 중이면 연결 시도
        try:
            ngrok.kill()
            public_url = ngrok.connect("127.0.0.1:8502").public_url
        except:
            pass
except ImportError:
    # pyngrok 라이브러리가 아예 없으면(클라우드 환경) 그냥 넘어감
    pass


@st.cache_resource
def init_system():
    init_user_db() 
    ai = CareerAI()
    ai.load_data(CAREER_TIPS)
    # 로그 설정 (파일 없으면 에러 안 나게 처리)
    try:
        logger = RealTimeLogger('monitor/service_key.json', 'CareerLog')
    except:
        logger = None # 로그 기능 끄기
    return ai, logger

try:
    ai_system, logger = init_system()
except Exception as e:
    st.error(f"시스템 오류: {e}")
    st.stop()

# 로그 기록 헬퍼 함수 (logger가 없어도 죽지 않게)
def safe_log(user_id, action, details):
    if logger:
        logger.log(user_id, action, details)
    else:
        print(f"[{user_id}] {action}: {details}")

# -------------------------------------------------------------------------
# 3. 메인 UI
# -------------------------------------------------------------------------
st.title("🎓 Job-Navigator")

# Ngrok 주소가 있을 때만 표시 (로컬용)
if public_url:
    with st.expander("🔗 (개발용) 친구 초대 링크 보기", expanded=False):
        st.code(public_url, language="text")

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
        
        safe_log("User", "REQ_COACHING", prompt[:30])

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
        
        # API Key 관리
        with st.expander("🔑 API Key 업데이트", expanded=True):
            st.info("보안을 위해 현재 등록된 Key는 표시하지 않습니다. 새로운 Key가 필요할 때만 입력하세요.")
            new_key = st.text_input("새로운 API Key 입력", type="password", placeholder="AIza...")
            if st.button("🔄 Key 덮어쓰기"):
                if new_key.strip():
                    os.environ["GOOGLE_API_KEY"] = new_key.strip()
                    st.cache_resource.clear()
                    st.toast("새로운 Key가 적용되었습니다! 시스템을 재시작합니다.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("키를 입력해주세요.")

        st.divider()

        # 사용자 데이터
        st.markdown("##### 📥 사용자 데이터")
        history_df = get_all_history()
        st.dataframe(history_df, use_container_width=True)
        
        st.divider()
        
        # 지식 추가
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