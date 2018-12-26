from controllers.ControllerContext import ControllerContext
from controllers.ComputationMethodController import ComputationMethodController
from controllers.PatientController import PatientController
from controllers.CancerTypeController import CancerTypeController
from typing import Iterable, Sequence, Mapping, Tuple
from uuid import UUID


class ControllerFacade:
    """
    Any id that will be used should be numeric.
    """

    def __init__(self):
        self.__controller_context = ControllerContext()
        self.__computation_method_controller = \
            ComputationMethodController(self.__controller_context)
        self.__patient_controller =\
            PatientController(self.__controller_context)
        self.__cancer_type_controller =\
            CancerTypeController(self.__controller_context)

    # COMPUTATION METHODS

    @property
    def computation_method_controller(self):
        return self.__computation_method_controller

    @property
    def computation_method_ids(self) -> Iterable[int]:
        return self.__computation_method_controller.method_ids

    def computation_method_name_for_id(self, id: int) -> str:
        return self.__computation_method_controller.get_method_name_for_id(id)

    # PATIENTS

    def get_patient_ids(self, filter_query: str = None,
                        first_patient: int = None,
                        number_of_patients: int = None) -> Sequence[UUID]:
        return self.__patient_controller.get_patient_ids(
            filter_query=filter_query,
            first_patient=first_patient,
            number_of_patients=number_of_patients
        )

    def get_name_for_patient(self, uuid: UUID) -> str:
        return self.__patient_controller.get_name_for_patient(uuid)

    def get_cancer_subtype_id_for_patient(self, patient_id: UUID) -> int:
        return self.__patient_controller.get_cancer_subtype_id_for_patient(patient_id)

    def get_cancer_type_id_for_patient(self, patient_id: UUID) -> int:
        return self.__patient_controller.get_cancer_type_id_for_patient(patient_id)

    def get_mutated_gene_vafs_for_patient(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        return self.__patient_controller.get_mutated_gene_vafs(uuid)

    def get_expressions_for_patient(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        return self.__patient_controller.get_expressions(uuid)

    def get_methylations_for_patient(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        return self.__patient_controller.get_methylations(uuid)

    def get_cnvs_for_patient(self, uuid: UUID) -> Iterable[Tuple[str, int]]:
        return self.__patient_controller.get_cnvs(uuid)

    def new_patient(self) -> UUID:
        return self.__patient_controller.new_patient()

    def set_name_for_patient(self, uuid: UUID, name: str):
        self.__patient_controller.set_name_for_patient(
            uuid=uuid,
            name=name
        )

    def set_cancer_subtype_for_patient(self, patient_id: UUID, cancer_subtype_id: int):
        self.__patient_controller.set_cancer_subtype_for_patient(
            patient_id=patient_id,
            cancer_subtype_id=cancer_subtype_id
        )

    # CANCER TYPES

    @property
    def cancer_type_ids(self) -> Iterable[int]:
        return self.__cancer_type_controller.cancer_type_ids

    def get_cancer_type_names_per_nomenclature(self, cancer_type_id: int) -> \
            Mapping[str, Sequence[str]]:
        return self.__cancer_type_controller\
            .get_cancer_type_names_per_nomenclature(cancer_type_id)

    def get_cancer_subtype_ids_for_type(self, cancer_type_id: int) -> Sequence[int]:
        return self.__cancer_type_controller\
            .get_cancer_subtype_ids_for_type(cancer_type_id)

    def make_cancer_type(self, names_per_nomenclature: Mapping[str, Iterable[str]]) -> int:
        return self.__cancer_type_controller.make_cancer_type(names_per_nomenclature)

    def get_cancer_subtype_names_per_nomenclature(self, cancer_type_id: int, cancer_subtype_id: int) -> \
            Mapping[str, Sequence[str]]:
        return self.__cancer_type_controller.get_cancer_subtype_names_per_nomenclature(cancer_type_id, cancer_subtype_id)

    def make_cancer_subtype(self, cancer_type_id: int, names_per_nomenclature: Mapping[str, Iterable[str]]) -> int:
        return self.__cancer_type_controller.make_cancer_subtype(cancer_type_id, names_per_nomenclature)