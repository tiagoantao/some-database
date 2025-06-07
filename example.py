import logging as log

from rich import print

from some import engine, parse

query1 = "CREATE TABLE users (id INT, name VARCHAR(100))"
query2 = "INSERT INTO users (id, name) VALUES (1, 'Jane Doe')"
query3 = "SELECT * FROM users"

if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    for query in (query1, query2, query3):
        parsed_statement = parse.parse(query)
        print(f"Parsed statement: {type(parsed_statement)}")
        print(parsed_statement)
        result = engine.execute(parsed_statement)
        if type(result) is engine.SomeSelectResult:
            print()
            print(result.column_names)
            for row in result.rows:
                print(row)
        print()
