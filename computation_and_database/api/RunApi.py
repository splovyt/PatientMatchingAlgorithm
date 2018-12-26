from api.request_handlers.HomeRequestHandler import HomeRequestHandler
from api.request_handlers.SimilarPatientsComputationMethodsRequestHandler\
    import SimilarPatientsComputationMethodsRequestHandler
from api.request_handlers.PatientListRequestHandler import\
    PatientListRequestHandler
from api.request_handlers.CancerTypeListRequestHandler import\
    CancerTypeListRequestHandler
from api.request_handlers.CancerTypeRequestHandler import\
    CancerTypeRequestHandler
from api.request_handlers.CancerSubtypeListRequestHandler import\
    CancerSubtypeListRequestHandler
from api.request_handlers.CancerSubtypeRequestHandler import\
    CancerSubtypeRequestHandler
from api.request_handlers.PatientRequestHandler import\
    PatientRequestHandler
from api.request_handlers.AberrationsRequestHandler import\
    AberrationsRequestHandler
from api.ApiServer import ApiServer


def run_api():
    print('starting server...')
    httpd = ApiServer()
    register_endpoints(httpd)

    print('running server...')
    httpd.serve_forever()


def register_endpoints(server: ApiServer):
    server.register_handler_class_for_endpoint(HomeRequestHandler.endpoint,
                                        HomeRequestHandler)
    server.register_handler_class_for_endpoint(
        SimilarPatientsComputationMethodsRequestHandler.endpoint,
        SimilarPatientsComputationMethodsRequestHandler
    )
    server.register_handler_class_for_endpoint(
        PatientListRequestHandler.endpoint,
        PatientListRequestHandler
    )
    server.register_handler_class_for_endpoint(
        PatientRequestHandler.endpoint,
        PatientRequestHandler
    )
    server.register_handler_class_for_endpoint(
        CancerTypeListRequestHandler.endpoint,
        CancerTypeListRequestHandler
    )
    server.register_handler_class_for_endpoint(
        CancerTypeRequestHandler.endpoint,
        CancerTypeRequestHandler
    )
    server.register_handler_class_for_endpoint(
        CancerSubtypeListRequestHandler.endpoint,
        CancerSubtypeListRequestHandler
    )
    server.register_handler_class_for_endpoint(
        CancerSubtypeRequestHandler.endpoint,
        CancerSubtypeRequestHandler
    )
    server.register_handler_class_for_endpoint(
        AberrationsRequestHandler.endpoint,
        AberrationsRequestHandler
    )
