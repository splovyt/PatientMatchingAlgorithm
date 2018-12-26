from typing import Iterable
from threading import RLock as Rlock


class Nomenclature:
    """
    A nomenclature for objects like genes or pathways.
    """

    def __init__(self, object_type):
        """
        :param object_type: the type of objects this nomenclature should handle
        """
        assert object_type is not None
        self.__object_type = object_type
        self.__objects_per_name = dict()
        self.__names_per_object = dict()
        self.__lock = Rlock()

    def get_objects_with_name(self, name: str) -> Iterable:
        assert name is not None
        with self.__lock:
            objects = self.__objects_per_name.get(name)
        if objects is None:
            return frozenset()
        else:
            return frozenset(objects)

    def get_object_with_name(self, name: str):
        for object in self.get_objects_with_name(name):
            return object
        return None

    def get_names_for_object(self, object) -> Iterable[str]:
        assert object is not None
        with self.__lock:
            names = self.__names_per_object.get(object)
        if names is None:
            return frozenset()
        else:
            return frozenset(names)

    def get_name_for_object(self, object) -> str:
        for name in self.get_names_for_object(object):
            return name
        return None

    def add_names_for_object(self, new_names: Iterable[str], object):
        assert new_names is not None
        assert object is not None
        assert isinstance(object, self.__object_type)
        with self.__lock:
            self.__update_objects_per_name(new_names, object)
            self.__update_names_per_object(new_names, object)

    def __update_objects_per_name(self, new_names: Iterable[str], object):
        """
        WARNING: not thread-safe. Use a lock when using this method.
        """
        for name in new_names:
            current_objects = self.__objects_per_name.get(name)
            if current_objects is None:
                current_objects = set()
                self.__objects_per_name[name] = current_objects
            current_objects.add(object)

    def __update_names_per_object(self, new_names: Iterable[str], object):
        """
        WARNING: not thread-safe. Use a lock when using this method.
        """
        current_names = self.__names_per_object.get(object)
        if current_names is None:
            current_names = set()
            self.__names_per_object[object] = current_names
        for name in new_names:
            current_names.add(name)
