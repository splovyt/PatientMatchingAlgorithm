from domain.state.Patient import Patient as Patient

class SimilarPatient:

    def __init__(self, patient: Patient, similarity_explanation: str, similarity_score: float):
        assert patient is not None
        self.__patient = patient
        self.__similarity_explanation = similarity_explanation
        self.__score = similarity_score

    @property
    def patient(self) -> Patient:
        return self.__patient

    @property
    def similarity_score(self) -> float:
        """
        A score representing how similar the patient is.
        """
        return self.__score

    @property
    def similarity_explanation(self):
        return self.__similarity_explanation