import subprocess
import sys

def run_demo():
    """데모 앱을 실행합니다."""
    print("🚀 서울시 청년포털 챗봇 데모를 시작합니다...")
    print("📱 브라우저에서 자동으로 열립니다.")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 데모를 종료합니다.")

if __name__ == "__main__":
    run_demo()
