import streamlit as st
import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import create_retrieval_chain
from langchain_community.vectorstores import FAISS


load_dotenv()
groq_api_ke = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

st.image("RAG.png", width=200)
st.title(" document question answer")

llm = ChatGroq(groq_api_key = groq_api_key, model_name="Llama3-8b-8192")


prompt = ChatPromptTemplate.form_template(
    """
        please answer the questions strictly based on the provided context.
        Ensure the response is accurate , concise and directly addresses the question.
        <context>
        {context}
        </context>
        questionL
        {input}

    """
)

def vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        st.session_state.loader = PypdfDirectoryLoader("./ed_pdf")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(
            st.session_state.docs[:20]
        )
        st.session_state.vector_store = FAISS.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings
        )
prompt1 =st.text_input("Enter your question from any documents")
if st.button("Search"):
    vector_embedding()
    st.success("DB is Ready for queries")

if prompt1:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start= time.process_time()
    response = retrieval_chain.invoke({"input": prompt1})
    response_time = time.process_time() - start

    st.markdown("AI Response")
    st.success(response['text'])
    st.write(f"Response time: {response_time:2f} seconds")
    

    with st.expander("Show Similarity Results"):
        st.markdown("below are the most relavent documents chunks")
        for i, doc in enumerate(response.get("context",[])):
            st.markdown(f"""
            <style>
            .center{
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                margin-top: 20px;
            }
            stButton>button{
                color: white;
                background-color: #4caf50;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }
            stButton>button:hover{
                background-color: #45a049;
            }
            .card{
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            } 
            </style>
            <div class="card">
                <p> {doc.page_content}</p>
            </div>
            """, unsafe_allow_html=True)
