from urllib.parse import parse_qs

class Request:
    def __init__(self, request):
        self.request = request
        self.request_line = request.splitlines()[0]
        self.method = self.request_line.split()[0]
        self.path = self.request_line.split()[1]
        self.version = self.request_line.split()[2]
        self.headers = request.splitlines()[1:]
        self.body = request.splitlines()[-1]

        # handle no query string
        if "?" not in self.path:
            self.query_string = None
        else:
            self.query_string = self.path.split("?")[1]
            self.query_string_parameters = parse_qs(self.query_string)
        
    def get_request_method(self):
        return self.method

    def get_request_path(self):
        return self.path

    def get_request_version(self):
        return self.version

    def get_request_headers(self):
        return self.headers

    def get_request_body(self):
        return self.body

    def get_request(self):
        return self.request

class Response:
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body
    

    def get_status_based_on_code(self):
        if self.status_code == 200:
            return "OK"
        elif self.status_code == 301:
            return "Moved Permanently"
        elif self.status_code == 400:
            return "Bad Request"
        elif self.status_code == 403:
            return "Forbidden"
        elif self.status_code == 404:
            return "Not Found"
        elif self.status_code == 405:
            return "Method Not Allowed"
        else:
            return "Internal Server Error"

    def get_response(self) -> str:
        # embed body in html

        if self.headers:
            # handle header dictionary
            header_string = ""
            for key, value in self.headers.items():
                header_string += f"{key}: {value}\n"
            
            return f"HTTP/1.1 {self.status_code} {self.get_status_based_on_code()}\n{header_string}\n<html> <body> {self.body} </body> </html>"

        return f"HTTP/1.1 {self.status_code} {self.get_status_based_on_code()}\n\n<html> <body> {self.body} </body> </html>"
