from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
import re


class CancerSubtypeRequestHandler:
    endpoint = '/cancer-types/{id}/subtypes/{id}/'

    def get(self, general_request_handler: GeneralRequestHandler):
        subtype_id = int(general_request_handler.ids[1])
        self.get_for_id(
            general_request_handler=general_request_handler,
            subtype_id=subtype_id
        )

    def get_for_id(self, general_request_handler: GeneralRequestHandler, subtype_id: int):
        cancer_type_id = int(general_request_handler.ids[0])

        server = general_request_handler.server
        controller_facade = server.controller_facade

        if cancer_type_id not in controller_facade.cancer_type_ids or\
                subtype_id not in controller_facade.get_cancer_subtype_ids_for_type(cancer_type_id):
            general_request_handler.send_resource_not_found()
            return

        self_url = server.base_url_with_port +\
                   CancerSubtypeRequestHandler.endpoint\
                       .replace('{id}', str(cancer_type_id), 1)\
                       .replace('{id}', str(subtype_id), 1)
        cancer_type_url = re.sub('subtypes/[0-9]*/', '', self_url)

        json_object = {
            'self': {'href': self_url},
            'cancer_type': {'href': cancer_type_url},
            'names_per_nomenclature': controller_facade.get_cancer_subtype_names_per_nomenclature(
                cancer_type_id, subtype_id)
        }

        general_request_handler.send_json_response(json_object)
