from controllers.ControllerContext import ControllerContext
from domain.state.CancerType import CancerType
from domain.state.CancerSubtype import CancerSubtype
from typing import Mapping, Sequence, Iterable
from threading import RLock


class CancerTypeController:

    def __init__(self, controller_context: ControllerContext):
        self.__lock = RLock()
        self.__controller_context = controller_context
        self.__biology = controller_context.biology
        self.__cancer_type_id_counter = 0
        self.__cancer_subtype_id_counter = 0
        self.__subtypes_per_type = dict()
        for cancer_type in controller_context.domain_initializer.cancer_types:
            self.__add_cancer_type(cancer_type)
        for cancer_subtype in controller_context.domain_initializer.cancer_subtypes:
            self.__add_cancer_subtype(cancer_subtype)

    @property
    def cancer_type_ids(self):
        return self.__controller_context.get_cancer_type_ids()

    def get_cancer_type_names_per_nomenclature(self, cancer_type_id: int) -> \
            Mapping[str, Sequence[str]]:

        with self.__lock:
            cancer_type = self.__controller_context.get_cancer_type_for_id(cancer_type_id)

        return self.__get_cancer_type_names_per_nomenclature(cancer_type)

    def __get_cancer_type_names_per_nomenclature(self, cancer_type: CancerType) -> \
            Mapping[str, Sequence[str]]:
        names_per_nomenclature = dict()

        for (name, nomenclature) in self.__biology\
                    .cancer_type_metanomenclature\
                    .get_nomenclatures_per_name():
            names_per_nomenclature[name] =\
                list(nomenclature.get_names_for_object(cancer_type))

        return names_per_nomenclature

    def get_cancer_subtype_ids_for_type(self, cancer_type_id: int) -> Sequence[int]:
        with self.__lock:
            ids = self.__subtypes_per_type[cancer_type_id].keys()
            if ids is not None:
                ids = list(ids)
            else:
                ids = list()
        return ids

    def __add_cancer_type(self, cancer_type: CancerType) -> int:
        with self.__lock:
            cancer_type_index = self.__cancer_type_id_counter
            self.__controller_context.set_id_for_cancer_type(cancer_type, cancer_type_index)
            self.__subtypes_per_type[cancer_type_index] = dict()
            self.__cancer_type_id_counter += 1

        return cancer_type_index

    def make_cancer_type(self, names_per_nomenclature: Mapping[str, Iterable[str]]) -> int:
        cancer_type = CancerType()

        metanomenclature = self.__biology.cancer_type_metanomenclature

        self.__controller_context.add_names_to_metanomenclature(
            metanomenclature=metanomenclature,
            object=cancer_type,
            names_per_nomenclature=names_per_nomenclature
        )

        return self.__add_cancer_type(
            cancer_type=cancer_type
        )

    def get_cancer_subtype_names_per_nomenclature(self, cancer_type_id: int, cancer_subtype_id: int) -> \
            Mapping[str, Sequence[str]]:

        with self.__lock:
            cancer_subtype = self.__subtypes_per_type[cancer_type_id][cancer_subtype_id]

        return self.__get_cancer_subtype_names_per_nomenclature(cancer_subtype)

    def __get_cancer_subtype_names_per_nomenclature(self, cancer_subtype: CancerSubtype) -> \
            Mapping[str, Sequence[str]]:
        names_per_nomenclature = dict()

        for (name, nomenclature) in self.__biology\
                    .cancer_subtype_metanomenclature\
                    .get_nomenclatures_per_name():
            names_per_nomenclature[name] =\
                list(nomenclature.get_names_for_object(cancer_subtype))

        return names_per_nomenclature

    def make_cancer_subtype(self, cancer_type_id: int, names_per_nomenclature: Mapping[str, Iterable[str]]) -> int:
        with self.__lock:
            cancer_type = self.__controller_context.get_cancer_type_for_id(cancer_type_id)
            subtype = CancerSubtype(cancer_type)

        metanomenclature = self.__biology.cancer_subtype_metanomenclature

        self.__controller_context.add_names_to_metanomenclature(
            metanomenclature=metanomenclature,
            object=subtype,
            names_per_nomenclature=names_per_nomenclature
        )

        return self.__add_cancer_subtype(subtype)

    def __add_cancer_subtype(self, subtype: CancerSubtype) -> int:
        with self.__lock:
            cancer_type_id = self.__controller_context.get_id_for_cancer_type(subtype.cancer_type)

            subtype_index = self.__cancer_subtype_id_counter

            self.__subtypes_per_type[cancer_type_id][subtype_index] = subtype
            self.__cancer_subtype_id_counter += 1

        self.__controller_context.set_id_for_cancer_subtype(
            subtype=subtype,
            subtype_id=subtype_index
        )

        return subtype_index
