import requests
import time
import argparse
import os
import csv

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

def load_retriever(chroma_path):
    embeddings = OpenAIEmbeddings()
    vs = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    return vs.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 5})

def ask_question(question, api_url, retriever, session_id="test-session"):
    # 1. 요청 및 응답 시간 측정
    payload = {"session_id": session_id, "user_message": question}
    start = time.perf_counter()
    res = requests.post(api_url, json=payload)
    end = time.perf_counter()

    try:
        data = res.json()
        answer = data.get("response", "")
    except Exception as e:
        answer = f"[ERROR] {str(e)}"

    elapsed = round(end - start, 3)

    # 2. 유사도 문서 추출
    try:
        results = retriever.vectorstore.similarity_search_with_score(question, k=3)
        scores = [(doc.metadata.get("category", "no-category"), round(score, 4)) for doc, score in results]
    except Exception as e:
        scores = [("유사도 추출 실패", 1.0)]

    return question, answer.strip(), elapsed, scores

def run(filepath, api_url, chroma_path, save_csv=None, limit=None):
    retriever = load_retriever(chroma_path)

    with open(filepath, "r", encoding="utf-8") as f:
        questions = [q.strip() for q in f if q.strip()]

    if limit:
        questions = questions[:limit]

    rows = []
    print(f"🧪 총 {len(questions)}개 질문 테스트 시작")
    
    for i, q in enumerate(questions, 1):
        q, a, t, scores = ask_question(q, api_url, retriever)
        print(f"[{i}] ⏱ {t:.3f}s | ❓ {q}")
        print(f"    💬 {a[:100]}...")
        print(f"    🔎 유사도:")
        for idx, (cat, score) in enumerate(scores, 1):
            print(f"     {idx}. {cat} | score={score}")
        print()

        rows.append({"index": i, "question": q, "time_sec": t, "answer": a})

    if save_csv:
        with open(save_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"📁 CSV 저장 완료: {save_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["local", "prod"], default="local", help="테스트 환경 선택")
    parser.add_argument("--url", default=None, help="API 수동 주소 입력 (선택)")
    parser.add_argument("--file", default="questions.txt", help="질문 목록 경로")
    parser.add_argument("--save_csv", default=None, help="CSV 저장 경로 (선택)")
    parser.add_argument("--limit", type=int, default=None, help="테스트 질문 수 제한")

    args = parser.parse_args()

    # 자동 URL 설정
    default_urls = {
        "local": "http://localhost:8000/chat",
        "prod": "https://youth-chatbot-backend.onrender.com/chat"
    }
    api_url = args.url or default_urls[args.env]
    chroma_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db"))
    question_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.file))

    run(filepath=question_path, api_url=api_url, chroma_path=chroma_path, save_csv=args.save_csv, limit=args.limit)
