import os, glob
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.prompts import PromptTemplate
from utils import create_llm

class PDFQuery(BaseModel):
    question: str = Field(..., description="Question about the PDFs")
    top_k: int = 3
    llm_provider: str = Field(default="OpenRouter", description="LLM provider: OpenAI or OpenRouter")
    model_name: str = Field(default="minimax/minimax-m2:free", description="Model name to use")
    api_key: str = Field(..., description="API key for the selected provider")

def load_docs(folder="data/pdfs"):
    """Load documents from text files (instead of PDFs for simplicity)"""
    docs = []
    for fp in glob.glob(os.path.join(folder,"*.txt")):
        try:
            loader = TextLoader(fp)
            docs.extend(loader.load())
        except Exception as e:
            print(f"Error loading {fp}: {e}")
    return docs

def find_relevant_docs(query, top_k=3):
    """Find relevant documents using TF-IDF similarity"""
    docs = load_docs()
    if not docs:
        return []

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(docs)

    # Create TF-IDF vectors
    corpus = [doc.page_content for doc in texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus + [query])

    # Calculate similarity
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).ravel()

    # Get top similar documents
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    relevant_docs = []
    for idx in top_indices:
        relevant_docs.append(texts[idx])

    return relevant_docs

def answer_pdf(payload: PDFQuery):
    try:

        # Initialize LLM based on user selection
        llm = create_llm(payload.llm_provider, payload.model_name, payload.api_key)

        # Create custom prompt
        prompt_template = """
        You are a helpful assistant that answers questions based on the provided context from documents.

        Context from relevant documents:
        {context}

        Question: {question}

        Instructions:
        - Answer based only on the provided context
        - If the context doesn't contain enough information to answer the question, say so clearly
        - Cite specific parts of the documents when relevant
        - Keep your answer concise but comprehensive
        - Use bullet points if listing multiple items or steps

        Answer:
        """

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Get relevant documents using TF-IDF
        relevant_docs = find_relevant_docs(payload.question, payload.top_k)

        # Combine document content as context
        context = "\n\n".join([doc.page_content for doc in relevant_docs[:payload.top_k]])

        # Generate answer using LLM
        response = llm.invoke(PROMPT.format(context=context, question=payload.question))
        answer = response.content.strip()

        # Get source documents for citations
        citations = []
        for i, doc in enumerate(relevant_docs):
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            citations.append({
                "rank": i+1,
                "source": source,
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })

        return {
            "answer": answer,
            "citations": citations
        }

    except Exception as e:
        return {
            "answer": f"Error processing PDF query: {str(e)}. Please check your API key and try again.",
            "citations": []
        }
