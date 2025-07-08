import os
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate

CHROMA_PATH = "../chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Initialize the OpenAI-compatible client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('API_KEY', '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'),  # Make sure API_KEY is set in .env or environment
)

def main():
    # Ask the user for input
    query_text = input("Ask a question: ")

    # Load embeddings and vector database
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search for relevant content
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0:
        print("No relevant results found in the knowledge base.")
        return

    # Build prompt
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Call the LLM
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3-30b-a3b:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512
        )

        response_text = completion.choices[0].message.content
        sources = [doc.metadata.get("source", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {set(sources)}"
        print(formatted_response)

    except Exception as e:
        print(f"LLM call failed: {e}")

if __name__ == "__main__":
    main()