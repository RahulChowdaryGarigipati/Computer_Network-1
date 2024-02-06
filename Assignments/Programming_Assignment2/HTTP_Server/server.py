import socket
import threading
import time
import urllib
import urllib.parse
from http_objects import Request, Response
import queue
import multiprocessing


# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the port 8080
serversocket.bind(('localhost', 8080))
serversocket.listen()
# function to connect to the server
def connect():
    # queue up to many requests
    serversocket.listen() 
    print("Server is listening on port 8080")

    while True:
        # establish a connection
        clientsocket,addr = serversocket.accept()
        print("Got a connection from %s" % str(addr))
    
# function to build a thread to handle the incoming connections
def build_thread():
    while True:
        # create a thread to handle the incoming connections
        clientThread = threading.Thread(target=connect)
        clientThread.start()
        time.sleep(2)


def handle_multiply(request) -> Response:
    # handle multiply only if the request method is POST and request has a query string
    if request.method == "POST": 
        if request.query_string or request.body:
            # parse the query string or body
            if request.query_string:
                query_string = request.query_string
            else:
                query_string = request.body

            query_string_parameters = urllib.parse.parse_qs(query_string)
            a = query_string_parameters["a"][0]
            b = query_string_parameters["b"][0]
            # check if a and b are integers
          
            return Response(200, None, f"{int(a) * int(b)}")
            
        else:
            return Response(400, None, "Bad Request")
    else:
        # send the response
        return Response(405, None,  "Method Not Allowed")

def handle_database(request) -> Response:
    # Handle database only if the request method is DELETE and request has a query string
    if request.method == "DELETE":
        return Response(403, None, "Forbidden")
    else:
        return Response(405, None, "Method Not Allowed")

def handle_home(request) -> Response:
    # Handle home only if the request method is GET and path is / or /index.html
    if request.method == "GET" and (request.path == "/" or request.path == "/index.html"):
        # send the response
        return Response(200, None, "Hello World!")
    else:
        # send the response
        return Response(405, None, "Method Not Allowed")

def handle_google(request) -> Response:
    # Handle google only if the request method is GET and path is /google
    if request.method == "GET":
        # send the response
        #"Location: https://www.google.com"
        return Response(301, {"Location" : "https://google.com"}, None)
    else:
        # send the response
        return Response(405, None, "Method Not Allowed")

def handle_404(request) -> Response:
    # Handle 404
    return Response(404, None, "Not Found")


def handle_request(tup):
    clientsocket, address = tup
    try:    
        data_chunk = []

        while True:
            data = clientsocket.recv(2048)

            # process partial data chunks and extract content length and end of header
            if not data:
                break
                #continue
            else:
                # Append the received data to the data_chunk list
                data_chunk.append(data.decode("utf-8"))

                # wrap for exception handling
                try:
                    #TODO: Handle partial data chunks which cannot be decoded

                    # Convert the data_chunk list to a string
                    data_string = "".join(data_chunk)

                    # check for end of header and no content length
                    
                    # check if content length is in the data string                    
                    if "Content-Length" in data_string:
                        content_length = int(data_string.split("Content-Length: ")[1].split("\r\n")[0])
                    # extract the content length and end of header
                        end_of_header = data_string.find("\r\n\r\n")
                    
                    # if end of header is not found, continue to receive data
                        if end_of_header == -1:
                            continue
                        else:
                        # extract the body
                            body = data_string[end_of_header + 4:]
                        # check if the body is complete
                            if len(body) == content_length:
                                break
                    elif "\r\n\r\n" in data_string:
                        break
                    
                except Exception as e:
                    #continue
                    raise Exception(e)
        
        # decode the data

        request_raw = "".join(data_chunk)
        # if the request_raw is empty, throw an exception and continue
        if not request_raw:
            raise Exception("Empty Request")
        
        # Init request obj
        request = Request(request_raw)
    
        # Handle according to the path 
        if request.path == "/" or request.path == "/index.html":
            response = handle_home(request)
        elif request.path == "/google":
            response = handle_google(request)
        elif request.path == "/multiply":
            response = handle_multiply(request)
        elif request.path == "/database.php":
            response = handle_database(request)
        else:
            response = handle_404(request)

        # send the response
        clientsocket.send(response.get_response().encode())
        clientsocket.close()
    except Exception as e:
        clientsocket.send(Response(500, None, repr(e)).get_response().encode())
        clientsocket.close()


# store request in a queue
request_queue = queue.Queue()

# set number of threads to half the number of cores
num_threads = 4 * multiprocessing.cpu_count() // 2

# wait for connections 
while True:
   
    # Handle the incoming connections event
    clientsocket, address = serversocket.accept()

    # store connection in a queue and handle it in a thread
    request_queue.put((clientsocket, address))


    # processing event
    #for i in range(num_threads):
        # create a thread to handle the incoming connections

    # create no of threads equal to pending tasks in the queue and max of num_threads
    for i in range(min(request_queue.qsize(), num_threads)):
        clientThread = threading.Thread(target=handle_request, args=(request_queue.get(),))
        clientThread.start()

            

# close all connections
# serversocket.close()
