from http.server import BaseHTTPRequestHandler, HTTPServer
import requests


# The handler for the HTTP requests.
class RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Get the message from data processing and send it to the client
        data_request = requests.get('http://localhost:8081')

        if(data_request.status_code != 200):
            # An error has occurred
            message = "Error."
        else:
            message = data_request.text

        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return


def run():
    print('starting server...')

    # Server settings
    # Choose port 8082, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', 8082)
    httpd = HTTPServer(server_address, RequestHandler)
    print('running server...')
    httpd.serve_forever()


run()