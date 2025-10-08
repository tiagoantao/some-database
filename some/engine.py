import csv
import os
import tomllib
from pathlib import Path

import toml
from pydantic import BaseModel

from .parse import (
    SomeCreateTable,
    SomeDescribeTable,
    SomeInsertInto,
    SomeSelect,
    SomeShowTables,
    SomeSQLStatement,
)

DATABASE_PATH = Path.cwd() / "DB"
DATABASE_PATH.mkdir(parents=True, exist_ok=True)


class SomeResultBase(BaseModel):
    pass


class SomeNone(SomeResultBase):
    pass


class SomeSelectResult(SomeResultBase):
    column_names: list[str]
    rows: list[list[str]]


class SomeShowTablesResult(SomeResultBase):
    table_names: list[str]


class SomeDescribeTableResult(SomeResultBase):
    columns: dict[str, dict]  #  Not correct XXX


SomeResult = (
    SomeNone | SomeSelectResult | SomeShowTablesResult | SomeDescribeTableResult
)


def _create_table_to_toml(stmt: SomeCreateTable) -> dict:
    return {
        "columns": [
            {
                "name": col.name,
                "type": str(col.type),
                **({"length": col.length} if col.length is not None else {}),
            }
            for col in stmt.columns
        ]
    }


def create_table(table_definition: SomeCreateTable) -> None:
    with open(DATABASE_PATH / f"{table_definition.name}.csv", "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(map(lambda col: col.name, table_definition.columns))
    with open(DATABASE_PATH / f"{table_definition.name}.toml", "w") as f:
        toml.dump(_create_table_to_toml(table_definition), f)


def insert_into(insert_definition: SomeInsertInto) -> None:
    with open(DATABASE_PATH / f"{insert_definition.table_name}.csv", "a") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(insert_definition.values)


def select(select_definition: SomeSelect) -> SomeSelectResult:
    with open(DATABASE_PATH / f"{select_definition.table_name}.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)  # get the header
        rows = [row for row in reader]
        return SomeSelectResult(
            column_names=header,
            rows=rows,
        )


def show_tables() -> SomeShowTablesResult:
    table_names = [p.stem for p in DATABASE_PATH.glob("*.csv")]
    return SomeShowTablesResult(table_names=table_names)


def describe_table(describe_definition: SomeDescribeTable) -> SomeDescribeTableResult:
    transformed_dict = {}
    with open(DATABASE_PATH / f"{describe_definition.table_name}.toml", "rb") as f:
        data = tomllib.load(f)
        column_list = data["columns"]
        for column in column_list:
            column_attributes = column.copy()

            try:
                name = column_attributes.pop("name")
            except KeyError:
                print(f"Warning: Column definition missing 'name' key: {column}")
                continue
            transformed_dict[name] = column_attributes
    return SomeDescribeTableResult(columns=transformed_dict)


def execute(statement: SomeSQLStatement) -> SomeResult:
    # Sadly mypy doesn't understand the match statement yet
    os.makedirs(DATABASE_PATH, exist_ok=True)
    if isinstance(statement, SomeCreateTable):
        create_table(statement)
        return SomeNone()
    elif isinstance(statement, SomeInsertInto):
        insert_into(statement)
        return SomeNone()
    elif isinstance(statement, SomeSelect):
        select_result = select(statement)
        return select_result
    elif isinstance(statement, SomeShowTables):
        return show_tables()
    elif isinstance(statement, SomeDescribeTable):
        return describe_table(statement)
