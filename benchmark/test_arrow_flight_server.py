from ariadne import QueryType, make_executable_schema, graphql_sync
import pyarrow as pa
import pyarrow.flight

import random
import string
import asyncio
import json
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


class FlightServer(pyarrow.flight.FlightServerBase):
    def __init__(self, location="grpc://0.0.0.0:8815", **kwargs):
        super(FlightServer, self).__init__(location, **kwargs)
        self._location = location
        print("started server at: " + location)

    def do_get(self, context, ticket):
        query = ticket.ticket.decode("utf-8")
        query = json.loads(query)
        success, result = graphql_sync(schema, query)
        arrow_data = pa.Table.from_pylist([result])
        return pa.flight.RecordBatchStream(arrow_data)


if __name__ == "__main__":
    server = FlightServer()
    server.serve()
