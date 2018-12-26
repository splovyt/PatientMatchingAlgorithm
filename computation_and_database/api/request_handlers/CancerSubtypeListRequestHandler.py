from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from api.request_handlers.CancerSubtypeRequestHandler import CancerSubtypeRequestHandler


class CancerSubtypeListRequestHandler:
    endpoint = "/cancer-types/{id}/subtypes/"

    def get(self, general_request_handler: GeneralRequestHandler):
        controller_facade = general_request_handler.server.controller_facade

        json_object = {
            'self': {'href': general_request_handler.self_url},
            'cancer_type': {'href': general_request_handler.self_url.replace("subtypes/", "")},
            'cancer_subtypes': []
        }

        for subtype_id in controller_facade.get_cancer_subtype_ids_for_type(int(general_request_handler.ids[0])):
            json_object['cancer_subtypes'].append(
                {'href': general_request_handler.self_url + str(subtype_id) + '/'}
            )

        general_request_handler.send_json_response(json_object)

    def post(self, general_request_handler: GeneralRequestHandler):
        names_per_nomenclature = general_request_handler.input_json_object.get('names_per_nomenclature')

        # Check for syntax errors
        if not general_request_handler.check_names_per_nomenclature_structure(names_per_nomenclature):
            return

        cancer_type_id = int(general_request_handler.ids[0])


        controller_facade = general_request_handler.server.controller_facade
        subtype_id = controller_facade.make_cancer_subtype(cancer_type_id, names_per_nomenclature)

        if cancer_type_id not in controller_facade.cancer_type_ids:
            general_request_handler.send_resource_not_found()
            return

        CancerSubtypeRequestHandler().get_for_id(
            general_request_handler=general_request_handler,
            subtype_id=subtype_id
        )