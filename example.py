import logging as log

from rich import print

from some import engine, parse

queries = [
    "CREATE TABLE users (id INT, name VARCHAR(100))",
    "INSERT INTO users (id, name) VALUES (1, 'Jane Doe')",
    "SELECT * FROM users",
    "SHOW TABLES",
]

if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    for query in queries:
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
