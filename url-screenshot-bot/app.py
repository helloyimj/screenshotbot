import streamlit as st
import pandas as pd
import os
import time
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

# 페이지 설정
st.set_page_config(page_title="스크린샷 현황", layout="wide")
st.title("📸 실시간 스크린샷 현황")

def get_rep_name(url):
    try:
        domain = urlparse(url).netloc
        name = domain.split('.')[0]
        return name if name != 'www' else domain.split('.')[1]
    except: return "img"

# 1. 파일 업로드 섹션
uploaded_file = st.file_uploader("URL 리스트 엑셀 파일을 업로드하세요", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    urls = df.iloc[:, 0].dropna().tolist()
    total_urls = len(urls)
    
    st.success(f"총 {total_urls}개의 URL을 확인했습니다. 작업을 시작합니다.")

    # 2. 전광판 UI 요소 설정
    progress_bar = st.progress(0) # 진행률 바
    status_text = st.empty()      # 현재 상태 메시지
    
    # 실시간 히스토리 전광판 (검은색 터미널 느낌)
    st.subheader("📝 작업 히스토리")
    log_container = st.empty() 
    log_history = []

    # 3. 스크린샷 로직 실행
    if st.button("스크린샷 작업 시작"):
        save_dir = "screenshots"
        os.makedirs(save_dir, exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            for idx, url in enumerate(urls, 1):
                # 세트 계산 (10개 단위)
                set_num = ((idx - 1) // 10) + 1
                if (idx - 1) % 10 == 0:
                    set_msg = f"--- [세트 {set_num}] 작업 시작 (URL {idx} ~ {min(idx+9, total_urls)}) ---"
                    log_history.append(set_msg)

                try:
                    # 현재 진행 상태 업데이트
                    status_msg = f"[{idx}/{total_urls}] 처리 중: {url}"
                    status_text.write(f"**현재 작업:** {status_msg}")
                    
                    # 브라우저 작업
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    rep_name = get_rep_name(url)
                    file_path = f"{save_dir}/{rep_name}{idx}.png"
                    page.screenshot(path=file_path, full_page=True)
                    
                    # 로그 추가 및 전광판 갱신
                    log_history.append(status_msg)
                    # 최신 15개 로그만 보여주기 (전광판 느낌)
                    log_container.code("\n".join(log_history[-15:]))
                    
                    # 진행률 바 업데이트
                    progress_bar.progress(idx / total_urls)
                    
                except Exception as e:
                    error_msg = f"[{idx}/{total_urls}] ❌ 오류: {url} ({str(e)[:50]}...)"
                    log_history.append(error_msg)
                    log_container.code("\n".join(log_history[-15:]))

            browser.close()
        
        st.balloons() # 완료 효과
        st.success("모든 작업이 완료되었습니다!")
        
        # 압축 파일 생성 및 다운로드 버튼 (이후 추가 가능)