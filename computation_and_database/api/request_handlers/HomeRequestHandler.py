from api.request_handlers.GeneralRequestHandler import GeneralRequestHandler
from api.request_handlers.PatientListRequestHandler import\
    PatientListRequestHandler
from api.request_handlers.CancerTypeListRequestHandler import \
    CancerTypeListRequestHandler
from api.request_handlers.SimilarPatientsComputationMethodsRequestHandler\
    import SimilarPatientsComputationMethodsRequestHandler


class HomeRequestHandler:
    """
    Handles requests on the / endpoint.
    """

    endpoint = "/"

    def get(self, general_request_handler: GeneralRequestHandler):
        print("Homepage requested.")

        #Helper variables
        server = general_request_handler.server
        patients_endpoint = PatientListRequestHandler.endpoint
        first_patient_url_param = \
            PatientListRequestHandler.first_patient_url_param
        number_of_patients_url_param = \
            PatientListRequestHandler.number_of_patients_url_param
        number_of_patients = \
            server.configuration_reader.initial_number_of_patients_per_page
        filter_url_param = PatientListRequestHandler.filter_url_param

        #The urls that will be used
        all_patients_url = server.base_url_with_port + patients_endpoint
        first_patient_page_url = all_patients_url + "?" + \
            first_patient_url_param + "=" + "0&" + \
            number_of_patients_url_param + "=" + str(number_of_patients)


        json_object = {
            "self": {'href': general_request_handler.self_url},
            "patients" : {
                "first_page": {"href": first_patient_page_url},
                "all_patients": {"href": all_patients_url},
                "filter_url_parameter": filter_url_param,
                "first_patient_url_parameter": first_patient_url_param,
                "number_of_patients_url_parameter": number_of_patients_url_param
            },
            "similar_patients_computation_methods": { "href" : server.base_url_with_port +
                SimilarPatientsComputationMethodsRequestHandler.endpoint},
            "cancer_types": {"href": server.base_url_with_port +
                CancerTypeListRequestHandler.endpoint}
        }

        general_request_handler.send_json_response(json_object)

