from domain.state.Gene import Gene as Gene
from typing import Iterable, Mapping, Tuple, TypeVar, Generic


# The score for a gene
Score = TypeVar('Score')


class GeneAberrationSet(Generic[Score]):
    """
    One set of gene aberrations of one specific type, from one data source.
    """

    def __init__(self, data_source, gene_scores: Mapping[Gene, Score]):
        assert data_source is not None
        assert gene_scores is not None
        self.__data_source = data_source
        self.__gene_scores = dict(gene_scores)

    @property
    def gene_scores(self) -> Iterable[Tuple[Gene,Score]]:
        return self.__gene_scores.items()

    @property
    def data_source(self):
        return self.__data_source
