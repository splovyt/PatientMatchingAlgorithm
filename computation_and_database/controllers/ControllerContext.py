from domain.DomainInitializer import DomainInitializer
from domain.state.Metanomenclature import Metanomenclature
from domain.state.Biology import Biology
from domain.state.CancerSubtype import CancerSubtype
from domain.state.CancerType import CancerType
from typing import Iterable, Mapping
from threading import RLock


class ControllerContext:

    def __init__(self):
        self.__domain_initializer = DomainInitializer()
        self.__id_per_cancer_subtype = dict()
        self.__id_per_cancer_type = dict()
        self.__cancer_subtype_per_id = dict()
        self.__cancer_type_per_id = dict()
        self.__lock = RLock()

    def get_id_for_cancer_subtype(self, subtype: CancerSubtype) -> int:
        with self.__lock:
            return self.__id_per_cancer_subtype.get(subtype)

    def get_cancer_subtype_for_id(self, id: int) -> CancerSubtype:
        assert isinstance(id, int)
        with self.__lock:
            return self.__cancer_subtype_per_id.get(id)

    def set_id_for_cancer_subtype(self, subtype: CancerSubtype, subtype_id):
        with self.__lock:
            self.__id_per_cancer_subtype[subtype] = subtype_id
            self.__cancer_subtype_per_id[subtype_id] = subtype

    def get_id_for_cancer_type(self, type: CancerType) -> int:
        with self.__lock:
            return self.__id_per_cancer_type.get(type)

    def get_cancer_type_for_id(self, id: int) -> CancerType:
        with self.__lock:
            return self.__cancer_type_per_id.get(id)

    def set_id_for_cancer_type(self, type: CancerType, type_id):
        with self.__lock:
            self.__id_per_cancer_type[type] = type_id
            self.__cancer_type_per_id[type_id] = type

    def get_cancer_type_ids(self):
        with self.__lock:
            ids = frozenset(self.__cancer_type_per_id.keys())
        return ids

    @property
    def domain_initializer(self) -> DomainInitializer:
        return self.__domain_initializer

    @property
    def biology(self) -> Biology:
        return self.domain_initializer.biology

    def add_names_to_metanomenclature(self, metanomenclature: Metanomenclature, object,
                                      names_per_nomenclature: Mapping[str, Iterable[str]]):
        for (nomenclature_name, names) in names_per_nomenclature.items():
            nomenclature = metanomenclature.get_nomenclature(nomenclature_name)
            if nomenclature is None:
                metanomenclature.make_nomenclature(nomenclature_name)
                nomenclature = metanomenclature.get_nomenclature(nomenclature_name)
            nomenclature.add_names_for_object(
                new_names = names,
                object=object
            )