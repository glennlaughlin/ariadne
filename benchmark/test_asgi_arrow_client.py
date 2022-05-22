import requests
import pyarrow as pa
import pyarrow.flight
import time
import json
import argparse

asgi_server = 'http://127.0.0.1:8000/graphql/'
arrow_flight_server = 'grpc://127.0.0.1:8815'

def run_benchmarks(length):
    query = {"query": "query {test_lists(length: " + length + ") {length int_list float_list string_list}}"}
    start_time = time.time()
    response = requests.post(asgi_server, json=query)
    total_time = time.time() - start_time
    print("------------------------")
    print("ASGI Fetch Time for " + length + " records:" + str(total_time))
    my_data = response.json()
    total_time = time.time() - start_time
    print("ASGI Convert JSON to Dictionary Total Time:" + str(total_time))
    print("first 100 Ints")
    print(my_data['data']['test_lists']['int_list'][0:100])
    print("------------------------")


    client = pa.flight.connect(arrow_flight_server)
    start_time = time.time()
    reader = client.do_get(ticket=pyarrow.flight.Ticket(json.dumps(query)))
    total_time = time.time() - start_time
    print("------------------------")
    print("Arrow Flight Fetch Time for " + length + " records:" + str(total_time))
    pyarrow_table = reader.read_all()
    my_data = pa.Table.to_pylist(pyarrow_table)[0]
    print("Arrow Flight Convert Arrow to Dictionary Total Time:" + str(total_time))
    print("first 100 Ints")
    print(my_data['data']['test_lists']['int_list'][0:100])
    print("------------------------")

if __name__ == "__main__":
    parser =  argparse.ArgumentParser(description="Run Test")
    parser.add_argument("-l", "--length", help="number of records to generate")
    args = parser.parse_args()
    run_benchmarks(args.length)


