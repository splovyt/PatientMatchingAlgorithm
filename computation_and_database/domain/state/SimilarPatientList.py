from domain.state.Patient import Patient as Patient
from domain.state.SimilarPatient import SimilarPatient as SimilarPatient
from domain.state.SimilarPatientsComputationMethod import\
    SimilarPatientsComputationMethod as SimilarPatientsComputationMethod
from typing import Sequence, Iterable
from datetime import date


class SimilarPatientList:

    def __init__(self, patient: Patient, similar_patients: Sequence[SimilarPatient],
                 used_data_sources: Iterable, creation_date: date,
                 used_method: SimilarPatientsComputationMethod):
        assert patient is not None
        assert similar_patients is not None
        assert used_data_sources is not None
        assert creation_date is not None
        assert used_method is not None
        self.__patient = patient
        self.__similar_patients = similar_patients
        self.__used_data_sources = used_data_sources
        self.__creation_date = creation_date
        self.__used_method = used_method

    @property
    def patient(self):
        return self.__patient

    @property
    def similar_patients(self):
        return self.__similar_patients

    @property
    def used_data_sources(self):
        return self.__used_data_sources

    @property
    def creation_date(self):
        return self.__creation_date

    @property
    def used_method(self):
        return self.__used_method