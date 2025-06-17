from enum import Enum

from pydantic import BaseModel

import sqlparse
from sqlparse.sql import Function, Identifier, Parenthesis, Statement, Token


class SomeSQLType(Enum):
    """
    An enumeration to define basic SQL types.

    Attributes
    ----------
    INT : str
        Represents an integer type in SQL.
    VARCHAR : str
        Represents a variable character string type in SQL.
    """
    INT = "INT"
    VARCHAR = "VARCHAR"


class SomeColumnDefinition(BaseModel):
    """
    Represents the definition of a SQL column.

    Attributes
    ----------
    name : str
        The name of the column.
    type : SomeSQLType
        The data type of the column.
    length : int or None
        The length of the column if applicable (e.g., VARCHAR).
    """
    name: str
    type: SomeSQLType
    length: int | None = None


class SomeSQLStatementBase(BaseModel):
    """
    Base class for SQL statements.

    Serves as a parent class for different types of SQL statements.
    """
    pass


class SomeCreateTable(SomeSQLStatementBase):
    """
    Represents a CREATE TABLE SQL statement.

    Attributes
    ----------
    columns : list of SomeColumnDefinition
        Definitions of the columns to be created.
    name : str
        Name of the table to be created.
    """
    columns: list[SomeColumnDefinition]
    name: str


class SomeInsertInto(SomeSQLStatementBase):
    """
    Represents an INSERT INTO SQL statement.

    Attributes
    ----------
    table_name : str
        Name of the table to insert into.
    column_names : list of str
        Names of the columns where values will be inserted.
    values : list
        Values to be inserted into the columns.
    """
    table_name: str
    column_names: list[str]
    values: list


class SomeSelect(SomeSQLStatementBase):
    """
    Represents a SELECT SQL statement.

    Attributes
    ----------
    table_name : str
        Name of the table to select from.
    """
    table_name: str


SomeSQLStatement = SomeCreateTable | SomeInsertInto | SomeSelect


def get_varchar_size(token: Function) -> int:
    """
    Extracts the size of a VARCHAR from a SQL Function token.

    Parameters
    ----------
    token : Function
        The SQL Function token representing VARCHAR.

    Returns
    -------
    int
        The size of the VARCHAR specified in the token.

    Raises
    ------
    ValueError
        If the token does not represent a VARCHAR.
    """
    tokens = token.tokens
    if str(tokens[0].value).upper() != "VARCHAR":
        raise ValueError(f"Expected VARCHAR got {tokens[0].value}")
    return token.tokens[1].tokens[1].value


def parse_column_definitions(parenthesis: Parenthesis) -> list[SomeColumnDefinition]:
    """
    Parses column definitions from a SQL Parenthesis token.

    Parameters
    ----------
    parenthesis : Parenthesis
        The SQL Parenthesis token containing column definitions.

    Returns
    -------
    list of SomeColumnDefinition
        A list of parsed column definitions.

    Raises
    ------
    ValueError
        If parsing encounters unexpected token types.
    """
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
                column_definitions.append(
                    SomeColumnDefinition(
                        name=column_name, type=SomeSQLType.VARCHAR, length=size
                    )
                )
            elif isinstance(token, Token):
                if token.value.upper() == "INT":
                    column_definitions.append(
                        SomeColumnDefinition(name=column_name, type=SomeSQLType.INT)
                    )
                else:
                    raise ValueError(f"Expected INT or VARCHAR, got {token.value}")
            else:
                raise ValueError(f"Expected column type, got {token.ttype} {token}")

    return column_definitions


def parse_create_table(stmt: Statement) -> SomeCreateTable:
    """
    Parses a CREATE TABLE SQL statement into a SomeCreateTable object.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    SomeCreateTable
        The parsed representation of the CREATE TABLE statement.

    Raises
    ------
    ValueError
        If the statement is not a valid CREATE TABLE statement.
    """
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    table_name = None
    column_definitions = []
    for i, token in enumerate(tokens):
        if i == 1:
            if str(token.ttype) != "Token.Keyword" or token.value != "TABLE":
                raise ValueError("Expected 'TABLE' keyword after 'CREATE'")
        elif i == 2:
            if not isinstance(token, Identifier):
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


def parse_insert_into_column_names(stmt: Statement) -> list[str]:
    """
    Parses the column names from an INSERT INTO SQL statement.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    list of str
        The list of column names specified in the INSERT INTO statement.
    """
    column_names = []

    for i, c_token in enumerate(stmt.tokens):
        if i == 1:
            tokens = [token for token in c_token.tokens if not token.is_whitespace]
            for j, c_token in enumerate(tokens):
                if j % 2 == 0:
                    column_names.append(c_token.value)
    return column_names


def parse_insert_into(stmt: Statement) -> tuple[str, list[str]]:
    """
    Parses an INSERT INTO SQL statement to extract table name and column names.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    tuple
        A tuple containing the table name and list of column names.
    """
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    table_name = ""
    column_names = []
    for j, token in enumerate(tokens):
        if j == 0:
            table_name = token.value
        else:
            column_names = parse_insert_into_column_names(token)
    return table_name, column_names


def parse_insert_values(stmt: Statement) -> list[str]:
    """
    Parses values from an INSERT SQL statement.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    list of str
        The list of values specified for insertion.
    """
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    column_names = []
    for j, token in enumerate(tokens):
        if j == 1:
            vtokens = [
                str(vtoken) for vtoken in token.tokens[1] if not vtoken.is_whitespace
            ]
            vtokens = [t.replace("'", "") for t in vtokens]
            column_names = vtokens[::2]
    return column_names


def parse_insert(stmt: Statement) -> SomeInsertInto:
    """
    Parses an INSERT SQL statement into a SomeInsertInto object.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    SomeInsertInto
        The parsed representation of the INSERT statement.
    """
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    do_into = False
    do_values = False
    table_name = ""
    column_names = []
    values = []
    for i, token in enumerate(tokens):
        if str(token.ttype) == "Token.Keyword" and token.value == "INTO":
            do_into = True
        elif do_into:
            table_name, column_names = parse_insert_into(token)
            do_into = False
            do_values = True
        elif do_values:
            values = parse_insert_values(token)
    return SomeInsertInto(
        table_name=table_name, column_names=column_names, values=values
    )


def parse_select(stmt: Statement) -> SomeSelect:
    """
    Parses a SELECT SQL statement into a SomeSelect object.

    Parameters
    ----------
    stmt : Statement
        The SQL statement to parse.

    Returns
    -------
    SomeSelect
        The parsed representation of the SELECT statement.
    """
    tokens = [token for token in stmt.tokens if not token.is_whitespace]
    return SomeSelect(table_name=tokens[3].value)


def parse(statement_text: str) -> SomeSQLStatement:
    """
    Parses a raw SQL statement into its corresponding model representation.

    Parameters
    ----------
    statement_text : str
        The raw SQL statement as a string.

    Returns
    -------
    SomeSQLStatement
        The parsed representation of the SQL statement.

    Raises
    ------
    ValueError
        If the statement type is not supported.
    """
    p = sqlparse.parse(statement_text)

    stmt = p[0]
    statement_type_text = stmt.get_type()
    if statement_type_text == "CREATE":
        return parse_create_table(stmt)
    elif statement_type_text == "INSERT":
        return parse_insert(stmt)
    elif statement_type_text == "SELECT":
        return parse_select(stmt)
    else:
        raise ValueError(f"Still not processing {statement_type_text}")
