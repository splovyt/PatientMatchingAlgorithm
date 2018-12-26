from controllers.ControllerContext import ControllerContext
from domain.state.Patient import Patient
from domain.state.GeneAberrationRecord import GeneAberrationRecord
from typing import Iterable, Sequence, Tuple
from uuid import UUID
from threading import RLock


class PatientController:

    def __init__(self, controller_context: ControllerContext):
        self.__controller_context = controller_context
        patients = controller_context.domain_initializer.persisted_patients
        self.__lock = RLock()
        self.__biology = controller_context.biology
        self.__patient_ids = list()
        self.__patient_per_id = dict()
        for patient in patients:
            self.__patient_ids.append(patient.uuid)
            self.__patient_per_id[patient.uuid] = patient

    # REQUESTING INFO

    def get_patient_ids(self, filter_query: str = None,
                        first_patient: int = None,
                        number_of_patients: int = None) -> Sequence[UUID]:
        with self.__lock:
            if first_patient is None:
                first_patient = 0
            if number_of_patients is None:
                number_of_patients = len(self.__patient_ids)

            if filter_query is None:
                matching_patient_ids =  self.__patient_ids
            else:
                matching_patient_ids = []
                for patient_id in self.__patient_ids:
                    patient = self.__patient_per_id[patient_id]
                    if filter_query in patient.name:
                        matching_patient_ids.append(patient_id)

            patients_slice = \
                matching_patient_ids[first_patient:first_patient + number_of_patients]
            ids_tuple =  tuple(patients_slice)
        return ids_tuple

    def get_name_for_patient(self, uuid: UUID) -> str:
        return self.__get_patient(uuid).name

    def get_cancer_subtype_id_for_patient(self, uuid: UUID):
        patient = self.__get_patient(uuid)
        cancer_subtype = patient.cancer_subtype
        if cancer_subtype is None:
            return None
        else:
            return self.__controller_context.get_id_for_cancer_subtype(cancer_subtype)

    def get_cancer_type_id_for_patient(self, uuid: UUID):
        patient = self.__get_patient(uuid)
        if patient.cancer_subtype is None:
            return None
        cancer_type = patient.cancer_subtype.cancer_type
        if cancer_type is None:
            return None
        else:
            return self.__controller_context.get_id_for_cancer_type(cancer_type)

    def get_mutated_gene_vafs(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        patient = self.__get_patient(uuid)
        return self.__get_gene_aberrations(patient.mutation_record)

    def get_expressions(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        patient = self.__get_patient(uuid)
        return self.__get_gene_aberrations(patient.differential_expression_record)

    def get_methylations(self, uuid: UUID) -> Iterable[Tuple[str, float]]:
        patient = self.__get_patient(uuid)
        return self.__get_gene_aberrations(patient.methylation_record)

    def get_cnvs(self, uuid: UUID) -> Iterable[Tuple[str, int]]:
        patient = self.__get_patient(uuid)
        return self.__get_gene_aberrations(patient.copy_number_variation_record)

    def __get_gene_aberrations(self, aberration_record: GeneAberrationRecord):
        result = set()
        for (gene, score) in aberration_record.an_aberration_set.gene_scores:
            gene_name = self.__controller_context.biology.gene_metanomenclature\
                .get_nomenclature("ensembl").get_name_for_object(gene)
            result.add((gene_name, score))
        return frozenset(result)


    def __get_patient(self, uuid: UUID) -> Patient:
        assert uuid is not None
        with self.__lock:
            assert uuid in self.__patient_per_id
            patient = self.__patient_per_id[uuid]
        return patient


    # MANIPULATING PATIENTS

    def new_patient(self) -> UUID:
        patient = Patient()

        with self.__lock:
            self.__patient_ids.append(patient.uuid)
            self.__patient_per_id[patient.uuid] = patient

        return patient.uuid

    def set_name_for_patient(self, uuid: UUID, name: str):
        self.__get_patient(uuid).name = name

    def set_cancer_subtype_for_patient(self, patient_id: UUID, cancer_subtype_id: int):
        assert patient_id is not None
        assert cancer_subtype_id is not None
        assert isinstance(cancer_subtype_id, int)
        with self.__lock:
            cancer_subtype = self.__controller_context.get_cancer_subtype_for_id(cancer_subtype_id)
            if cancer_subtype is None:
                print('Tried to find cancer subtype with id: ')
                print(cancer_subtype_id)
                raise KeyError
            self.__patient_per_id[patient_id].cancer_subtype = cancer_subtype
