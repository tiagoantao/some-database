import logging as log
from enum import Enum

from pydantic import BaseModel

# from rich import print
import sqlparse
from sqlparse.sql import Function, Identifier, Parenthesis, Statement, Token


# Explain the prefix Some


class SomeSQLType(Enum):
    INT = "INT"
    VARCHAR = "VARCHAR"


class SomeStatementType(Enum):
    CREATE_TABLE = "CREATE TABLE"
    SELECT = "SELECT"
    INSERT = "INSERT"


class SomeColumnDefinition(BaseModel):
    name: str
    type: SomeSQLType
    length: int | None = None


class SomeCreateTable(BaseModel):
    columns: list[SomeColumnDefinition]
    name: str


class SomeSelect(BaseModel):
    name: str


class SomeSQLStatement(BaseModel):
    type: SomeStatementType
    statement: SomeCreateTable | SomeSelect


query1 = "CREATE TABLE users (id INT, name VARCHAR(100))"
query2 = "SELECT * FROM users"

query = query1
# print(stmt.get_type())

def get_varchar_size(token: Function) -> int:
    tokens = token.tokens
    if str(tokens[0].value).upper() != "VARCHAR":
        raise ValueError(f"Expected VARCHAR got {tokens[0].value}")
    return token.tokens[1].tokens[1].value

def parse_column_definitions(parenthesis: Parenthesis) -> list[SomeColumnDefinition]:
    column_definitions = []
    tokens = [token for token in parenthesis.tokens if not token.is_whitespace]
    column_name = ""
    for j, token in enumerate(tokens[1:-1]):
        if j % 3 == 0:
            if token.ttype is not None:
                raise ValueError(f"Expected column name, got {token.ttype} {token}")
            column_name = token.value
        elif j % 3 == 1:
            if isinstance(token, Function):
                size = get_varchar_size(token)
                column_definitions.append(SomeColumnDefinition(name=column_name, type=SomeSQLType.VARCHAR, length=size))
            elif isinstance(token, Token):
                if token.value.upper() == "INT":
                    column_definitions.append(SomeColumnDefinition(name=column_name, type=SomeSQLType.INT))
                else:
                    raise ValueError(f"Expected INT or VARCHAR, got {token.value}")
            else:
                raise ValueError(f"Expected column type, got {token.ttype} {token}")

    return column_definitions


def parse_create_table(stmt: Statement) -> SomeSQLStatement:
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    table_name = None
    column_definitions = []
    for i, token in enumerate(tokens):
        #print(i, token.ttype, token, type(token))
        if i == 1:
           if str(token.ttype) != "Token.Keyword" or token.value != "TABLE":
               raise ValueError("Expected 'TABLE' keyword after 'CREATE'")
        elif i == 2:
            #print(i, token.ttype, token, type(token))
            if not isinstance(token,Identifier):
                raise ValueError("Expected table name after 'CREATE TABLE'")
            table_name = token.value
        if isinstance(token, Parenthesis):
            column_definitions = parse_column_definitions(token)
    if table_name is None:
        raise ValueError("Table name not found in CREATE TABLE statement")
    if len(column_definitions) == 0:
        raise ValueError("Column definitions not found in CREATE TABLE statement")
    create_table = SomeCreateTable(name=table_name, columns=column_definitions)
    return create_table


def parse(statement_text: str) -> SomeSQLStatement:
    p = sqlparse.parse(statement_text)

    stmt = p[0]
    statement_type_text = stmt.get_type()
    if statement_type_text == "CREATE":
        return parse_create_table(stmt)
    else:
        print(1, statement_type_text)
        return
    indent = 1
    for token in stmt.tokens:
        if token.ttype is None:
            print(">" * indent, token)
            indent += 2
            for subtoken in token.tokens:
                print("#" * indent, subtoken.ttype, subtoken, sep=" ")
            indent -= 2
        else:
            print("$" * indent, token.ttype, token.value)

if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    print(parse(query))
