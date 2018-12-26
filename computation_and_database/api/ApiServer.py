from http.server import HTTPServer

from ConfigurationReader import ConfigurationReader
from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from controllers.ControllerFacade import ControllerFacade


class ApiServer(HTTPServer):

    def __init__(self):
        self.__configuration_reader = ConfigurationReader()
        server_address = (self.__configuration_reader.base_url,
                          self.__configuration_reader.port_number)
        super().__init__(server_address, GeneralRequestHandler)
        self.__handlers_per_endpoint = dict()
        self.__controller_facade = ControllerFacade()

    def get_handler_for_endpoint(self, endpoint: str):
        handler_class = self.__handlers_per_endpoint.get(endpoint)
        if handler_class is None:
            return None
        else:
            return handler_class()

    def register_handler_class_for_endpoint(self, endpoint:str, handler_class):
        """
        This should be called in the files of these classes.
        (Avoids circular dependency and errors when removing the file.)
        """
        print("Registered endpoint " + endpoint)
        self.__handlers_per_endpoint[endpoint] = handler_class

    @property
    def configuration_reader(self):
        return self.__configuration_reader

    @property
    def controller_facade(self):
        return self.__controller_facade

    @property
    def base_url_with_port(self):
        base_url =  self.__configuration_reader.base_url
        port_str = str(self.__configuration_reader.port_number)
        return 'http://' + base_url + ':' + port_str
