from domain.state.Nomenclature import \
    Nomenclature as Nomenclature
from typing import Type, Iterable, Tuple
from threading import RLock as Rlock

class Metanomenclature:
    """
    Stores nomenclatures per name.
    """

    def __init__(self, object_type: Type):
        """
        :param object_type: the types of objects the nomenclatures handle.
        """
        assert object_type is not None
        self.__object_type = object_type
        self.__nomenclature_per_name = dict()
        self.__lock = Rlock()

    def make_nomenclature(self, name: str):
        assert name is not None
        with self.__lock:
            self.__nomenclature_per_name[name] = Nomenclature(self.__object_type)

    def get_nomenclature(self, name: str) -> Nomenclature:
        """
        Can return None.
        """
        assert name is not None
        with self.__lock:
            nomenclature = self.__nomenclature_per_name.get(name)
        return nomenclature

    def get_nomenclatures_per_name(self) -> Iterable[Tuple[str, Nomenclature]]:
        """
        Don't use these names to look up nomenclatures. They may have changed.
        Just use the tuples.
        """
        with self.__lock:
            nomenclatures_per_name = frozenset(self.__nomenclature_per_name.items())
        return nomenclatures_per_name
