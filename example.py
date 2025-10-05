import os
import shutil
import logging as log
import shutil

from rich import print

from some import engine, parse
from some.engine import DATABASE_PATH

queries = [
    "CREATE TABLE users (id INT, name VARCHAR(100))",
    "INSERT INTO users (id, name) VALUES (1, 'Jane Doe')",
    "INSERT INTO users (id, name) VALUES (2, 'John Doe')",
    "SELECT * FROM users",
    "SELECT * FROM users WHERE id = 1",
    "CREATE TABLE ex_2 (f2 VARCHAR(20))",
    "SHOW TABLES",
    "DESCRIBE TABLE users",
]

if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    shutil.rmtree(engine.DATABASE_PATH)
    os.makedirs(engine.DATABASE_PATH)
    for query in queries:
        print(f"Executing query: {query}")
        parsed_statement = parse.parse(query)
        print(f"Parsed statement:\n{type(parsed_statement)}")
        print(parsed_statement)
        result = engine.execute(parsed_statement)
        if type(result) is engine.SomeSelectResult:
            print()
            print(result.column_names)
            for row in result.rows:
                print(row)
        else:
            print(result)
        print()
