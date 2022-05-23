from ariadne import QueryType, make_executable_schema
from ariadne.asgi import GraphQL

import random
import string
import time

type_defs = """
    type Query {
        test_lists(
            length: Int!
        ): Result!
    }

    type Result {
        length: Int!
        time_spent: Float!
        int_list: [Int!]
        float_list: [Float!]
        string_list: [String!]
    }
"""

query = QueryType()


@query.field("test_lists")
def resolve_test_lists(_, info, length):
    start_time = time.time()

    int_list = [random.randint(1, 30) for i in range(length)]

    float_list = [random.uniform(1.0, 30.0) for i in range(length)]

    sample_string = "pqrstuvwxy"
    string_list = [
        "".join((random.choice(sample_string)) for x in range(10))
        for i in range(length)
    ]

    return {
        "length": length,
        "int_list": int_list,
        "time_spent": time.time() - start_time,
        "float_list": float_list,
        "string_list": string_list,
    }


schema = make_executable_schema(type_defs, [query])

app = GraphQL(schema, debug=True)
