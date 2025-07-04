#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_vectorstore():
    """벡터스토어 상태 테스트"""
    try:
        from app.dataLoader import get_vectorstore_and_retriever
        print("=== 벡터스토어 테스트 ===")
        
        vs, ret, enabled = get_vectorstore_and_retriever()
        print(f"Vectorstore enabled: {enabled}")
        print(f"Vectorstore: {vs}")
        print(f"Retriever: {ret}")
        
        if vs and hasattr(vs, '_collection'):
            count = vs._collection.count()
            print(f"Collection count: {count}")
            
            if count > 0:
                # 샘플 검색 테스트
                print("\n=== 검색 테스트 ===")
                test_queries = [
                    "청년 주거 지원정책",
                    "신혼부부 주택",
                    "전세자금 대출"
                ]
                
                for query in test_queries:
                    print(f"\n검색어: {query}")
                    try:
                        docs = ret.get_relevant_documents(query)
                        print(f"검색된 문서 수: {len(docs)}")
                        if docs:
                            print(f"첫 번째 문서: {docs[0].page_content[:100]}...")
                    except Exception as e:
                        print(f"검색 오류: {e}")
        else:
            print("벡터스토어가 비어있거나 초기화되지 않음")
            
    except Exception as e:
        print(f"벡터스토어 테스트 오류: {e}")
        import traceback
        traceback.print_exc()

def test_routing():
    """라우팅 함수 테스트"""
    try:
        from app.llm_manager import is_housing_policy_question
        print("\n=== 라우팅 테스트 ===")
        
        test_questions = [
            "20대 청년 주거 지원정책이 있나",
            "자취하고 싶은데 돈이 없어",
            "신혼 부부를 위한 주거 정책은?",
            "세금 관련 질문입니다",
            "청년 전세자금 대출 받을 수 있나요"
        ]
        
        for question in test_questions:
            result = is_housing_policy_question(question)
            print(f"질문: {question}")
            print(f"결과: {result}")
            print()
            
    except Exception as e:
        print(f"라우팅 테스트 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vectorstore()
    test_routing() 