import socket
import requests
import re
import threading

def main():
    # Define socket host and port
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 8080

    # Create a server socket
    # Using TCP socket as it is more reliable in communication and best suits our purpose
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # To prevent the port already in usage error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1000)
    print('Listening on port %s ...' % SERVER_PORT)
    while True:    
        # Wait for client connections
        client_connection, client_address = server_socket.accept()
        thread=threading.Thread(target=manage_clients,args=(client_connection, client_address))
        thread.start()
        print(f"Active connections: {threading.activeCount()-1}")


def manage_clients(client_connection,client_address):
    connected=True
    while connected:
        print(f"New connection : {client_address}")
        # Get the client request
        request = client_connection.recv(1024).decode()
        response=''
        if len(request)==0:
            break
            
        print(request)
        print()

        ''' 
        The request from the browser will be of the form

        GET / HTTP/1.1
        Host: 127.0.0.1:8080
        Connection: keep-alive
        sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
        sec-ch-ua-mobile: ?0
        sec-ch-ua-platform: "Windows"
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Purpose: prefetch
        Sec-Fetch-Site: none
        Sec-Fetch-Mode: navigate
        Sec-Fetch-User: ?1
        Sec-Fetch-Dest: document
        Accept-Encoding: gzip, deflate, br
        Accept-Language: en-US,en;q=0.9


        '''
        # getting the HTTP Request Method (POST,GET and DELETE)
        print('REQUEST')
        print(request.split('\n')[0].split()[0])

        # getting the End Point (POST,GET and DELETE)
        print('END POINT')
        print(request.split('\n')[0].split()[1])

        end_point=request.split('\n')[0].split()[1]
        request_type=request.split('\n')[0].split()[0]
        
        """
        Test cases to be verified:

            ["/google", "POST", "405"],
            ["/google", "DELETE", "405"],
            ["/google", "OPTIONS", "405"],
            ["/multiply", "POST", "400"],
            ["/multiply", "GET", "405"],
            ["/database.php", "DELETE", "403"],
            ["/database.php", "GET", "405"],    
            ["/", "POST", "405"],
            ["/index.html", "POST", "405"],
            ["/favicon.ico", "GET", "404"]
        """


        # Handling Requests to non existent end points(404)
        if end_point=='/favicon.ico' and request_type=='GET':
            response = 'HTTP/1.0 404 NON_EXISTENT_END_POINT\n\n'+''
        
        
        # Handling wrong HTTP Requests(405)
        if end_point=='/google' and request_type=='POST':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/google' and request_type=='DELETE':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/google' and request_type=='OPTIONS':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/multiply' and request_type=='GET':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/database.php' and request_type=='GET':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/' and request_type=='POST':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'
        if end_point=='/index.html' and request_type=='POST':
            response = 'HTTP/1.0 405 WRONG_HTTP_METHOD\n\n'


        # 1. GET / → Returns a simple HTML page.
        # 3. GET /index.html → Returns the same html page
        if (end_point=='/' or end_point=='/index.html') and request_type=='GET' :
            filename='index.html'
            try:
                fin = open(filename)
                content = fin.read()
                fin.close()
                response = 'HTTP/1.0 200 OK\n\n' + content
            except FileNotFoundError:
                response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'

        # 4. DELETE /database.php?data=all → Always returns a 403 Forbidden error response
        if end_point=='/database.php' and request_type=="DELETE":
            response = 'HTTP/1.0 403 FORBIDDEN ERROR\n\nNo Access'
        
        #5. GET /google → Permanent redirect 301 to google.com
        if end_point=="/google" and request_type=="GET":
            r=requests.get("https://www.google.com")
            print('google resp')
            response = 'HTTP/1.0 301 Moved Permanently\n\n'+r.text
            
        #2. POST /multiply → Returns the product of a and b sent as form-encoded data
        if request_type=='POST' and end_point=='/multiply':
            print(end_point)
            print(request.split('\n')[21])
            #number1=12&number2=34
            nrequest=request.split('\n')[21]
            n1=nrequest.split('&')[0].split('=')[1]
            n2=nrequest.split('&')[1].split('=')[1]

            #using regex to check if the submitted numbers were integers or not
            res_n1 = re.match("[-+]?\\d+$", n1)
            res_n2 = re.match("[-+]?\\d+$", n2)

            # case -1 : if the numbers submitted were empty,return 0 as product
            if request.split('\n')[21]=='number1=&number2=':
                res_n1,res_n2='',''
                n1,n2=0,0
                res=n1*n2
                print(res)
                response = 'HTTP/1.0 200 OK\n\n' + str(res)
            
            # case -2 : if the both the numbers submitted were not integer,return 400 as status code
            if res_n1 is None and res_n2 is None:
                res='Cannot multiply!please check if both inputs are integers'
                response = 'HTTP/1.0 400 WRONG_INPUT\n\n' + str(res)
            
            # case -3 : if the one of the numbers submitted was not integer,return 400 as status code
            if res_n1 is None and res_n2 is not None:
                res='Cannot multiply!please check if both inputs are integers'
                response = 'HTTP/1.0 400 WRONG_INPUT\n\n' + str(res)
            
            # case -4 : if the one of the numbers submitted was not integer,return 400 as status code
            if res_n1 is not None and res_n2 is None:
                res='Cannot multiply!please check if both inputs are integers'
                response = 'HTTP/1.0 400 WRONG_INPUT\n\n' + str(res)

            # case -5 : if both the numbers submitted were integer,return 200 as status code along with
            # their product say(n1*n2) and display on the page
            if res_n1 is not None and res_n2 is not None and request.split('\n')[21]!='number1=&number2=':
                n1=int(n1)
                n2=int(n2)
                print(n1)
                print(n2)
                res=n1*n2
                print(res)
                response = 'HTTP/1.0 200 OK\n\n' + str(res)
        # Send HTTP response
        client_connection.send(response.encode())
    #close the connection        
    client_connection.close()



    

if __name__=='__main__':
    main()
# Close socket
#server_socket.close()
