import os

def scout_target_file(repo_path: str):

    java_files = []
    for root, _, files in os.walk(repo_path):

        rel_root = os.path.relpath(root, repo_path).lower().split(os.sep)
        if any(exc in rel_root for exc in ["test", "tests", "build", ".git", "target", "bin", "out"]):
            continue

        for file in files:

            if file.endswith(".java") and "Test" not in file and "package-info" not in file:
                java_files.append(os.path.join(root, file))

    if not java_files:
        return None

    priority_order = ["Controller", "Service", "Repository", "Model"]
    for pos in priority_order:
        for f in java_files:
            if pos in f:
                return f

    return java_files[0]
