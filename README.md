# AI Code Agents: Senior-Level PR Review & Test Generation

This project implements a professional, context-aware AI agent system designed to perform automated code reviews and unit test generation for Java codebases, strictly following the assignment requirements.

## 🚀 One-Command "Zero-Config" Automation

The system is now fully automated. You only need to provide the repository path. It will automatically:
1.  **Detect Git Changes**: Identifies modified files via `git diff`.
2.  **Auto-Load Requirements**: Scans the repo for `README.md` or `requirements.txt` to use as the functional spec.
3.  **Smart Context**: Uses Regex to find class names in your edits and pulls the **Top-3 context chunks** from the vector DB.

### 🛠️ Setup & Usage

#### 1. Installation
```powershell
pip install -r requirements.txt
```

#### 2. Configuration (Environment)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_api_key_here
```

#### 3. Running the Workflow
To perform a complete, senior-level review and test generation:
```powershell
python main.py --repo "C:/path/to/your/java/project"
```

## 🏗️ Project Scope & Justification

*   **WebGoat (Security Analysis)**: Maintaining a perfect real-world baseline for testing the **AI Review Agent's Security Capabilities** (SQL Injection, XSS, etc.).
*   **Apache Commons Text (Complexity)**: Testing the agent's **Architectural Awareness** and **Performance Analysis** capabilities.
*   **JUnit 5 & Mockito**: The core testing stack identified and used for all generated tests.

## 🦾 AI Agent Architecture

### Agent 1: Code Review Agent (Senior Architect)
Performs a holistic, context-aware PR review matching the assignment's JSON schema.
### Agent 2: Unit Test Generation Agent (SDET Agent)
Generates high-coverage tests using the **Arrange-Act-Assert (AAA)** pattern and **Mockito** dependencies.

## 📊 Outputs
- **`output/assignment_review_report.json`**: The official senior-level review report.
- **`output/generated_tests/`**: JUnit 5 test files for modified classes.

---
*Developed for the AI Agent Engineering Assignment.*
