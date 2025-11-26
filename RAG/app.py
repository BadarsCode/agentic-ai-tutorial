import streamlit as st
import os
import time
from dotenv import load_dotenv

# Fixed imports for LangChain 1.1.0
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.chains import RetrievalQA 
# Optional: use OpenAI embeddings if GoogleGenerativeAIEmbeddings is not installed
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

st.image("RAG.png", width=200)
st.title("Document Question Answer")

# LLM instance
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Prompt template
prompt = ChatPromptTemplate.from_template(
    """
    Please answer the questions strictly based on the provided context.
    Ensure the response is accurate, concise, and directly addresses the question.
    <context>
    {context}
    </context>
    Question:
    {input}
    """
)

def vector_embedding():
    if "vector_store" not in st.session_state:
        # Use OpenAI embeddings if Google embeddings are not available
        st.session_state.embeddings = OpenAIEmbeddings()
        st.session_state.loader = PypdfDirectoryLoader("./ed_pdf")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(
            st.session_state.docs[:20]
        )
        st.session_state.vector_store = FAISS.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings
        )

prompt1 = st.text_input("Enter your question from any documents")
if st.button("Search"):
    vector_embedding()
    st.success("DB is Ready for queries")

if prompt1:
    # Fixed: use RetrievalQA instead of non-existent create_stuff_documents_chain
    retriever = st.session_state.vector_store.as_retriever()
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    start = time.process_time()
    response_text = retrieval_chain.run(prompt1)
    response_time = time.process_time() - start

    st.markdown("AI Response")
    st.success(response_text)
    st.write(f"Response time: {response_time:.2f} seconds")

    with st.expander("Show Similarity Results"):
        st.markdown("Below are the most relevant document chunks")
        for i, doc in enumerate(st.session_state.final_documents):
            st.markdown(f"""
            <style>
            .card{{
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            </style>
            <div class="card">
                <p>{doc.page_content}</p>
            </div>
            """, unsafe_allow_html=True)
