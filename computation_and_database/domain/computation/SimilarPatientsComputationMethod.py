import domain.state.SimilarPatientsComputationMethod
from domain.state.Biology import Biology as Biology
from domain.state.Patient import Patient as Patient
from domain.state.SimilarPatientList import SimilarPatientList\
    as SimilarPatientList
from typing import Iterable
import abc

class SimilarPatientComputationMethod(
    domain.state.SimilarPatientsComputationMethod.
        SimilarPatientsComputationMethod):

    @abc.abstractmethod
    def compute_similar_patients(self, biology: Biology, patient: Patient,
                                 all_patients: Iterable[Patient])\
            -> SimilarPatientList:
        pass
