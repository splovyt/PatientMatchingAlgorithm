import abc
from typing import Iterable


class GeneEventListener(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def gene_created(self, gene: 'Gene'):
        """
        Notify the listener that a gene was made.
        """


class Gene:

    def __init__(self, event_listener: GeneEventListener):
        assert event_listener is not None
        event_listener.gene_created(self)
        self.__interacting_genes = frozenset()

    @property
    def interacting_genes(self) -> Iterable['Gene']:
        return frozenset(self.__interacting_genes)

    @interacting_genes.setter
    def interacting_genes(self, interacting_genes: Iterable['Gene']):
        self.__interacting_genes = frozenset(interacting_genes)