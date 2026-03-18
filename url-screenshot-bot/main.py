# import streamlit as st
# import pandas as pd
# import os
# import time
# import sys
# import asyncio
# from urllib.parse import urlparse
# from playwright.sync_api import sync_playwright

# # --- Windows 환경에서 NotImplementedError 해결을 위한 설정 ---
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# # --- 페이지 기본 설정 (디자인 강화) ---
# st.set_page_config(page_title="스크린샷 작업 전광판", layout="wide", initial_sidebar_state="expanded")

# # --- 까리한 CSS 스타일 적용 ---
# st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
    
#     /* 전체 배경 및 폰트 설정 */
#     .main { background-color: #0e1117; }
#     p, h1, h2, h3, span { font-family: 'Pretendard', sans-serif; }
    
#     /* 네온 그린 프로그레스 바 */
#     .stProgress > div > div > div > div {
#         background-image: linear-gradient(to right, #00ff41 , #008f11);
#     }
    
#     /* 사이드바 스타일 */
#     [data-testid="stSidebar"] {
#         border-right: 1px solid #30363d;
#     }
    
#     /* 전광판 로그 박스 스타일 */
#     .stCodeBlock {
#         background-color: #000000 !important;
#         border: 1px solid #00ff41 !important;
#         box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
#     }
    
#     /* 메트릭 카드 스타일 */
#     .metric-container {
#         background-color: #1c2128;
#         padding: 15px;
#         border-radius: 10px;
#         border: 1px solid #30363d;
#         text-align: center;
#     }
#     .metric-label { color: #8b949e; font-size: 14px; }
#     .metric-value { color: #00ff41; font-size: 24px; font-weight: bold; text-shadow: 0 0 5px #00ff41; }
#     </style>
#     """, unsafe_allow_html=True)

# # --- 설정값 ---
# RESULT_DIR = "output"
# SET_SIZE = 10

# def get_representative_name(url):
#     try:
#         domain = urlparse(url).netloc
#         name = domain.split('.')[0]
#         if name == 'www' and len(domain.split('.')) > 1:
#             name = domain.split('.')[1]
#         return name if name else "image"
#     except:
#         return "image"

# # 2. 웹 UI 설정 (상단 타이틀 디자인)
# st.markdown("<h1 style='text-align: center; color: #00ff41;'>📟 스크린샷 작업 실시간 현황</h1>", unsafe_allow_html=True)
# st.markdown("<div style='text-align: center; color: #8b949e; margin-bottom: 20px;'>SCREENSHOT COMMAND CENTER v1.0</div>", unsafe_allow_html=True)

# # 3. 사이드바 설정
# st.sidebar.markdown("<h2 style='color: #00ff41;'>📂 데이터 업로드</h2>", unsafe_allow_html=True)
# uploaded_file = st.sidebar.file_uploader("URL이 담긴 엑셀 파일을 선택하세요", type=['xlsx'])

# if uploaded_file:
#     try:
#         df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
#         all_urls = df.iloc[:, 0].dropna().tolist()
#         total_urls = len(all_urls)
        
#         st.sidebar.success(f"✅ 총 {total_urls}개의 URL 로드 완료")
        
#         # 상단 현황판 (카드 형태)
#         c1, c2, c3 = st.columns(3)
#         with c1:
#             st.markdown(f"<div class='metric-container'><div class='metric-label'>전체 타겟</div><div class='metric-value'>{total_urls}</div></div>", unsafe_allow_html=True)
#         with c2:
#             count_placeholder = st.empty()
#             count_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>현재 완료</div><div class='metric-value'>0</div></div>", unsafe_allow_html=True)
#         with c3:
#             time_placeholder = st.empty()
#             time_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>소요 시간</div><div class='metric-value'>0s</div></div>", unsafe_allow_html=True)

#         st.markdown("---")
        
#         # 전광판 UI 레이아웃
#         col1, col2 = st.columns([1, 1])
#         with col1:
#             st.markdown("<h3 style='color: #00ff41;'>📊 전체 진행률</h3>", unsafe_allow_html=True)
#             progress_bar = st.progress(0)
#             status_text = st.empty()
        
#         with col2:
#             st.markdown("<h3 style='color: #00ff41;'>💡 현재 작업 상태</h3>", unsafe_allow_html=True)
#             current_task_display = st.empty()

#         st.markdown("<h3 style='color: #00ff41;'>📝 실시간 작업 히스토리</h3>", unsafe_allow_html=True)
#         log_board = st.empty()
#         logs = ["SYSTEM READY... AWAITING INITIATION"]
#         log_board.code("\n".join(logs), language="bash")

#         if st.sidebar.button("스크린샷 작업 시작 🚀", use_container_width=True):
#             if not os.path.exists(RESULT_DIR):
#                 os.makedirs(RESULT_DIR)

#             with sync_playwright() as p:
#                 status_text.write("🚀 브라우저를 실행하는 중...")
#                 browser = p.chromium.launch(headless=True)
#                 context = browser.new_context(viewport={'width': 1920, 'height': 1080})
#                 page = context.new_page()

#                 global_count = 1
#                 start_time = time.time()

#                 for i in range(0, total_urls, SET_SIZE):
#                     current_set = all_urls[i : i + SET_SIZE]
#                     set_num = (i // SET_SIZE) + 1
                    
#                     set_header = f"\n--- [세트 {set_num}] 작업 시작 (URL {i+1} ~ {min(i+SET_SIZE, total_urls)}) ---"
#                     logs.append(set_header)
#                     log_board.code("\n".join(logs[-15:]))

#                     for url in current_set:
#                         if not str(url).startswith('http'):
#                             url = 'https://' + str(url)

#                         rep_name = get_representative_name(url)
#                         file_name = f"{rep_name}{global_count}.png"
#                         file_path = os.path.join(RESULT_DIR, file_name)
                        
#                         try:
#                             # 실시간 지표 업데이트
#                             elapsed_time = int(time.time() - start_time)
#                             count_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>현재 완료</div><div class='metric-value'>{global_count}</div></div>", unsafe_allow_html=True)
#                             time_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>소요 시간</div><div class='metric-value'>{elapsed_time}s</div></div>", unsafe_allow_html=True)
                            
#                             current_msg = f"[{global_count}/{total_urls}] 처리 중: {url}"
#                             current_task_display.info(current_msg)
                            
#                             page.goto(url, wait_until="networkidle", timeout=60000)
#                             page.wait_for_timeout(500)
#                             page.screenshot(path=file_path, full_page=True)
                            
#                             log_entry = f"   └─ 저장 완료: {file_name}"
#                             logs.append(current_msg)
#                             logs.append(log_entry)
                            
#                             log_board.code("\n".join(logs[-20:]))
#                             progress_bar.progress(global_count / total_urls)
#                             status_text.write(f"진행률: {int((global_count/total_urls)*100)}%")
                            
#                             global_count += 1
#                         except Exception as e:
#                             error_msg = f"   ⚠️ 오류 발생: {url} (건너뜀)"
#                             logs.append(error_msg)
#                             log_board.code("\n".join(logs[-20:]))

#                 browser.close()
#                 st.balloons()
#                 st.success(f"✨ 모든 작업 완료!")
#                 os.startfile(os.path.abspath(RESULT_DIR))

#     except Exception as e:
#         st.error(f"파일 처리 중 오류: {e}")
# else:
#     st.info("사이드바에서 엑셀 파일을 업로드하세요.")



# 배포용 재작성


# main.py 최상단에 추가
import subprocess

# 서버 환경에서 Playwright 브라우저가 없을 경우 자동 설치
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    os.system("pip install playwright")
    os.system("playwright install chromium")

# 만약 서버에서 실행 시 브라우저가 없다는 에러가 나면 아래 한 줄을 실행 로직 앞에 추가하세요.
# subprocess.run(["playwright", "install", "chromium"])


import streamlit as st
import pandas as pd
import os
import time
import sys
import asyncio
import zipfile
import shutil
import uuid
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

# --- Windows 환경 에러 해결 ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="SCREENSHOT COMMAND CENTER V2", layout="wide", initial_sidebar_state="expanded")

# --- 까리한 CSS 스타일 (UI 복구) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
    .main { background-color: #0e1117; }
    p, h1, h2, h3, span { font-family: 'Pretendard', sans-serif; }

    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00ff41 , #008f11); }
    [data-testid="stSidebar"] { border-right: 1px solid #30363d; background-color: #ccc; }
    .stCodeBlock { background-color: #000000 !important; border: 1px solid #00ff41 !important; box-shadow: 0 0 10px rgba(0, 255, 65, 0.2); }
    .metric-container { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .metric-label { color: #8b949e; color: #00ff41; font-size: 14px; }
    .metric-value { color: #00ff41; font-size: 24px; font-weight: bold; text-shadow: 0 0 5px #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- 세션 ID 설정 (서버 자원 관리용) ---
if 'job_id' not in st.session_state:
    st.session_state['job_id'] = str(uuid.uuid4())[:8]
job_id = st.session_state['job_id']
temp_dir = f"temp_{job_id}"
zip_path = f"results_{job_id}.zip"

# --- 유틸리티 함수 ---
def get_representative_name(url):
    try:
        domain = urlparse(url).netloc
        name = domain.split('.')[0]
        if name == 'www' and len(domain.split('.')) > 1:
            name = domain.split('.')[1]
        return name if name else "image"
    except: return "image"

# --- 메인 헤더 ---
st.markdown("<h1 style='text-align: center; color: #333;'>📟 스크린샷 현황</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align: center; color: #00ff41; text-shadow: 0 0 10px #00ff41;'>📟 스크린샷 현황</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center; color: #8b949e; margin-bottom: 20px;'>COMMAND CENTER ID: {job_id}</div>", unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.markdown("<h2 style='color: #333;'>📂 데이터 업로드</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("URL이 담긴 엑셀 파일을 선택하세요", type=['xlsx'])
    st.markdown("---")
    start_btn = st.button("시스템 가동 🚀", use_container_width=True)
    
    if st.button("서버 데이터 정리 🧹", use_container_width=True):
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        if os.path.exists(zip_path): os.remove(zip_path)
        st.success("서버 리소스 정리 완료")

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
    all_urls = df.iloc[:, 0].dropna().tolist()
    total_urls = len(all_urls)
    st.sidebar.success(f"✅ 총 {total_urls}개의 URL 로드 완료")

    # 상단 지표 (Metrics 카드)
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div class='metric-container'><div class='metric-label'>전체 타겟</div><div class='metric-value'>{total_urls}</div></div>", unsafe_allow_html=True)
    count_placeholder = m2.empty()
    time_placeholder = m3.empty()
    count_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>현재 완료</div><div class='metric-value'>0</div></div>", unsafe_allow_html=True)
    time_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>소요 시간</div><div class='metric-value'>0s</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # 전광판 UI 레이아웃 (로그 | 미리보기)
    col_log, col_preview = st.columns([1.2, 0.8])
    
    with col_log:
        st.markdown("<h3 style='color: #00ff41;'>📊 전체 진행률 및 로그</h3>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_board = st.empty()
    
    with col_preview:
        st.markdown("<h3 style='color: #00ff41;'>🔍 최근 캡처 미리보기</h3>", unsafe_allow_html=True)
        preview_placeholder = st.empty()
        preview_placeholder.info("시스템 가동 시 미리보기가 표시됩니다.")

    logs = ["SYSTEM READY... 구동 준비 중 입니다. 파일 업로드 후 시스템 가동 버튼을 눌러주세요."]
    log_board.code("\n".join(logs), language="bash")
    failed_urls = []

    if start_btn:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        with sync_playwright() as p:
            status_text.write("🚀 브라우저 엔진을 가동하는 중...")
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            global_count = 1
            start_time = time.time()

            for i in range(0, total_urls, 10):
                current_set = all_urls[i : i + 10]
                set_num = (i // 10) + 1
                logs.append(f"\n--- [세트 {set_num}] 작업 시작 (URL {i+1} ~ {min(i+10, total_urls)}) ---")
                log_board.code("\n".join(logs[-15:]))

                for url in current_set:
                    if not str(url).startswith('http'): url = 'https://' + str(url)
                    rep_name = get_representative_name(url)
                    file_name = f"{rep_name}{global_count}.png"
                    file_path = os.path.join(temp_dir, file_name)

                    try:
                        elapsed = int(time.time() - start_time)
                        count_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>현재 완료</div><div class='metric-value'>{global_count}</div></div>", unsafe_allow_html=True)
                        time_placeholder.markdown(f"<div class='metric-container'><div class='metric-label'>소요 시간</div><div class='metric-value'>{elapsed}s</div></div>", unsafe_allow_html=True)
                        
                        # 캡처 프로세스
                        page.goto(url, wait_until="networkidle", timeout=60000)
                        page.wait_for_timeout(500)
                        page.screenshot(path=file_path, full_page=True)

                        # 로그 및 UI 업데이트
                        current_msg = f"[{global_count}/{total_urls}] 처리 중: {url}"
                        logs.append(current_msg)
                        logs.append(f"   └─ 저장 완료: {file_name}")
                        
                        log_board.code("\n".join(logs[-20:]))
                        preview_placeholder.image(file_path, caption=f"LIVE FEED: {file_name}", use_container_width=True)
                        progress_bar.progress(global_count / total_urls)
                        status_text.write(f"진행률: {int((global_count/total_urls)*100)}%")
                        
                        global_count += 1
                    except Exception as e:
                        error_msg = f"   ⚠️ 오류 발생: {url} (건너뜀)"
                        logs.append(error_msg)
                        failed_urls.append(url)
                        log_board.code("\n".join(logs[-20:]))

            browser.close()

            # ZIP 생성 (압축 없이 묶기만 하여 CPU 보호)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as z:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        z.write(os.path.join(root, file), file)

            st.balloons()
            st.success("✨ 모든 작동이 완료되었습니다. 좌측 다운로드 버튼을 눌러주세요.")
            
            with st.sidebar:
                st.markdown("---")
                st.markdown("<h3 style='color: #ccc;'>🎁 결과물 다운로드</h3>", unsafe_allow_html=True)
                with open(zip_path, "rb") as f:
                    st.download_button("ZIP 파일 다운로드 📥", f, file_name=zip_path, use_container_width=True)

            if failed_urls:
                st.markdown("<h3 style='color: #ff4b4b;'>❌ 실패한 URL 리스트</h3>", unsafe_allow_html=True)
                st.code("\n".join(failed_urls), language="text")

            # 로컬인 경우 폴더 열기
            try: os.startfile(os.path.abspath(temp_dir))
            except: pass

else:
    st.info("사이드바에서 엑셀 파일을 업로드하면 기능이 활성화됩니다.")