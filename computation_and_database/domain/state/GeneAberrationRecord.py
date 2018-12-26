from domain.state.GeneAberrationSet import GeneAberrationSet as \
    GeneAberrationSet
from threading import RLock as RLock
from typing import Iterable, TypeVar, Generic


# The score for a gene
Score = TypeVar('Score')


class GeneAberrationRecord(Generic[Score]):
    """
    GeneAberrationSets stored per data source.
    If required this can be optimized for memory by only fetching
    the sets from the database when needed.
    """

    def __init__(self):
        self.__aberration_set_per_source = dict()
        self.__lock = RLock()

    def clear(self):
        self.__aberration_set_per_source = dict()

    def add_aberration_set(self, aberration_set: GeneAberrationSet[Score]):
        source = aberration_set.data_source
        with self.__lock:
            assert self.__aberration_set_per_source.get(source) is None
            self.__aberration_set_per_source[source] = aberration_set

    def get_aberration_set(self, data_source) -> GeneAberrationSet[Score]:
        with self.__lock:
            aberration_set = self.__aberration_set_per_source.get(data_source)
        return aberration_set

    @property
    def aberration_sets(self) -> Iterable[GeneAberrationSet[Score]]:
        return set(self.__aberration_set_per_source.values())

    @property
    def an_aberration_set(self) -> GeneAberrationSet[Score]:
        for aberration_set in self.aberration_sets:
            return aberration_set
        return GeneAberrationSet('empty', {})
