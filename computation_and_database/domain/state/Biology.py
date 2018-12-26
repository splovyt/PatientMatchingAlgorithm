from domain.state.Gene import Gene as Gene
from domain.state.Gene import GeneEventListener as GeneEventListener
from domain.state.Metanomenclature import \
    Metanomenclature as Metanomenclature
from domain.state.CancerType import CancerType as CancerType
from domain.state.CancerSubtype import CancerSubtype as CancerSubtype
from typing import Iterable
from threading import RLock as RLock


class Biology (GeneEventListener):
    """
    __gene_per_id stores genes with their internal id
    """

    def __init__(self):
        self.__genes_lock = RLock()
        self.__genes = set()
        self.__gene_metanomenclature = Metanomenclature(Gene)
        self.__cancer_type_metanomenclature = Metanomenclature(CancerType)
        self.__cancer_subtype_metanomenclature = Metanomenclature(CancerSubtype)

    @property
    def gene_metanomenclature(self) -> Metanomenclature:
        return self.__gene_metanomenclature

    @property
    def cancer_type_metanomenclature(self) -> Metanomenclature:
        return self.__cancer_type_metanomenclature

    @property
    def cancer_subtype_metanomenclature(self) -> Metanomenclature:
        return self.__cancer_subtype_metanomenclature

    @property
    def genes(self) -> Iterable[Gene]:
        with self.__genes_lock:
            genes = frozenset(self.__genes)
        return genes

    def gene_created(self, gene: Gene):
        assert gene is not None
        with self.__genes_lock:
            assert gene not in self.__genes
            self.__genes.add(gene)