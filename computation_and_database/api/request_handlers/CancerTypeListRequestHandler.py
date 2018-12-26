from api.request_handlers.GeneralRequestHandler import \
    GeneralRequestHandler
from api.request_handlers.CancerTypeRequestHandler import CancerTypeRequestHandler


class CancerTypeListRequestHandler:
    endpoint = "/cancer-types/"

    def get(self, general_request_handler: GeneralRequestHandler):
        server = general_request_handler.server
        controller_facade = server.controller_facade

        url = general_request_handler.self_url

        json_object = {
            'self': {'href': url},
            'cancer_types': list()
        }

        for id in controller_facade.cancer_type_ids:
            json_object['cancer_types'].append(
                {'href': url + str(id) + "/"}
            )

        general_request_handler.send_json_response(json_object)

    def post(self, general_request_handler: GeneralRequestHandler):
        names_per_nomenclature = general_request_handler.input_json_object.get('names_per_nomenclature')

        # Check for syntax errors
        if not general_request_handler.check_names_per_nomenclature_structure(names_per_nomenclature):
            return

        controller_facade = general_request_handler.server.controller_facade
        cancer_type_id = controller_facade.make_cancer_type(names_per_nomenclature)

        if cancer_type_id not in controller_facade.cancer_type_ids:
            general_request_handler.send_resource_not_found()
            return

        CancerTypeRequestHandler().get_for_id(
            general_request_handler=general_request_handler,
            cancer_type_id=cancer_type_id
        )