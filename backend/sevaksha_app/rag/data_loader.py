from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os


def load_schemes_data(file_path="schemes.txt"):
    """Reads and splits schemes-related data into smaller chunks."""
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = text_splitter.split_text(text)

    return [Document(page_content=chunk) for chunk in chunks]


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_path = os.path.join(
        project_root, "sevaksha_app", "static", "data", "schemes.txt"
    )
    docs = load_schemes_data(data_path)
    print(f"Loaded {len(docs)} document chunks from schemes data.")
