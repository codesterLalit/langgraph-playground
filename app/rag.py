from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class HandbookSearch:
    """Small local handbook retriever built from the course PDF."""

    def __init__(self, pdf_path: Path | str):
        self.pdf_path = Path(pdf_path)
        self._retriever = None

    def _build_retriever(self):
        if not self.pdf_path.is_file():
            raise FileNotFoundError(self.pdf_path)
        documents = PyPDFLoader(str(self.pdf_path)).load()
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
        ).split_documents(documents)
        from langchain_openai import OpenAIEmbeddings
        from langchain_core.vectorstores import InMemoryVectorStore

        store = InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings())
        return store.as_retriever(search_kwargs={"k": 4})

    def search(self, question: str) -> str:
        if self._retriever is None:
            self._retriever = self._build_retriever()
        documents = self._retriever.invoke(question)
        if not documents:
            return "No relevant handbook content found."
        return "\n\n".join(document.page_content for document in documents)
