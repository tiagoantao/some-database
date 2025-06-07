import csv
from pathlib import Path

from pydantic import BaseModel

from .parse import SomeCreateTable, SomeInsertInto, SomeSelect, SomeSQLStatement

DATABASE_PATH = Path.cwd() / "DB"
DATABASE_PATH.mkdir(parents=True, exist_ok=True)


class SomeResultBase(BaseModel):
    pass


class SomeNone(SomeResultBase):
    pass


class SomeSelectResult(SomeResultBase):
    column_names: list[str]
    rows: list[list[str]]


SomeResult = SomeNone | SomeSelectResult


def create_table(table_definition: SomeCreateTable) -> None:
    with open(DATABASE_PATH / f"{table_definition.name}.csv", "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(map(lambda col: col.name, table_definition.columns))


def insert_into(insert_definition: SomeInsertInto) -> None:
    with open(DATABASE_PATH / f"{insert_definition.table_name}.csv", "a") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(insert_definition.values)


# vvv not a great return type...
def select(select_definition: SomeSelect) -> tuple[list[str], list[list[str]]]:
    with open(DATABASE_PATH / f"{select_definition.table_name}.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)  # get the header
        rows = [row for row in reader]
        return header, rows


def execute(statement: SomeSQLStatement) -> SomeResult:
    # Sadly mypy doesn't understand the match statement yet
    if isinstance(statement, SomeCreateTable):
        create_table(statement)
        return SomeNone()
    elif isinstance(statement, SomeInsertInto):
        insert_into(statement)
        return SomeNone()
    elif isinstance(statement, SomeSelect):
        column_names, rows = select(statement)
        return SomeSelectResult(column_names=column_names, rows=rows)
