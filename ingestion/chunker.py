import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_java_files(repo_path: str):
    java_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def parse_and_chunk_repo(repo_path: str):
    print(f"Scanning for Java files in: {repo_path}")
    java_files = get_java_files(repo_path)
    print(f"Found {len(java_files)} Java files.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\nclass ", "\npublic ", "\nprivate ", "\n\n", "\n", " ", ""]
    )

    docs = []
    print("Chunking files...")
    for file_path in java_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = splitter.split_text(content)
            for idx, chunk in enumerate(chunks):
                relative_path = os.path.relpath(file_path, start=repo_path)
                docs.append({
                    "id": f"{relative_path}_{idx}",
                    "text": chunk,
                    "metadata": {"file_path": relative_path, "chunk_idx": idx}
                })
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")

    print(f"Total chunks generated: {len(docs)}")
    return docs
