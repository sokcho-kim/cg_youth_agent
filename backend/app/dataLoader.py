import os
import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from .llm_manager import (
    get_or_create_memory, 
    extract_user_profile, 
    create_qa_chain, 
    get_active_sessions_count
)

# ChromaDB 텔레메트리 비활성화
os.environ["ANONYMIZED_TELEMETRY"] = "False"

def load_policy_data():
    """정책 데이터를 로드하고 Document 객체로 변환 (text 필드만 사용)"""
    try:
        DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/seoul_youth_policies_with_url_rag.jsonl')
        if not os.path.exists(DATA_PATH):
            print(f"Warning: Data file not found at {DATA_PATH}")
            return []
        documents = []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    doc_data = json.loads(line.strip())
                    policy_text = doc_data.get('text', '')
                    document = Document(
                        page_content=policy_text,
                        metadata={
                            'id': doc_data.get('id', ''),
                            'category': doc_data.get('category', ''),
                            'source': 'seoul_youth_policies_with_url_rag'
                        }
                    )
                    documents.append(document)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
        print(f"Successfully loaded {len(documents)} policy documents")
        return documents
    except Exception as e:
        print(f"Error loading policy data: {e}")
        return []

def initialize_vectorstore():
    """벡터스토어 초기화 및 데이터 로드"""
    try:
        embeddings = OpenAIEmbeddings()
        persist_directory = os.path.join(os.path.dirname(__file__), '../chroma_db')
        
        # 기존 벡터스토어가 있는지 확인
        if os.path.exists(persist_directory):
            print("Loading existing vectorstore...")
            try:
                vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
                collection = vectorstore._collection
                if collection.count() > 0:
                    print(f"Found {collection.count()} existing documents in vectorstore")
                    return vectorstore
            except Exception as e:
                print(f"Error loading existing vectorstore: {e}")
                print("Creating new vectorstore...")
        
        # 새로운 벡터스토어 생성
        print("Creating new vectorstore...")
        documents = load_policy_data()
        
        if not documents:
            print("No documents loaded. Creating empty vectorstore.")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separator="\n")
            split_docs = text_splitter.split_documents(documents)
            print(f"Split documents into {len(split_docs)} chunks")
            
            try:
                vectorstore = Chroma.from_documents(
                    documents=split_docs,
                    embedding=embeddings,
                    persist_directory=persist_directory
                )
                vectorstore.persist()
                print(f"Vectorstore created with {len(split_docs)} document chunks")
            except Exception as e:
                print(f"Error creating vectorstore with embeddings: {e}")
                print("Creating empty vectorstore without embeddings...")
                vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        
        return vectorstore
        
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        print("Creating empty vectorstore as fallback...")
        try:
            persist_directory = os.path.join(os.path.dirname(__file__), '../chroma_db')
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=None)
            return vectorstore
        except Exception as fallback_error:
            print(f"Fallback vectorstore creation failed: {fallback_error}")
            return None

def get_vectorstore_and_retriever():
    """벡터스토어와 리트리버를 초기화하고 반환"""
    print("Initializing vectorstore...")
    vectorstore = initialize_vectorstore()

    if vectorstore is None:
        print("Warning: Vectorstore initialization failed. RAG functionality will be disabled.")
        return None, None, False
    else:
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": 0.85,  # 임계값: 0.8~0.9 정도 추천
                "k": 10                   # 최대 문서 수
            }
        )
        return vectorstore, retriever, True