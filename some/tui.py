from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static, TextArea


class SomeApp(App):
    CSS = """
    Vertical {
        align: center middle;
    }
    Static#top {
        border: round white;
        height: 80%;
        width: 60;
        content-align: center middle;
        margin: 1 0;
    }
    Input#input {
        border: round white;
        height: 20%;
        width: 60;
        padding: 0 1;
        margin: 1 0;
    }
    """

    BINDINGS = [("ctrl+enter", "execute_statement", "Execute statement")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("Hello, world!", id="top")
            yield TextArea(id="input")
        yield Footer()

    def action_execute_statement(self) -> None:
        top = self.query_one("#top", Static)
        my_input = self.query_one("#input", TextArea)
        top.update(my_input.text)


if __name__ == "__main__":
    SomeApp().run()
