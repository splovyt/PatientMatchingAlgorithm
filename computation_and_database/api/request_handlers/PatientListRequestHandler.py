from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from api.request_handlers.CancerTypeListRequestHandler import\
    CancerTypeListRequestHandler
from api.request_handlers.PatientRequestHandler import PatientRequestHandler
from api.ApiServer import ApiServer
from controllers.ControllerFacade import ControllerFacade
import re


class PatientListRequestHandler:
    endpoint = "/patients/"
    filter_url_param = "query"
    first_patient_url_param = "first-patient"
    number_of_patients_url_param = "number-of-patients"

    def get(self, general_request_handler: GeneralRequestHandler):
        print("Patient list requested.")

        server = general_request_handler.server
        controller_facade = server.controller_facade

        current_page_url = general_request_handler.self_url
        patient_list = self.get_patient_list(
            general_request_handler=general_request_handler,
            controller_facade=controller_facade,
            server=server
        )

        json_object = {
            'self': {'href': current_page_url},
            'patients': patient_list
        }

        if general_request_handler.url_params.get(PatientListRequestHandler.number_of_patients_url_param) is not None:
            next_page_url = self.get_next_page_url(general_request_handler=general_request_handler)
            previous_page_url = self.get_previous_page_url(general_request_handler=general_request_handler)
            json_object['next_page'] = {'href': next_page_url}
            json_object['previous_page'] = {'href': previous_page_url}


        general_request_handler.send_json_response(json_object)

    def post(self, general_request_handler: GeneralRequestHandler):
        input_json = general_request_handler.input_json_object

        name = input_json.get('name')
        cancer_subtype_url = input_json.get('cancer_subtype')

        if cancer_subtype_url is not None:
            # extract the id
            cancer_subtype_url_ids = general_request_handler.extract_ids(cancer_subtype_url)

            if len(cancer_subtype_url_ids) != 2 :
                general_request_handler.send_syntax_error('Could not parse cancer subtype url.')

            cancer_subtype_id = int(cancer_subtype_url_ids[1])

        controller_facade = general_request_handler.controller_facade
        patient_id = controller_facade.new_patient()

        if cancer_subtype_url is not None:
            controller_facade.set_cancer_subtype_for_patient(
                patient_id=patient_id,
                cancer_subtype_id=cancer_subtype_id
            )

        if name is not None:
            controller_facade.set_name_for_patient(patient_id, name)

        PatientRequestHandler().get_for_id(
            general_request_handler=general_request_handler,
            patient_id=patient_id
        )


    def get_patient_list(self,
                         general_request_handler: GeneralRequestHandler,
                         controller_facade: ControllerFacade,
                         server: ApiServer):
        url_params = general_request_handler.url_params
        filter_query = url_params.get(PatientListRequestHandler.filter_url_param)
        first_patient_index = url_params.get(PatientListRequestHandler.first_patient_url_param)
        if first_patient_index is not None:
            first_patient_index = int(first_patient_index)
        number_of_patients = url_params.get(PatientListRequestHandler.number_of_patients_url_param)
        if number_of_patients is not None:
            number_of_patients = int(number_of_patients)

        ids = controller_facade.get_patient_ids(
            filter_query=filter_query,
            first_patient=first_patient_index,
            number_of_patients=number_of_patients)

        patient_json_objects = list()

        for patient_id in ids:
            patient_json_objects.append(
                {'href': server.base_url_with_port +
                PatientListRequestHandler.endpoint + str(patient_id) + "/"}
            )

        return patient_json_objects

    def get_next_page_url(self, general_request_handler: GeneralRequestHandler):
        url_params = general_request_handler.url_params
        number_of_patients = \
            int(url_params.get(PatientListRequestHandler.number_of_patients_url_param))
        return self.__get_page_url_with_offset(
            general_request_handler=general_request_handler,
            offset=number_of_patients
        )

    def get_previous_page_url(self, general_request_handler: GeneralRequestHandler):
        url_params = general_request_handler.url_params
        number_of_patients = \
            int(url_params.get(PatientListRequestHandler.number_of_patients_url_param))
        return self.__get_page_url_with_offset(
            general_request_handler=general_request_handler,
            offset=-number_of_patients
        )

    def __get_page_url_with_offset(self, general_request_handler: GeneralRequestHandler, offset: int):
        """
        Get a page url starting from offset patients further than the current first patient.
        """
        url_params = general_request_handler.url_params
        current_first_patient_index = \
            int(url_params.get(PatientListRequestHandler.first_patient_url_param))
        new_first_patient_index = current_first_patient_index + offset
        current_page_url = general_request_handler.self_url
        param_name = PatientListRequestHandler.first_patient_url_param
        return re.sub(param_name + "=-?[0-9]*",
                      param_name + "=" + str(new_first_patient_index),
                      current_page_url
                      )
