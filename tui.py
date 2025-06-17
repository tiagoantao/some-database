from rich.pretty import Pretty
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static, TextArea

from some import execute_statement
from some.engine import SomeNone, SomeSelectResult


class SomeApp(App):
    CSS = """
    Vertical {
        align: center middle;
    }
    Static#top {
        border: round white;
        height: 80%;
        padding: 0 1;
        margin: 1 0;
    }
    Input#input {
        border: round white;
        height: 20%;
        padding: 0 1;
        margin: 1 0;
    }
    """

    BINDINGS = [("ctrl+enter", "execute_statement", "Execute statement")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("", id="top")
            yield TextArea(id="input")
        yield Footer()

    def action_execute_statement(self) -> None:
        top = self.query_one("#top", Static)
        my_input = self.query_one("#input", TextArea).text
        try:
            result = execute_statement(my_input)
        except Exception as e:
            # dealing with flismy parser
            top.update(f"Error: {e}")
            return
        match type(result):
            case _ if isinstance(result, SomeNone):
                top.update("Executed")
            case _ if isinstance(result, SomeSelectResult):
                top.update(Pretty(result))
            case _:
                top.update(f"Unknown result type: {type(result)}")


if __name__ == "__main__":
    SomeApp().run()
