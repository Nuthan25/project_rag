import os
from typing import List, Tuple
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI as OpenAIClient
from dotenv import load_dotenv
from file_manager import FileManager
import os

# Load environment variables
load_dotenv()

from langchain_community.vectorstores import Chroma


class DeleteAgent:
    """Agent for deleting files and their data from the database"""

    def __init__(self, chroma_path: str = "chroma", metadata_path: str = "file_metadata.json"):
        self.chroma_path = chroma_path
        self.metadata_path = metadata_path
        self.file_manager = FileManager(metadata_path)
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def delete_file_by_number(self, number: str) -> str:
        """Delete a file and its data by number (1-based index)"""
        try:
            # Get file ID from number
            files = list(self.file_manager.get_all_files().items())
            try:
                index = int(number) - 1
                if 0 <= index < len(files):
                    file_id = files[index][0]
                else:
                    return f"Invalid file number: {number}. Use 'list' to see available files."
            except ValueError:
                return f"Invalid file number: {number}. Please provide a valid number."

            # Get file info
            file_info = self.file_manager.get_file_info(file_id)
            if not file_info:
                return f"File ID not found: {file_id}"

            # Delete from Chroma database
            if os.path.exists(self.chroma_path):
                db = Chroma(persist_directory=self.chroma_path, embedding_function=self.embedding_function)
                # Use the correct method to get and delete documents
                # First, get all documents with matching file_id metadata
                results = db.get(where={"file_id": file_id})

                if results and results.get("ids"):
                    # Delete the documents using their IDs
                    db.delete(ids=results["ids"])
                    print(f"Deleted {len(results['ids'])} document chunks from vector database")
                else:
                    print("No documents found in vector database for this file")

            # Delete from metadata (updates file_metadata.json)
            filename = file_info['filename']
            del self.file_manager.metadata[file_id]
            self.file_manager._save_metadata()  # Save changes to file_metadata.json

            return f"Successfully deleted file: {filename} (ID: {file_id})"

        except Exception as e:
            return f"Error deleting file: {str(e)}"


class FileLoaderAgent:
    """Agent for loading and processing PDF and text files"""

    def __init__(self, chroma_path: str = "chroma"):
        self.chroma_path = chroma_path
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def process_file(self, file_path: str, file_id: str) -> Tuple[bool, str]:
        """Process PDF or text file and store in vector database"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_ext == '.txt':
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                return False, f"Unsupported file type: {file_ext}"

            documents = loader.load()
            for doc in documents:
                doc.metadata["file_id"] = file_id
                doc.metadata["file_type"] = file_ext[1:]  # Remove dot

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                add_start_index=True,
            )
            chunks = text_splitter.split_documents(documents)
            self._save_to_chroma(chunks)

            return True, f"Successfully processed {file_ext[1:]} file! Created {len(chunks)} chunks."

        except Exception as e:
            return False, f"Error processing file: {str(e)}"

    def _save_to_chroma(self, chunks: List[Document]):
        """Save chunks to Chroma database"""
        if os.path.exists(self.chroma_path):
            db = Chroma(persist_directory=self.chroma_path, embedding_function=self.embedding_function)
            db.add_documents(chunks)
        else:
            db = Chroma.from_documents(
                chunks, self.embedding_function, persist_directory=self.chroma_path
            )
        # Removed db.persist() as Chroma auto-persists since 0.0.4x


class QueryAgent:
    """Agent for querying the vector database"""

    def __init__(self, chroma_path: str = "chroma"):
        self.chroma_path = chroma_path
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.client = OpenAIClient(
            base_url="https://openrouter.ai/api/v1/",
            api_key=os.getenv('API_KEY', 'sk-or-v1-0e9acbfc-74565bc9b7073deeb3a7d091648366beac2e0a3080ece9ec1b2fe958')
        )

    def query_database(self, query: str, file_id: str) -> str:
        """Query the vector database for a specific file"""
        try:
            if not os.path.exists(self.chroma_path):
                return "No documents loaded yet. Please load a file first."

            db = Chroma(persist_directory=self.chroma_path, embedding_function=self.embedding_function)
            results = db.similarity_search_with_relevance_scores(
                query,
                k=3,
                filter={"file_id": file_id}
            )

            if not results:
                return "No relevant information found for your question.Try rephrasing or asking about something else."

            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            prompt = f"""
            Answer the question based only on the following context:

            {context_text}

            ---

            Answer the question based on the above context: {query}
            """
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-30b-a3b:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512
            )
            response_text = completion.choices[0].message.content

            sources = [f"Source: {os.path.basename(doc.metadata.get('source', 'Unknown'))}" for doc, _ in results]
            return f"{response_text}\n\nSources:\n {', '.join(set(sources))}"

        except Exception as e:
            return f"Error while searching: {str(e)}"