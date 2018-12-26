import abc

class SimilarPatientsComputationMethod(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def name(self):
        pass