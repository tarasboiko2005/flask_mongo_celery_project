from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the provided context to answer the question."),
    ("human", "Question: {input}\n\nContext:\n{context}")
])
