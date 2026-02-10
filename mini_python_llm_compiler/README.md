# Mini Python LLM Compiler

Generate Python code with an LLM, then validate it with a tiny compiler (lexer + parser + semantic analyzer) built using PLY.

## Project Layout
```
mini_python_llm_compiler/
├── compiler/
│   ├── lexer.py          # PLY lexer with indentation handling
│   ├── parser.py         # PLY yacc grammar producing a small AST
│   ├── semantic.py       # Symbol-table based semantic checks
│   └── compiler.py       # Orchestrates parse + semantics
├── llm/
│   └── llm_generator.py  # OpenAI (or offline) code generator
├── backend/
│   └── api.py            # FastAPI endpoints: /generate_code, /compile_code
├── frontend/
│   └── app.py            # Streamlit UI to drive the workflow
├── requirements.txt
└── README.md
```

## Supported Language Features
- Variable assignment: `x = 5`, `y = x + 2`
- Arithmetic: `+ - * /` with parentheses
- Comparisons: `> < >= <= == !=`
- Strings: single or double quoted
- Print: `print(expr)`
- If / else with indentation
- Comments with `#`

## Compiler Phases
1. **Lexing**: Converts source to tokens, including `INDENT/DEDENT` to model Python blocks.
2. **Parsing**: Builds a minimal AST (assignments, prints, if/else, binops, literals, names).
3. **Semantic Analysis**: Symbol table tracks defined variables; flags any use before assignment.

## Running Locally (Windows, Python 3.10+)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Start the API
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Launch the Streamlit UI
```bash
streamlit run frontend/app.py
```

Set `BACKEND_URL` env var if your API is not on `http://localhost:8000`.

### LLM API Key (optional)
Set `OPENAI_API_KEY` to enable real LLM generation. Without it, a deterministic fallback produces example code so everything remains runnable.

## Sample Programs
```python
x = 5
y = x + 3
if y > 6:
    print("Large")
else:
    print("Small")
```

```python
# Simple comparison
name = "Ada"
if name == "Ada":
    print("Hello, Ada")
```

## Error Examples
- Syntax: `x =` → reported by the parser
- Semantic: `print(total)` (when `total` was never assigned) → reported as undefined variable

## Notes
- Indentation uses spaces (tabs count as 4 spaces for this lexer).
- The language subset intentionally excludes imports, functions, and loops to keep the grammar concise.
