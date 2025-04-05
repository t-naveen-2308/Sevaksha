import os
import pickle
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from .gemini_llm import GeminiLLM


def load_schemes_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_path = os.path.join(
        project_root, "backend", "sevaksha_app", "static", "data", "schemes.txt"
    )
    with open(data_path, "r") as file:
        return file.read()


def load_vector_store():
    with open("vectorstore.pkl", "rb") as f:
        return pickle.load(f)


def create_qa_chain():
    schemes_data = load_schemes_data()

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    texts = text_splitter.split_text(schemes_data)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)

    llm = GeminiLLM()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=False,
    )
