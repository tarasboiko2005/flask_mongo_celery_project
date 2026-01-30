from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from app.rag.vector_store import get_vectorstore
from app.rag.embeddings import get_llm
from app.rag.prompt import rag_prompt

llm = get_llm()

def query_history(question: str) -> str:
    vectorstore = get_vectorstore()
    document_chain = create_stuff_documents_chain(llm, rag_prompt)

    retrieval_chain = create_retrieval_chain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        combine_docs_chain=document_chain
    )

    result = retrieval_chain.invoke({"input": question})
    return result.get("output", "No answer found")