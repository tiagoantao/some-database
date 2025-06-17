from . import engine, parse


def execute_statement(stmt: str) -> engine.SomeResult:
    """
    Parse and execute a SQL statement.

    Parameters
    ----------
    stmt : str
        The SQL statement to execute.

    Returns
    -------
    engine.SomeResult
        The result of the execution.
    """
    parsed_statement = parse.parse(stmt)
    return engine.execute(parsed_statement)
