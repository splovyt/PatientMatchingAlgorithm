from controllers.ControllerContext import ControllerContext
from typing import Iterable


class ComputationMethodController:

    def __init__(self, controller_context: ControllerContext):
        assert controller_context is not None
        self.__controller_context = controller_context
        methods = controller_context.domain_initializer.\
                similar_patients_computation_methods
        self.__methods_per_id = dict()
        id = 0
        for method in methods:
            self.__methods_per_id[id] = method
            id = id + 1

    @property
    def method_ids(self) -> Iterable[int]:
        return self.__methods_per_id.keys()

    def get_method_name_for_id(self, id: int) -> str:
        method = self.__methods_per_id.get(id)
        return method.name