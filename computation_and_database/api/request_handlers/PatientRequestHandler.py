from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from api.request_handlers.AberrationsRequestHandler import AberrationsRequestHandler
from api.request_handlers.SimilarPatientListListRequestHandler import SimilarPatientListListRequestHandler
from api.request_handlers.CancerSubtypeRequestHandler import CancerSubtypeRequestHandler
from uuid import UUID


class PatientRequestHandler:
    endpoint = "/patients/{id}/"

    def get(self, general_request_handler: GeneralRequestHandler):
        patient_id = UUID(general_request_handler.ids[0])
        return self.get_for_id(general_request_handler, patient_id)

    def get_for_id(self, general_request_handler: GeneralRequestHandler, patient_id):
        controller_facade = general_request_handler.controller_facade

        json_object = {
            'self': general_request_handler
                .get_url_for_endpoint(PatientRequestHandler.endpoint.replace('{id}', str(patient_id))),
            'id': str(patient_id),
            'name': controller_facade.get_name_for_patient(patient_id),
            'gene_aberrations': general_request_handler
                .get_url_for_endpoint(AberrationsRequestHandler.endpoint.replace('{id}', str(patient_id))),
            'similar_patient_lists': SimilarPatientListListRequestHandler.endpoint.replace('{id}', str(patient_id))
        }

        if controller_facade.get_cancer_subtype_id_for_patient(patient_id) is not None:
            cancer_subtype_link = CancerSubtypeRequestHandler.endpoint.replace(
                '{id}',
                str(controller_facade.get_cancer_type_id_for_patient(patient_id)),
                1
            )

            cancer_subtype_link = general_request_handler.get_url_for_endpoint(cancer_subtype_link.replace(
                '{id}',
                str(controller_facade.get_cancer_subtype_id_for_patient(patient_id)),
                1
            ))

            json_object['cancer_subtype'] = cancer_subtype_link

        general_request_handler.send_json_response(json_object)