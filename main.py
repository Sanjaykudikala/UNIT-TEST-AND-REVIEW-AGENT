import os
import argparse
import json
import subprocess
import re
import time
import shutil
from agents.graph import app
from ingestion.chunker import parse_and_chunk_repo
from ingestion.vector_store import store_chunks, query_context
from agents.scout import scout_target_file
from agents.injector import inject_code_change
from core.config import settings

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_modified_files(repo_path):
    try:

        result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True, cwd=repo_path)
        files = result.stdout.splitlines()

        result_staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, cwd=repo_path)
        files.extend(result_staged.stdout.splitlines())
        unique_files = list(set(os.path.join(repo_path, f) for f in files if f.endswith('.java')))
        return [f for f in unique_files if os.path.exists(f)]
    except Exception: return []

def get_file_diff(repo_path, file_path):
    try:
        rel_path = os.path.relpath(file_path, start=repo_path)
        result = subprocess.run(['git', 'diff', rel_path], capture_output=True, text=True, cwd=repo_path)
        return result.stdout
    except Exception: return ""

def main():
    parser = argparse.ArgumentParser(description="AI Code Agents - Senior PR Suite")
    parser.add_argument("--repo", help="Path to the Java repository")
    parser.add_argument("--output", default="./output", help="Output root directory")
    args = parser.parse_args()

    repo_path_input = args.repo
    if not repo_path_input:
        repo_path_input = input("Enter Java repository path: ").strip()

    if not repo_path_input:
        return

    repo_path = os.path.abspath(repo_path_input.replace('"', '').replace("'", ""))
    if not os.path.exists(repo_path):
        print(f"Error: Path '{repo_path}' not found.")
        return

    ensure_dir(args.output)
    repo_name = os.path.basename(repo_path)
    if not repo_name: repo_name = os.path.basename(os.path.dirname(repo_path))

    repo_output_dir = os.path.join(args.output, repo_name)
    ensure_dir(repo_output_dir)
    test_dir = os.path.join(repo_output_dir, "tests")
    ensure_dir(test_dir)

    chunks = parse_and_chunk_repo(repo_path)
    if chunks:
        store_chunks(chunks)

    modified_files = get_modified_files(repo_path)

    if not modified_files:
        target_file = scout_target_file(repo_path)
        if target_file:
            inject_code_change(target_file)
            modified_files = get_modified_files(repo_path)
        else:
            return

    if not modified_files:
        return

    for file_path in modified_files:
        rel_path = os.path.relpath(file_path, start=repo_path)
        print(f"Processing: {rel_path}")

        with open(file_path, "r", encoding="utf-8") as f: code_full = f.read()
        file_diff = get_file_diff(repo_path, file_path)

        state = {
            "code_input": code_full,
            "file_diff": file_diff,
            "file_path": rel_path,
            "context": [],
            "requirements": {},
            "review_output": {},
            "test_output": ""
        }

        try:
            state = app.invoke(state)
        except Exception as e:
            print(f"Error: {e}")
            continue

        with open(os.path.join(repo_output_dir, "review.json"), "w", encoding="utf-8") as f:
            json.dump(state["review_output"], f, indent=2)

        test_file = os.path.join(test_dir, f"{os.path.basename(file_path).replace('.java', 'Test.java')}")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(state["test_output"])

    print(f"Done. Results saved to: {repo_output_dir}")

if __name__ == "__main__":
    main()
