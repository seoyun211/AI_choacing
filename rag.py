import os
import glob

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

POSTING_DIR = "data/postings"
DB_DIR = "data/chroma"
EMBED_MODEL = "bge-m3"

embeddings = OllamaEmbeddings(model=EMBED_MODEL)


# ============================================================
# 준비 단계 — 공고를 읽어 벡터DB에 저장 (한 번만 실행)
# ============================================================
def build_index():
    """공고 파일을 읽고 조각내어 벡터DB에 저장한다."""
    paths = sorted(glob.glob(os.path.join(POSTING_DIR, "*.txt")))
    print(f"공고 파일 {len(paths)}개 발견")

    docs = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()

        filename = os.path.basename(path)
        company = _extract(text, "회사:")
        job = _extract(text, "직무:")

        docs.append(Document(
            page_content=text,
            metadata={"source": filename, "company": company, "job": job},
        ))

    # 조각내기 (Chunking)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n[", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"조각 {len(chunks)}개 생성 (평균 {len(chunks)/len(docs):.1f}개/공고)")

    # 임베딩 + 저장
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
    )
    print(f"벡터DB 저장 완료: {DB_DIR}")
    return db


def _extract(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(key):
            return line.replace(key, "").strip()
    return ""


# ============================================================
# 검색 단계 — 질문과 유사한 조각 찾기
# ============================================================
_db = None


def get_db():
    """저장된 벡터DB를 불러온다."""
    global _db
    if _db is None:
        _db = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings,
        )
    return _db


def search(job: str, answer: str, k: int = 3) -> list:
    """직무와 답변 내용으로 관련 공고 조각을 검색한다."""
    query = f"{job} 채용 자격요건 우대사항 {answer[:200]}"
    return get_db().similarity_search(query, k=k)


def format_context(docs: list) -> str:
    """검색 결과를 프롬프트에 넣을 형태로 정리한다."""
    if not docs:
        return "(참고할 채용공고를 찾지 못했습니다)"

    parts = []
    for i, d in enumerate(docs, 1):
        company = d.metadata.get("company", "?")
        job = d.metadata.get("job", "?")
        parts.append(
            f"[공고 {i}] {company} - {job}\n{d.page_content.strip()}"
        )
    return "\n\n".join(parts)


# ============================================================
# 직접 실행하면 인덱스를 만든다
# ============================================================
if __name__ == "__main__":
    build_index()
