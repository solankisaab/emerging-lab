"""
RAG Pipeline — Retrieval-Augmented Generation for news Q&A.
Flow: Query → Embed → Vector Search → Retrieve Chunks → LLM Answer
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are an AI news assistant. Use the following news articles as context to answer the user's question accurately and concisely.

Context (News Articles):
{context}

Question: {question}

Answer (include source references if possible):"""


class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.vectorstore = None
        self.qa_chain = None

    def load_vectorstore(self, path: str):
        """Load persisted FAISS vector store from disk."""
        try:
            self.vectorstore = FAISS.load_local(
                path, self.embeddings, allow_dangerous_deserialization=True
            )
            self._build_chain()
            logger.info(f"Vector store loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise

    def _build_chain(self):
        """Build the RetrievalQA chain."""
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": settings.RAG_TOP_K}
            ),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )

    async def query(self, question: str) -> dict:
        """Run a RAG query and return answer + sources."""
        if not self.qa_chain:
            raise RuntimeError("Vector store not loaded. Run ingest first.")

        result = self.qa_chain.invoke({"query": question})
        sources = [
            {
                "title": doc.metadata.get("title", "Unknown"),
                "source": doc.metadata.get("source", ""),
                "url": doc.metadata.get("url", ""),
                "published_at": doc.metadata.get("published_at", ""),
            }
            for doc in result.get("source_documents", [])
        ]
        return {
            "answer": result["result"],
            "sources": sources,
        }

    def ingest_articles(self, articles: list[dict], save_path: str):
        """
        Embed and store articles into the vector store.
        Each article: {"title": ..., "content": ..., "url": ..., "source": ...}
        """
        from langchain.schema import Document

        docs = [
            Document(
                page_content=f"{a['title']}\n\n{a.get('content', '')}",
                metadata={
                    "title": a["title"],
                    "source": a.get("source", ""),
                    "url": a.get("url", ""),
                    "published_at": a.get("published_at", ""),
                },
            )
            for a in articles
        ]

        if self.vectorstore:
            self.vectorstore.add_documents(docs)
        else:
            self.vectorstore = FAISS.from_documents(docs, self.embeddings)
            self._build_chain()

        self.vectorstore.save_local(save_path)
        logger.info(f"Ingested {len(docs)} articles into vector store.")


# Singleton instance
rag_pipeline = RAGPipeline()
