import math
import grpc
from concurrent import futures

# Import the generated classes from the .proto compilation
from calculator_pb2 import (
    ArithmeticOperation,
    CalculateResponse
)
import calculator_pb2_grpc


class CalculatorService(calculator_pb2_grpc.CalculatorServicer):
    """A class to implement the service defined in the .proto file"""
    def Calculate(self, request, context):
        """Override this method's implementation in the base class"""
        if request.operation == ArithmeticOperation.ADD:
            res = sum(request.nums)
        elif request.operation == ArithmeticOperation.MULTIPLY:
            res = math.prod(request.nums)
        else:
            # The context allows us to set the status code for the response
            # abort() here ends the request and sets the status code to 
            # NOT_FOUND when the method gets an unexpected operation
            context.abort(
                grpc.StatusCode.NOT_FOUND, "Arithmetic Operation not found"
            )
        
        return CalculateResponse(result=res)


def run_server():
    """Run the server."""
    # Create a gRPC server with a thread pool of workers to handle requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add the CalculatorService to the server to handle RPCs
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorService(), server)

    # Listen on port 50051 and accept connections without encryption (i.e., no TLS/SSL)
    server.add_insecure_port('[::]:50051')

    # Start the server
    server.start()
    print("gRPC server running on port 50051...")

    server.wait_for_termination()


if __name__ == "__main__":
    run_server()
