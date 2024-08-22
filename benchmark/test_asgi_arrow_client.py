import requests
import pyarrow as pa
import pyarrow.flight
import time
import json
import argparse


def run_benchmarks(length, server):

    asgi_server = "http://" + server + ":8000/graphql/"
    arrow_flight_server = "grpc://" + server + ":8815"

    query = {
        "query": "query {test_lists(length: "
        + length
        + ") {length time_spent int_list float_list string_list}}"
    }
    start_time = time.time()
    response = requests.post(asgi_server, json=query)
    total_time = time.time() - start_time
    print("------------------------")
    print("ASGI Fetch Time for " + length + " records:" + str(total_time))
    my_data = response.json()
    total_time = time.time() - start_time
    print("ASGI Convert JSON to Dictionary Total Time:" + str(total_time))
    print("------------------------")
    print(
        "Server side data generation time:"
        + str(my_data["data"]["test_lists"]["time_spent"])
    )
    print(
        "Actual ASGI minus server side:"
        + str(total_time - my_data["data"]["test_lists"]["time_spent"])
    )
    print("------------------------")
    print("first 100 Ints")
    print(my_data["data"]["test_lists"]["int_list"][0:100])
    print("")
    client = pa.flight.connect(arrow_flight_server)
    start_time = time.time()
    reader = client.do_get(ticket=pyarrow.flight.Ticket(json.dumps(query)))
    total_time = time.time() - start_time
    print("------------------------")
    print("Arrow Flight Fetch Time for " + length + " records:" + str(total_time))
    pyarrow_table = reader.read_all()
    my_data = pa.Table.to_pylist(pyarrow_table)[0]
    print("Arrow Flight Convert Arrow to Dictionary Total Time:" + str(total_time))
    print("------------------------")
    print(
        "Server side data generation time:"
        + str(my_data["data"]["test_lists"]["time_spent"])
    )
    print(
        "Actual Arrow Flight minus server side:"
        + str(total_time - my_data["data"]["test_lists"]["time_spent"])
    )
    print("------------------------")
    print("first 100 Ints")
    print(my_data["data"]["test_lists"]["int_list"][0:100])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Test")
    parser.add_argument(
        "-l", "--length", required=True, help="number of records to generate"
    )
    parser.add_argument("-s", "--server", required=True, help="server host")
    args = parser.parse_args()
    run_benchmarks(args.length, args.server)
