import os
import argparse
import json
import subprocess
import re
import time
import shutil
from agents.graph import app_review, app_test
from ingestion.chunker import parse_and_chunk_repo
from ingestion.vector_store import store_chunks, query_context
from core.config import settings

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_modified_files(repo_path):
    try:
        # Get unstaged changes
        result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True, cwd=repo_path)
        files = result.stdout.splitlines()
        # Get staged changes
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

def extract_class_names(text):
    pattern = re.compile(r'\b[A-Z][a-zA-Z0-9]+\b')
    matches = pattern.findall(text)
    excluded = {"String", "System", "Integer", "Exception", "Override", "Test", "List", "Map", "Set", "Optional"}
    return list(set(m for m in matches if m not in excluded))

def auto_find_requirements(repo_path):
    potential_names = ["requirements.txt", "my_reqs.txt", "README.md", "specification.md"]
    for name in potential_names:
        full_path = os.path.join(repo_path, name)
        if os.path.exists(full_path):
            return f"Auto-detected in {name}"
    return "No specific requirements file found."

def invoke_with_retry(app, name, state, max_retries=3):
    for attempt in range(max_retries):
        try:
            return app.invoke(state)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                wait_time = 30 * (attempt + 1)
                print(f"    [!] Rate limit reached. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                return None
    return None

def main():
    parser = argparse.ArgumentParser(description="AI Code Agents - Senior-Level PR Suite")
    parser.add_argument("--repo", help="Path to the Java repository")
    parser.add_argument("--output", default="./output", help="Output root directory")
    args = parser.parse_args()

    # Step 1: Resolve Repository Path (Frictionless)
    repo_path_input = args.repo
    if not repo_path_input:
        print("\n" + "="*50)
        print("  AI CODE AGENTS - SENIOR-LEVEL PR SUITE")
        print("="*50)
        repo_path_input = input("[*] Please enter the path to the Java repository: ").strip()

    if not repo_path_input:
        print("[!] Error: No repository path provided.")
        return

    repo_path = os.path.abspath(repo_path_input.replace('"', '').replace("'", ""))
    if not os.path.exists(repo_path):
        print(f"[!] Error: Path '{repo_path}' not found.")
        return

    # PERSISTENT OUTPUT: We do NOT delete the output folder anymore
    ensure_dir(args.output)
    repo_name = os.path.basename(repo_path)
    if not repo_name: repo_name = os.path.basename(os.path.dirname(repo_path))
    
    repo_output_dir = os.path.join(args.output, repo_name)
    ensure_dir(repo_output_dir)
    test_dir = os.path.join(repo_output_dir, "tests")
    ensure_dir(test_dir)

    print("\n" + "="*50)
    
    # [STEP 1] Data Ingestion
    print(f"[*] [STEP 1] DATA INGESTION: {repo_path}")
    chunks = parse_and_chunk_repo(repo_path)
    if chunks:
        store_chunks(chunks)
    
    # [STEP 2] Codebase Relationship Map
    print(f"[*] [STEP 2] VECTOR DATABASE (RAG) INITIALIZED")

    # [STEP 3] Local Git Diff
    print(f"[*] [STEP 3] DETECTING LOCAL GIT CHANGES...")
    modified_files = get_modified_files(repo_path)
    if not modified_files:
        print(f"[!] No changes found in {repo_name}. Workflow paused.")
        return
        
    reqs_status = auto_find_requirements(repo_path)
    print(f"    [+] Requirements Source: {reqs_status}")

    # Processing Loop
    print(f"[*] ANALYZING {len(modified_files)} MODIFIED FILE(S)...")
    for file_path in modified_files:
        rel_path = os.path.relpath(file_path, start=repo_path)
        print(f"\n--- Processing: {rel_path} ---")
        
        with open(file_path, "r", encoding="utf-8") as f: code_full = f.read()
        file_diff = get_file_diff(repo_path, file_path)
        class_names = extract_class_names(code_full)
        
        # [STEP 4] Context Shifting
        print(f"[*] [STEP 4] EXTRACTING CONTEXT CHUNKS FOR ANALYSIS...")
        context_sigs = ""
        for name in class_names[:5]:
            sigs = query_context(name, n_results=3)
            context_sigs += f"\nClass: {name} {{ {sigs} }}\n"

        # [STEP 5] Agent 1 Review
        print(f"[*] [STEP 5] AGENT 1: SENIOR CODE REVIEW INVOCATION...")
        review_state = {
            "code_input": file_diff if file_diff else code_full,
            "file_path": rel_path,
            "context": context_sigs,
            "requirements": reqs_status,
            "review_output": {}
        }
        res_review = invoke_with_retry(app_review, "Reviewer", review_state)
        if res_review:
            with open(os.path.join(repo_output_dir, "review.json"), "w", encoding="utf-8") as f:
                json.dump(res_review["review_output"], f, indent=2)

        # [STEP 6] Agent 2 Test Generation
        print(f"[*] [STEP 6] AGENT 2: UNIT TEST GENERATION INVOCATION...")
        test_state = {
            "code_input": code_full,
            "diff_content": file_diff,
            "context": context_sigs,
            "test_output": ""
        }
        res_test = invoke_with_retry(app_test, "QA", test_state)
        if res_test:
            test_file = os.path.join(test_dir, f"{os.path.basename(file_path).replace('.java', 'Test.java')}")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(res_test["test_output"])

    print("\n" + "="*50)
    print(f"WORKFLOW COMPLETED SUCCESSFULLY.")
    print(f" - Persistent Output: {repo_output_dir}")
    print("="*50)

if __name__ == "__main__":
    main()
