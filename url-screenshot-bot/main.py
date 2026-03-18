import os
import subprocess
import time
import sys
import asyncio
import zipfile
import shutil
import uuid
import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# [서버 전용] Playwright 및 브라우저 강제 설치 함수 (중복 로직 통합)
@st.cache_resource
def install_playwright():
    try:
        # 이미 설치되어 있는지 확인
        subprocess.run(["playwright", "--version"], check=True)
    except FileNotFoundError:
        # 설치가 안 되어 있다면 설치 진행
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    
    # 브라우저 및 시스템 의존성 설치 (가장 확실한 방법)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install-deps"], check=False)

# 앱 실행 시 가장 먼저 실행 (서버 환경 세팅)
install_playwright()

# 이제 안전하게 import 가능
from playwright.sync_api import sync_playwright

# --- Windows 환경 에러 해결 ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="SCREENSHOT COMMAND CENTER V2", layout="wide", initial_sidebar_state="expanded")

# --- CSS 스타일 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
    .main { background-color: #0e1117; }
    p, h1, h2, h3, span { font-family: 'Pretendard', sans-serif; }

    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00ff41 , #008f11); }
    [data-testid="stSidebar"] { border-right: 1px solid #30363d; background-color: #ccc; }
    .stCodeBlock { background-color: #000000 !important; border: 1px solid #00ff41 !important; box-shadow: 0 0 10px rgba(0, 255, 65, 0.2); }
    .metric-container { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .metric-label { color: #00ff41; font-size: 14px; }
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

    # 콤마(,) 누락 버그 수정
    logs = [
        "✅ SYSTEM READY... 구동 준비가 완료되었습니다.",
        "",
        "⏱️ 첫 실행 시 환경 구성 작업으로 인해 다소 시간이 소요될 수 있습니다.",
        "📢 로그가 뜰 때까지 브라우저를 종료하지 마세요.",
        "🧹 무료 서버의 안정성을 위해 *** 모든 작업의 종료 후 [서버 데이터 정리]버튼을 눌러주세요."
    ]
    log_board.code("\n".join(logs), language="bash")
    failed_urls = []

    if start_btn:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # 💡 [로컬/서버 만능 호환 로직] 
        # 컴퓨터에 깔린 크롬 경로를 찾습니다. (리눅스용, 윈도우용 모두 확인)
        system_chromium_path = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or shutil.which("chrome")
        
        with sync_playwright() as p:
            status_text.write("🚀 브라우저 엔진을 가동하는 중...")
            
            # 실행 옵션 (로컬과 서버 모두 안정적으로 돌아가게 설정)
            launch_args = {
                "headless": True,
                "args": [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions'
                ]
            }
            
            # 서버 환경이거나 시스템 크롬이 발견되면 해당 경로를 사용
            if system_chromium_path:
                launch_args["executable_path"] = system_chromium_path
                
            # 브라우저 실행!
            browser = p.chromium.launch(**launch_args)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            global_count = 1
            start_time = time.time()

            # --- 이후 반복문(for i in range...)은 기존 코드와 100% 동일하게 유지 ---
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
                        
                        page.goto(url, wait_until="networkidle", timeout=60000)
                        page.wait_for_timeout(500)
                        page.screenshot(path=file_path, full_page=True)

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

            # 로컬인 경우 폴더 열기 (서버에서는 작동하지 않으나 에러는 안 남)
            try: os.startfile(os.path.abspath(temp_dir))
            except: pass

else:
    st.info("사이드바에서 엑셀 파일을 업로드 후 시스템 가동 버튼을 누르면 기능이 활성화됩니다.")