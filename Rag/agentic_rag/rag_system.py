import re
from typing import Optional
from file_manager import FileManager
from agents import FileLoaderAgent, QueryAgent, DeleteAgent
import os

class ConversationalRAGSystem:
    """Main conversational RAG system"""
    def __init__(self):
        self.file_manager = FileManager()
        self.loader_agent = FileLoaderAgent()
        self.query_agent = QueryAgent()
        self.delete_agent = DeleteAgent()
        print("RAG Assistant initialized! Type 'hi' or 'help' to see what I can do.")

    def _detect_intent(self, user_input: str) -> tuple[str, str]:
        """Detect user intent from input"""
        user_input = user_input.lower().strip()

        if any(word in user_input for word in ['hi', 'hello', 'hey', 'help']):
            return "help", user_input

        if any(phrase in user_input for phrase in ['load', 'process', 'add file', 'upload']):
            return "load_file", user_input

        if any(phrase in user_input for phrase in ['list', 'show files', 'what files', 'data in db']):
            return "list_files", user_input

        if any(phrase in user_input for phrase in ['delete', 'remove', 'erase']):
            return "delete_file", user_input

        if re.match(r'^\d+\s+', user_input):
            return "query_specific", user_input

        return "unknown", user_input

    def _extract_file_path(self, user_input: str) -> Optional[str]:
        """Extract file path from user input"""
        patterns = [
            r'["\']([^"\']+\.(?:pdf|txt))["\']',
            r'(\S+\.(?:pdf|txt))',
            r'(?:load|process|add)\s+(.+\.(?:pdf|txt))',
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_file_number(self, user_input: str) -> tuple[Optional[str], str]:
        """Extract file number and query from user input"""
        match = re.match(r'^(\d+)\s+(.+)$', user_input, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).strip()
        # Handle delete command without query
        delete_match = re.match(r'^(?:delete|remove|erase)\s+(\d+)$', user_input, re.IGNORECASE)
        if delete_match:
            return delete_match.group(1), ""
        return None, user_input

    def _get_file_id_by_number(self, number: str) -> Optional[str]:
        """Get file ID by number (1-based index)"""
        files = list(self.file_manager.get_all_files().items())
        try:
            index = int(number) - 1
            if 0 <= index < len(files):
                return files[index][0]
        except ValueError:
            pass
        return None

    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        intent, original_input = self._detect_intent(user_input)
        print(intent)
        print(original_input)

        if intent == "help":
            return self._help_response()

        elif intent == "load_file":
            file_path = self._extract_file_path(user_input)
            if file_path:
                return self._load_file(file_path)
            return "Please provide a file path. Example: load C:\\Users\\NUTHAN R\\Downloads\\AI.pdf"

        elif intent == "list_files":
            return self._list_files()

        elif intent == "delete_file":
            number = self._extract_file_number(original_input)[0]
            if number:
                return self.delete_agent.delete_file_by_number(number)
            return "Please provide a file number to delete. Example: delete 1"

        elif intent == "query_specific":
            number, query = self._extract_file_number(user_input)
            print("number", number)
            print("query", query)
            if number and query:
                file_id = self._get_file_id_by_number(number)
                if file_id:
                    return self._query_specific_file(file_id, query)
                return f"Invalid file number: {number}. Use 'list' to see available files."
            return "Please use format: [number] your question (e.g., '1 what is AI')"

        return "Type 'help' to see what I can do."

    def _help_response(self) -> str:
        """Generate help response"""
        loaded_files = len(self.file_manager.get_all_files())
        return f"""
RAG Assistant - Here's what I can do:
1. Load PDF or text files: "load C:\\path\\to\\file.pdf"
2. List loaded files: "list"
3. Ask about a specific file: "[number] your question" (e.g., "1 what is AI")
4. Delete a file: "delete [number]" (e.g., "delete 1")
Current status: {loaded_files} files loaded
"""

    def _load_file(self, file_path: str) -> str:
        """Load and process a file"""
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        file_ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)

        if file_ext not in ['.pdf', '.txt']:
            return f"Only PDF and TXT files are supported. You provided: {file_ext}"

        file_id = self.file_manager.register_file(file_path, file_ext[1:])
        success, message = self.loader_agent.process_file(file_path, file_id)

        if success:
            self.file_manager.update_file_status(file_id, "processed")
            return f"Data loaded successfully. File: {filename}, Unique ID: {file_id}"
        return f"Failed to load file: {message}"

    def _list_files(self) -> str:
        """List all loaded files"""
        files = self.file_manager.get_all_files()
        if not files:
            return "No files loaded yet. Use 'load [file_path]' to add a file."

        file_list = ["Loaded files:"]
        for index, (file_id, info) in enumerate(files.items(), 1):
            file_list.append(f"{index}. {info['filename']} (ID: {file_id})")
        return "\n".join(file_list)

    def _query_specific_file(self, file_id: str, query: str) -> str:
        """Query a specific file"""
        file_info = self.file_manager.get_file_info(file_id)
        if not file_info:
            return f"File ID not found: {file_id}"

        if not query.strip():
            return f"Please ask a specific question about {file_info['filename']}."

        result = self.query_agent.query_database(query, file_id)
        return result

    def chat(self):
        """Start the conversational interface"""
        print("\n" + "=" * 60)
        print("RAG Assistant - Conversational Mode")
        print("=" * 60)
        print("Type 'exit' to quit, 'help' for assistance\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye!")
                    break
                if not user_input:
                    continue
                response = self.process_input(user_input)
                print(f"Assistant: {response}\n")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}\n")

def main():
    """Main function to run the conversational RAG system"""
    system = ConversationalRAGSystem()
    system.chat()

if __name__ == "__main__":
    main()