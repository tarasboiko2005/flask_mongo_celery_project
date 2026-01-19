from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.rag.vector_store import get_vectorstore
from app.rag.embeddings import get_llm


def query_history(question: str) -> str:
    vectorstore = get_vectorstore()
    llm = get_llm()
    document_chain = create_stuff_documents_chain(llm)

    retrieval_chain = create_retrieval_chain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        combine_docs_chain=document_chain
    )

    result = retrieval_chain.invoke({"input": question})

    return result["answer"]
