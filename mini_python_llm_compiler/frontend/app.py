"""Streamlit UI for the Mini Python LLM Compiler."""
from __future__ import annotations
import os
import textwrap
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Mini Python LLM Compiler", layout="wide")

st.title("Mini Python LLM Compiler")
st.caption("Generate code with an LLM, then validate it with a tiny compiler built on PLY.")

prompt = st.text_area(
    "Prompt",
    value="Write a tiny program that greets and adds two numbers.",
    height=120,
)

col1, col2 = st.columns(2)

if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""


def call_backend(path: str, payload: dict):
    url = f"{BACKEND_URL}{path}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:  # pragma: no cover - UI helper
        st.error(f"Backend error: {exc}")
        return None


with col1:
    if st.button("Generate Code", type="primary"):
        resp = call_backend("/generate_code", {"prompt": prompt})
        if resp:
            st.session_state.generated_code = resp.get("code", "")

    st.subheader("Generated Code")
    st.code(st.session_state.generated_code or "// click Generate to get code", language="python")

with col2:
    st.subheader("Compile / Analyze")
    code_input = st.text_area(
        "Code to compile",
        value=st.session_state.generated_code,
        height=260,
    )
    if st.button("Compile Code"):
        resp = call_backend("/compile_code", {"code": code_input})
        if resp:
            syntax_errors = resp.get("syntax_errors", [])
            semantic_errors = resp.get("semantic_errors", [])
            st.write("**Syntax Errors**")
            st.write(syntax_errors or "None")
            st.write("**Semantic Errors**")
            st.write(semantic_errors or "None")

st.divider()

st.write("Sample program you can paste:")
example = textwrap.dedent(
    """
    x = 5
    y = x + 3
    if y > 6:
        print("Large")
    else:
        print("Small")
    """
)
st.code(example, language="python")
