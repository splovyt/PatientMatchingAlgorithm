from controllers.ControllerFacade import ControllerFacade
from http.server import BaseHTTPRequestHandler
from typing import Sequence, Mapping
import json
import re
import traceback


class GeneralRequestHandler(BaseHTTPRequestHandler):
    """
    Receives requests and sends them to the right specific handler.
    Also contains general methods for handling requests.
    """

    def do_GET(self):
        self.__handle_request()

    def do_POST(self):
        self.__handle_request()

    def do_PUT(self):
        self.__handle_request()

    def do_OPTIONS(self):
        print("Asked options.")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

    def send_json_response(self, json_object):
        """
        Sends a JSON response, not an error.
        :param json_object: should be an object that can be serialized
        to json, like a dict or list
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        reply = json.dumps(json_object)

        self.wfile.write(bytes(reply, "utf8"))

    def get_url_for_endpoint(self, endpoint: str) -> str:
        return {'href': self.server.base_url_with_port + endpoint}

    @property
    def self_url(self):
        return self.server.base_url_with_port + self.path

    @property
    def controller_facade(self) -> ControllerFacade:
        return self.server.controller_facade

    @property
    def input_json_object(self):
        input_str = self.rfile.read(int(self.headers['Content-Length'])).decode('utf8')
        print("Decoding JSON:")
        print(input_str)
        return json.loads(input_str)

    def end_headers(self):
        """
        Add own headers.
        """
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def __handle_request(self):
        try:
            print(self.command + " to " + self.__endpoint)

            specific_handler =\
                self.server.get_handler_for_endpoint(self.__endpoint)

            if specific_handler is None:
                self.__send_endpoint_not_found()
            else:
                try:
                    if self.command == 'GET':
                        specific_handler.get(self)
                    elif self.command == 'POST':
                        specific_handler.post(self)
                    elif self.command == 'PUT':
                        specific_handler.put(self)
                except AttributeError as e:
                    print(str(traceback.format_exc()))
                    self.__send_method_not_supported()

        except BaseException as e:
            self.__handle_general_exception(traceback.format_exc())

    def send_syntax_error(self, message: str):
        print("Client sent request with syntax error.")
        print(message)
        self.send_error(400, "Syntax error: " + message)

    def send_resource_not_found(self):
        print("Nonexistent resource requested.")
        self.send_error(404, "The specified resource was not found.")

    def check_names_per_nomenclature_structure(self, names_per_nomenclature) -> bool:
        """
        Check whether the structure of a 'names_per_nomenclature' field in JSON was correct.
        """
        if names_per_nomenclature is None:
            self.send_syntax_error("Field 'names_per_nomenclature' was missing.")
            return False;
        elif not isinstance(names_per_nomenclature, dict):
            self.send_syntax_error("Field 'names_per_nomenclature' is not a dictionary.")
            return False
        else:
            for (nomenclature_name, names) in names_per_nomenclature.items():
                if not isinstance(nomenclature_name, str):
                    self.send_syntax_error("Field 'names_per_nomenclature' has keys that are not strings.")
                    return False
                elif not isinstance(names, list):
                    self.send_syntax_error("Field 'names_per_nomenclature' has keys that are not lists.")
                    return False
                else:
                    for name in names:
                        if not isinstance(name, str):
                            self.send_syntax_error("The given names are not strings")
                            return False
        return True

    def __send_endpoint_not_found(self):
        print("Client requested endpoint that was not found.")
        self.send_error(404, "The specified endpoint was not found.")

    def __send_method_not_supported(self):
        print("Tried " + self.command +
              " on endpoint that doesn't support it.")
        self.send_error(405,
                        "The specified endpoint doesn't support the method "
                        + self.command + ". This could also be caused by unexpected input.")

    def __handle_general_exception(self, exceptionInfo):
        print(exceptionInfo)
        self.send_error(500, str(exceptionInfo))

    def extract_ids(self, url: str):
        """
        Makes a list of the numerical ids or uuids in the url, in the order
        in which they appeared.
        """
        return [s for s in url.split('/') if
                re.fullmatch("[a-zA-Z0-9-]*[0-9]+[a-zA-Z0-9-]*", s)]

    @property
    def ids(self) -> Sequence[str]:
        return self.extract_ids(self.path)

    @property
    def url_params(self) -> Mapping[str, str]:
        if '?' in self.path:
            params_part = self.path.split('?')[1]
        else:
            return dict()
        param_assignments = params_part.split('&')
        params = dict()
        for assignment in param_assignments:
            parts = assignment.split('=')
            name = parts[0]
            value = parts[1]
            params[name] = value
        return params

    @property
    def __endpoint(self):
        """
        The path in the api.
        Any numeric id will be replaced by {id}
        If the api is located on a seperate relative path (like '/api')
        this function should remove that part.
        This removes url parameters and
        """
        endpoint = re.sub("[a-zA-Z0-9-]*[0-9]+[a-zA-Z0-9-]*", "{id}", self.path)
        endpoint = re.sub("\?.*", "", endpoint)
        return endpoint
