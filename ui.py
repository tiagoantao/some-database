import streamlit as st
from rich.console import Console

from some import execute_statement
from some.engine import SomeNone, SomeSelectResult


def rich_to_html(renderable) -> str:
    console = Console(record=True)
    console.print(renderable)
    return console.export_html(inline_styles=True)


def some_app() -> None:
    st.set_page_config(layout="wide")
    st.title("Some Database")
    with st.sidebar:
        st.header("Navigation")
    st.write("Welcome to Some Database")
    if "text" not in st.session_state:
        st.session_state["text"] = ""
    user_input = st.text_input("SQL input", "")
    if user_input:
        try:
            result = execute_statement(user_input)

            match type(result):
                case _ if isinstance(result, SomeNone):
                    st.session_state["text"] = "Done"
                case _ if isinstance(result, SomeSelectResult):
                    st.session_state["text"] = result
                case _:
                    st.session_state["text"] = f"Unknown result type: {type(result)}"
        except ValueError as e:
            st.session_state["text"] = f"Error: {e}"
    st.markdown("### Result")
    st.html(rich_to_html(st.session_state["text"]))


if __name__ == "__main__":
    some_app()
