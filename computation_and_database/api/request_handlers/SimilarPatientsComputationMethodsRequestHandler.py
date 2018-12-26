from api.request_handlers.GeneralRequestHandler import\
    GeneralRequestHandler
from api.ApiServer import ApiServer

class SimilarPatientsComputationMethodsRequestHandler:
    """
    Handles requests on the /similar-patients-computation-methods/
    path.
    """
    endpoint = "/similar-patients-computation-methods/"

    def get(self, general_request_handler: GeneralRequestHandler):
        print("Similar patients computation methods requested.")

        server = general_request_handler.server

        json_object = {
            "self": {"href":
                     server.base_url_with_port +
                     SimilarPatientsComputationMethodsRequestHandler.endpoint},
            "methods": self.__methods_json_list(server)
        }

        general_request_handler.send_json_response(json_object)

    def __methods_json_list(self, server: ApiServer) -> list:
        json_list = list()
        for id in server.controller_facade.computation_method_ids:
            url_for_id = self.__get_url_for_id(server, id)
            name = server.controller_facade.computation_method_name_for_id(id)
            json_list.append({
                "href": url_for_id,
                "name": name
            })
        return json_list

    def __get_url_for_id(self, server: ApiServer, id: int) -> str:
        return server.base_url_with_port +\
               SimilarPatientsComputationMethodsRequestHandler.endpoint +\
               str(id) + "/"
