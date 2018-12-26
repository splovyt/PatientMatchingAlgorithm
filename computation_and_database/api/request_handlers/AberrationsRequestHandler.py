from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from uuid import UUID

class AberrationsRequestHandler:
    endpoint = "/patients/{id}/aberrations/"

    def get(self, general_request_handler: GeneralRequestHandler):
        controller_facade = general_request_handler.controller_facade

        patient_id = UUID(general_request_handler.ids[0])

        json = {
            'self': general_request_handler
                .get_url_for_endpoint(AberrationsRequestHandler.endpoint.replace('{id}', str(patient_id))),
            'mutated_gene_vafs': dict(controller_facade.get_mutated_gene_vafs_for_patient(patient_id)),
            'expressions': dict(controller_facade.get_expressions_for_patient(patient_id)),
            'methylations': dict(controller_facade.get_methylations_for_patient(patient_id)),
            'cnvs': dict(controller_facade.get_cnvs_for_patient(patient_id))
        }

        general_request_handler.send_json_response(json)