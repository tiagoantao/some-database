# from rich import print
import sqlparse


query1 = "CREATE TABLE users (id INT, name VARCHAR(100))"
query2 = "SELECT * FROM users"

query = query1
p = sqlparse.parse(query)

stmt = p[0]

# print(stmt.get_type())


def parse(statement_text: str):
    p = sqlparse.parse(statement_text)

    stmt = p[0]
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
