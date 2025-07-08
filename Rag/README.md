# RAG (Retrieval-Augmented Generation) Project

A comprehensive implementation of RAG system with both simple and agentic approaches for document querying and conversation.

## 🚀 Project Overview

This project provides two different RAG implementations:
- **Agentic RAG**: Interactive conversational interface with file management
- **Simple RAG**: Basic document processing and querying

## 📁 Project Structure

```
rag/
├── agentic_rag/
│   ├── agents.py           # Core agents for file operations and querying
│   ├── file_manager.py     # File metadata management
│   └── rag_system.py       # Main conversational interface
├── only_rag/
│   ├── data/
│   │   └── books/          # Place your PDF/TXT files here
│   ├── create_database.py  # Database creation script
│   └── query_data.py       # Query execution script
└── requirements.txt        # Python dependencies
```

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd rag
pip install -r requirements.txt
```

### 2. Get Your Free API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Create a free account
3. Generate your API key
4. Create a `.env` file in the project root:

```env
API_KEY=your_openrouter_api_key_here
```

### 3. Choose Your RAG Implementation

## 🤖 Agentic RAG (Recommended)

### Features
- Interactive conversational interface
- File management (load, list, delete)
- Multi-file support with unique IDs
- Persistent storage with Chroma vector database

### Usage

```bash
cd agentic_rag
python rag_system.py
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `load "path/to/file.pdf"` | Load PDF or text file | `load "C:\docs\AI.pdf"` |
| `list` | Show all loaded files | `list` |
| `[number] question` | Ask about specific file | `1 what is AI?` |
| `delete [number]` | Delete a file | `delete 1` |
| `help` | Show help message | `help` |
| `exit` | Quit the application | `exit` |

### Example Session

```
============================================================
RAG Assistant - Conversational Mode
============================================================
Type 'exit' to quit, 'help' for assistance

You: load "C:\Users\NUTHAN R\Downloads\AI.pdf"
Assistant: Data loaded successfully. File: AI.pdf, Unique ID: c83a9ea6

You: list
Assistant: Loaded files:
1. AI.pdf (ID: c83a9ea6)

You: 1 what is ai
Assistant: Artificial Intelligence (AI) is the branch of computer science that aims to mimic human behavior to assist humans in achieving better performance in science and technology...

Sources: Source: AI.pdf
```

## 📚 Simple RAG

### Step-by-Step Usage

1. **Load your files**
   - Place your PDF/TXT files in `only_rag/data/books/` directory
   - Example: Copy `AI.pdf` to `only_rag/data/books/AI.pdf`

2. **Create the database**
   ```bash
   cd simple_rag
   python create_database.py
   ```
   - This will process all files in the `data/books/` folder
   - Wait for processing to complete

3. **Query your documents**
   ```bash
   python query_data.py
   ```
   - This will start an interactive query session
   - Type your questions and get answers from your documents

### Example Simple RAG Session

```
$ python query_data.py
Enter your question (or 'quit' to exit): what is artificial intelligence?
Answer: Artificial Intelligence (AI) is the branch of computer science that aims to mimic human behavior...

Enter your question (or 'quit' to exit): quit
```

## ⚠️ Important Notes

### Loading Time
- **Wait 10-15 seconds** after loading a file before querying
- The system needs time to process and embed documents

### Empty Responses
If you get empty responses:
1. Wait a bit longer after loading
2. Try asking the same question **2-3 times**
3. Rephrase your question
4. Check if the file was loaded correctly with `list`

### Supported File Types
- PDF files (`.pdf`)
- Text files (`.txt`)

## 🔧 Configuration

### Embedding Model
- Default: `sentence-transformers/all-MiniLM-L6-v2`
- Automatically downloaded on first use

### LLM Model
- Default: `qwen/qwen3-30b-a3b:free` (Free tier)
- Configurable in `agents.py`

### Chunk Settings
- Chunk size: 500 characters
- Overlap: 50 characters
- Similarity search: Top 3 results

## 🐛 Troubleshooting

### Common Issues

1. **"No documents loaded yet"**
   - Make sure you've loaded a file using `load "path/to/file"`
   - Wait 10-15 seconds after loading

2. **"No relevant information found"**
   - Try rephrasing your question
   - Ask 2-3 times (system sometimes needs multiple attempts)
   - Check if the topic exists in your document

3. **API Key Errors**
   - Verify your `.env` file has the correct API key
   - Check your OpenRouter.ai account balance/limits

4. **File Loading Errors**
   - Use absolute file paths
   - Ensure file exists and is readable
   - Check file format (PDF/TXT only)

### Performance Tips

- Keep document files under 10MB for optimal performance
- Use specific, focused questions for better results
- Wait for processing to complete before querying

## 📝 Dependencies

Key packages used:
- `langchain` - RAG framework
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `openai` - LLM API client
- `PyPDF2` - PDF processing
- `python-dotenv` - Environment variables

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available under the MIT License.

---

**Happy RAG-ing! 🎉**

For more questions or issues, please create an issue in the repository.