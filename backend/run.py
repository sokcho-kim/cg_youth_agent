#!/usr/bin/env python3
"""
Youth Policy Chatbot Launcher
서울시 청년 정책 챗봇 실행 스크립트
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def print_banner():
    """배너 출력"""
    print("=" * 60)
    print("🏛️  서울시 청년포털 챗봇")
    print("=" * 60)
    print("💬 청년 정책 정보를 쉽게 찾아보세요!")
    print("=" * 60)

def check_requirements():
    """필요한 패키지 설치 확인"""
    try:
        print("📦 필요한 패키지를 확인하고 설치합니다...")
        print("   (이 과정은 처음 실행 시에만 필요합니다)")
        
        # pip 업그레이드
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 패키지 설치
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 패키지 설치 완료!")
            return True
        else:
            print("⚠️  일부 패키지 설치에 문제가 있을 수 있습니다.")
            print("   계속 진행하거나 수동으로 설치해주세요:")
            print("   pip install -r requirements.txt")
            return True  # 계속 진행
            
    except Exception as e:
        print(f"⚠️  패키지 설치 중 오류: {e}")
        print("   수동으로 설치해주세요: pip install -r requirements.txt")
        return True  # 계속 진행

def check_data_file():
    """데이터 파일 존재 확인"""
    data_path = Path(__file__).parent.parent / "data" / "seoul_youth_policies_categorized.jsonl"
    if not data_path.exists():
        print(f"❌ 데이터 파일을 찾을 수 없습니다: {data_path}")
        print("   data/seoul_youth_policies_categorized.jsonl 파일이 필요합니다.")
        return False
    print(f"✅ 데이터 파일 확인: {data_path}")
    return True

def check_openai_key():
    """OpenAI API 키 확인"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "YOUR_OPENAI_API_KEY":
        print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
        print("   환경 변수로 설정하거나 server.py 파일에서 직접 설정해주세요.")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   또는 server.py 파일에서 직접 설정")
        return False
    print("✅ OpenAI API 키 확인됨")
    return True

def run_fastapi_server():
    """FastAPI 서버 실행 (백그라운드)"""
    try:
        print("🔌 FastAPI 서버 시작 중...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI 서버 실행 오류: {e}")
    except KeyboardInterrupt:
        print("\n👋 FastAPI 서버를 종료합니다.")

def run_streamlit_app():
    """Streamlit 앱 실행 (메인)"""
    try:
        print("🌐 Streamlit 앱 시작 중...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501",
            "--server.headless", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit 앱 실행 오류: {e}")
    except KeyboardInterrupt:
        print("\n👋 Streamlit 앱을 종료합니다.")

def start_services():
    """서비스들을 동시에 시작"""
    print("\n🚀 서비스들을 시작합니다...")
    print("📡 FastAPI 서버: http://localhost:8000")
    print("📱 Streamlit 앱: http://localhost:8501")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔍 헬스체크: http://localhost:8000/health")
    print("\n   Ctrl+C로 모든 서비스를 종료할 수 있습니다.")
    print("=" * 60)
    
    # FastAPI 서버를 백그라운드 스레드로 시작
    server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    server_thread.start()
    
    # 잠시 대기하여 서버가 시작되도록 함
    time.sleep(3)
    
    # Streamlit 앱을 메인 스레드에서 시작
    run_streamlit_app()

def main():
    """메인 함수"""
    print_banner()
    
    # 현재 디렉토리 확인
    if not Path("app.py").exists() or not Path("server.py").exists():
        print("❌ 오류: app.py 또는 server.py 파일을 찾을 수 없습니다.")
        print("   scripts 디렉토리에서 실행해주세요.")
        return
    
    # 환경 확인
    check_requirements()
    
    if not check_data_file():
        return
    
    # OpenAI API 키 확인
    api_key_ok = check_openai_key()
    
    if not api_key_ok:
        print("\n⚠️  OpenAI API 키가 설정되지 않았습니다.")
        print("   Streamlit 앱만 실행됩니다 (RAG 기능 제한).")
        print("   FastAPI 서버를 사용하려면 OpenAI API 키를 설정해주세요.")
        
        # API 키가 없어도 Streamlit 앱은 실행
        print("\n🌐 앱을 시작합니다...")
        print("📱 브라우저에서 http://localhost:8501 로 접속하세요.")
        run_streamlit_app()
    else:
        # 모든 서비스 시작
        start_services()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 모든 서비스를 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        print("   문제가 지속되면 수동으로 서비스를 시작해주세요:")
        print("   - FastAPI: uvicorn server:app --host 0.0.0.0 --port 8000 --reload")
        print("   - Streamlit: streamlit run app.py --server.port 8501")
