from domain.state.GeneAberrationRecord import GeneAberrationRecord as\
    GeneAberrationRecord
from domain.state.CancerSubtype import CancerSubtype as CancerSubtype
from datetime import date
from threading import RLock as RLock
import uuid


class Patient:
    """
    The similar patient lists are not stored here to avoid circular
    dependencies. This also makes it easier to optimize memory
    because loading one patient in memory wil not automatically
    load others.
    The controllers can simply use a map to keep the similar patient
    lists.
    """

    def __init__(self):
        self.__mutation_record = GeneAberrationRecord[bool]()
        self.__differential_expression_record = GeneAberrationRecord[float]()
        self.__copy_number_variation_record = GeneAberrationRecord[int]()
        self.__methylation_record = GeneAberrationRecord[float]()
        self.__lock = RLock()
        self.__uuid = uuid.uuid4()
        self.name = None
        self.cancer_subtype = None

    @property
    def uuid(self) -> uuid.UUID:
        return self.__uuid

    @property
    def mutation_record(self) -> GeneAberrationRecord[float]:
        """
        VAF-values
        """
        return self.__mutation_record

    @property
    def differential_expression_record(self) -> GeneAberrationRecord[float]:
        return self.__differential_expression_record

    @property
    def copy_number_variation_record(self) -> GeneAberrationRecord[int]:
        return self.__copy_number_variation_record

    @property
    def methylation_record(self) -> GeneAberrationRecord[float]:
        return self.__methylation_record

    @property
    def cancer_subtype(self):
        with self.__lock:
            cancer_subtype = self.__cancer_subtype
        return cancer_subtype

    @cancer_subtype.setter
    def cancer_subtype(self, cancer_subtype: CancerSubtype):
        with self.__lock:
            self.__cancer_subtype = cancer_subtype

    @property
    def name(self):
        """
        Can be an alias.
        :return:
        """
        with self.__lock:
            name = self.__name
        return name

    @name.setter
    def name(self, name: str):
        with self.__lock:
            self.__name = name
