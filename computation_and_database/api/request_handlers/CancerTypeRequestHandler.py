from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler


class CancerTypeRequestHandler:
    endpoint = "/cancer-types/{id}/"

    def get(self, general_request_handler: GeneralRequestHandler):
        cancer_type_id = int(general_request_handler.ids[0])
        self.get_for_id(
            general_request_handler=general_request_handler,
            cancer_type_id=cancer_type_id
        )

    def get_for_id(self, general_request_handler: GeneralRequestHandler, cancer_type_id: int):
        server = general_request_handler.server
        controller_facade = server.controller_facade

        if cancer_type_id not in controller_facade.cancer_type_ids:
            general_request_handler.send_resource_not_found()
            return

        self_url = server.base_url_with_port + CancerTypeRequestHandler.endpoint.replace('{id}', str(cancer_type_id))

        json_object = {
            'self': {'href': self_url},
            'names_per_nomenclature': controller_facade.get_cancer_type_names_per_nomenclature(cancer_type_id),
            'subtypes': {'href': self_url + 'subtypes/'}
        }

        general_request_handler.send_json_response(json_object)

