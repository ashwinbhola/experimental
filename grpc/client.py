import grpc

# Import the generated classes for messages and the stub
from calculator_pb2 import CalculateRequest, ArithmeticOperation
from calculator_pb2_grpc import CalculatorStub


def run():
    # Create a channel to connect to the server at localhost:50051
    with grpc.insecure_channel('localhost:50051') as channel:
        # Create a stub (client) for the Calculator service
        calculator_stub = CalculatorStub(channel)

        # Create a request message with nums to add
        request = CalculateRequest(
            operation=ArithmeticOperation.ADD, nums=[1, 0, 5]
        )
        print(f"Request in binary format: {request.SerializeToString()}")
        # Call the remote Add method on the server
        response = calculator_stub.Calculate(request)
        # Print the result received from the server
        print(f"Add result: {response.result}")

        # Create a request message with nums to multiply
        request = CalculateRequest(operation="MULTIPLY", nums=[1, 0, 5])
        # Call the remote Add method on the server
        response = calculator_stub.Calculate(request)
        # Print the result received from the server
        print(f"Add result: {response.result}")

        try:
            # Create a request message with nums to Subtract
            request = CalculateRequest(operation="Subtract", nums=[1, 0, 5])
            # Call the remote Add method on the server
            response = calculator_stub.Calculate(request)
            # Print the result received from the server
            print(f"Add result: {response.result}")
        except Exception as exc:
            print(f"Request failed with exception: {exc}")


if __name__ == '__main__':
    run()