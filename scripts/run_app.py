import subprocess
import sys
import os

def install_requirements():
    """필요한 패키지들을 설치합니다."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 필요한 패키지가 모두 설치되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 중 오류가 발생했습니다: {e}")
        return False
    return True

def run_streamlit_app():
    """Streamlit 앱을 실행합니다."""
    try:
        print("🚀 서울시 청년포털 챗봇을 시작합니다...")
        print("📱 브라우저에서 http://localhost:8501 로 접속하세요.")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 챗봇을 종료합니다.")
    except Exception as e:
        print(f"❌ 앱 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🏛️  서울시 청년포털 챗봇")
    print("=" * 50)
    
    # 패키지 설치
    if install_requirements():
        # Streamlit 앱 실행
        run_streamlit_app()
