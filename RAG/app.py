import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check for API keys
if not groq_api_key:
    st.error("GROQ_API_KEY not found in environment variables")
    st.stop()
if not openai_api_key:
    st.error("OPENAI_API_KEY not found in environment variables")
    st.stop()

# Display image only if it exists
if os.path.exists("RAG.png"):
    st.image("RAG.png", width=200)

st.title("Document Question Answer")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="Llama3-8b-8192"
)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
Please answer the question strictly from the provided context.

Context:
{context}

Question: {question}

Answer:
""")

def format_docs(docs):
    """Format retrieved documents into a single string"""
    return "\n\n".join(doc.page_content for doc in docs)

def vector_embedding():
    """Create vector embeddings from PDF documents"""
    if "vector_store" not in st.session_state:
        with st.spinner("Creating vector embeddings..."):
            # Check if PDF directory exists
            if not os.path.exists("./ed_pdf"):
                st.error("PDF directory './ed_pdf' not found. Please create it and add PDF files.")
                return False
            
            try:
                # Initialize embeddings
                st.session_state.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
                
                # Load documents
                st.session_state.loader = PyPDFDirectoryLoader("./ed_pdf")
                st.session_state.docs = st.session_state.loader.load()
                
                # Check if documents were loaded
                if not st.session_state.docs:
                    st.error("No PDF documents found in './ed_pdf' directory.")
                    return False
                
                # Split documents into chunks
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, 
                    chunk_overlap=200
                )
                st.session_state.chunks = splitter.split_documents(st.session_state.docs)
                
                # Create vector store
                st.session_state.vector_store = FAISS.from_documents(
                    st.session_state.chunks,
                    st.session_state.embeddings
                )
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                if "cryptography" in error_msg.lower():
                    st.error("⚠️ Your PDFs are encrypted. Please install cryptography library:")
                    st.code("pip install cryptography>=3.1", language="bash")
                    st.info("After installing, restart the application.")
                else:
                    st.error(f"Error loading PDFs: {error_msg}")
                return False
                
    return True

# User input
user_question = st.text_input("Enter your question:")

# Button to create embeddings
if st.button("Create Vector Database"):
    if vector_embedding():
        st.success(f"Vector DB Ready! Processed {len(st.session_state.chunks)} document chunks.")

# Process query
if user_question:
    if "vector_store" not in st.session_state:
        st.warning("Please create the vector database first by clicking 'Create Vector Database'")
    else:
        with st.spinner("Searching for answer..."):
            # Create retriever
            retriever = st.session_state.vector_store.as_retriever(
                search_kwargs={"k": 4}  # Retrieve top 4 most relevant chunks
            )
            
            # Build RAG chain using LCEL (LangChain Expression Language)
            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            # Get response and retrieved documents
            start = time.time()
            
            # Get the answer
            answer = rag_chain.invoke(user_question)
            
            # Get the retrieved documents separately for display
            retrieved_docs = retriever.invoke(user_question)
            
            delta = time.time() - start
            
            # Display results
            st.subheader("AI Response")
            st.write(answer)
            st.info(f"Response time: {delta:.2f} seconds")
            
            # Show relevant chunks
            with st.expander("View Relevant Document Chunks"):
                for i, doc in enumerate(retrieved_docs, 1):
                    st.markdown(f"**Chunk {i}:**")
                    st.markdown(f"""
                    <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        {doc.page_content}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show metadata if available
                    if doc.metadata:
                        st.caption(f"Source: {doc.metadata.get('source', 'Unknown')}")