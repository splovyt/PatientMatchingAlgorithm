from domain.state.CancerType import CancerType as CancerType

class CancerSubtype:

    def __init__(self, cancer_type: CancerType):
        assert cancer_type is not None
        self.__cancer_type = cancer_type

    @property
    def cancer_type(self) -> CancerType:
        return self.__cancer_type