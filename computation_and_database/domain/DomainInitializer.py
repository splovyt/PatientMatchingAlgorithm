from domain.state.Biology import Biology
from domain.state.Patient import Patient
from domain.state.SimilarPatientsComputationMethod import\
    SimilarPatientsComputationMethod
from domain.state.CancerType import CancerType
from domain.state.CancerSubtype import CancerSubtype
from domain.state.Gene import Gene
from domain.state.GeneAberrationSet import GeneAberrationSet
from typing import Iterable, Mapping
import csv
import numpy as np

class DomainInitializer:
    """
    Will initialize the domain objects that should be initialized
    by the domain package.
    This will mainly include connecting to the persistence layer
    and making sure everything happens in the right order.
    The biology and patients are initialized because they come from
    the database.
    The similar patients computation methods are initialized because
    the instances that have to be present can change (methods can be added), this change
    will then only affect the domain package.
    """
    def __init__(self):
        self.__biology = Biology()
        self.__similar_patients_computation_methods = set()
        self.__patients = set()
        self.__cancer_types = set()
        self.__cancer_subtypes = set()
        self.__read_ensembl_reactome()
        self.__read_brca_data()

    @property
    def biology(self) -> Biology:
        return self.__biology

    @property
    def persisted_patients(self) -> Iterable[Patient]:
        """
        The patients from the database.
        """
        return frozenset(self.__patients)

    @property
    def similar_patients_computation_methods(self)\
            -> Iterable[SimilarPatientsComputationMethod]:
        return frozenset(self.__similar_patients_computation_methods)

    @property
    def cancer_types(self) -> Iterable[CancerType]:
        return frozenset(self.__cancer_types)

    @property
    def cancer_subtypes(self) -> Iterable[CancerSubtype]:
        return frozenset(self.__cancer_subtypes)

    def __read_ensembl_reactome(self):
        filecontent = np.genfromtxt("data/ensembl_reactome.txt", delimiter='\t', dtype=np.str)

        reactome_no_headers = filecontent[1:]

        interaction_dict = dict()

        for interaction in reactome_no_headers:

            gene1 = self.__make_or_get_ensembl_gene(interaction[0])
            gene2 = self.__make_or_get_ensembl_gene(interaction[1])

            # We also exclude if two genes are the same, so no self loops included

            if gene1 != gene2:

                if gene1 not in interaction_dict:
                    interaction_dict[gene1] = set()

                interaction_dict[gene1].add(gene2)

                if gene2 not in interaction_dict:
                    interaction_dict[gene2] = set()

                interaction_dict[gene2].add(gene1)

        for gene in interaction_dict:
            gene_interacting_genes = interaction_dict[gene]
            gene.interacting_genes = gene_interacting_genes

    def __read_brca_data(self):
        breast_cancer = self.__add_breast_cancer()
        patient_per_name = dict()
        self.__read_brca_subtypes(breast_cancer, patient_per_name)
        self.__read_brca_expressions(patient_per_name)
        self.__read_brca_mutations(patient_per_name)
        self.__patients = patient_per_name.values()

    def __add_breast_cancer(self) -> CancerType:
        breast_cancer = CancerType()
        self.__cancer_types.add(breast_cancer)
        ct_m_nomenclature = self.__biology.cancer_type_metanomenclature
        ct_m_nomenclature.make_nomenclature("default")
        ct_nomenclature = ct_m_nomenclature.get_nomenclature("default")
        ct_nomenclature.add_names_for_object(["breast cancer"], breast_cancer)
        self.__cancer_types.add(breast_cancer)
        return breast_cancer

    def __read_brca_subtypes(self, breast_cancer: CancerType, patient_per_name: Mapping[str, Patient]):
        """
        :return: The patients per name.
        """

        with open('BRCAtestdata/BRCA_subtypes.txt', 'r') as subtypeFile:
            next(subtypeFile)
            subtype_reader = csv.reader(subtypeFile, delimiter='\t')
            for patient_name, subtype_name in subtype_reader:
                patient = Patient()
                patient.name = patient_name
                patient.cancer_subtype = self.__make_or_get_subtype(name=subtype_name, breast_cancer=breast_cancer)
                patient_per_name[patient_name] = patient

        return patient_per_name

    def __read_brca_expressions(self, patient_per_name: Mapping[str, Patient]):
        expressions_per_patient = dict()

        filename = 'BRCAtestdata/ens_BRCA_expressionset.txt'

        with open(filename, 'r') as expressionFile:
            next(expressionFile)
            expression_reader = csv.reader(expressionFile, delimiter='\t')
            for patient_name, expression, _, ensembl_id in expression_reader:
                if patient_name not in expressions_per_patient.keys():
                    expressions_per_patient[patient_name] = dict()
                gene = self.__make_or_get_ensembl_gene(ensembl_id)
                expressions_per_patient[patient_name][gene] = float(expression)

        for (patient_name, expressions) in expressions_per_patient.items():
            patient = patient_per_name['pat_'+ patient_name]
            patient.differential_expression_record.add_aberration_set(GeneAberrationSet(filename, expressions))

    def __read_brca_mutations(self, patient_per_name: Mapping[str, Patient]):

        mutations_per_patient = dict()
        filename = 'BRCAtestdata/ens_BRCA_mutationset.txt'

        with open(filename, 'r') as mutation_file:

            next(mutation_file)
            mutation_reader = csv.reader(mutation_file, delimiter='\t')

            for patient_name, vaf, _, ensembl_id in mutation_reader:
                if patient_name not in mutations_per_patient.keys():
                    mutations_per_patient[patient_name] = dict()
                gene = self.__make_or_get_ensembl_gene(ensembl_id)
                mutations_per_patient[patient_name][gene] = float(vaf)

        for (patient_name, mutations) in mutations_per_patient.items():
            patient = patient_per_name['pat_' + patient_name]
            patient.mutation_record.add_aberration_set(GeneAberrationSet(filename, mutations))

    def __make_or_get_subtype(self, name: str, breast_cancer: CancerType):
        cst_nomenclature = self.biology.cancer_subtype_metanomenclature.get_nomenclature("default")
        if cst_nomenclature is None:
            self.biology.cancer_subtype_metanomenclature.make_nomenclature("default")
            cst_nomenclature = self.biology.cancer_subtype_metanomenclature.get_nomenclature("default")

        subtype = cst_nomenclature.get_object_with_name(name)
        if subtype is None:
            subtype = CancerSubtype(breast_cancer)
            cst_nomenclature.add_names_for_object(new_names=[name], object=subtype)
            self.__cancer_subtypes.add(subtype)

        return subtype

    def __make_or_get_ensembl_gene(self, name: str) -> Gene:
        nomenclature = self.biology.gene_metanomenclature.get_nomenclature('ensembl')
        if nomenclature is None:
            self.biology.gene_metanomenclature.make_nomenclature('ensembl')
            nomenclature = self.biology.gene_metanomenclature.get_nomenclature('ensembl')

        gene = nomenclature.get_object_with_name(name)
        if gene is None:
            gene = Gene(self.biology)
            nomenclature.add_names_for_object(new_names=[name], object=gene)

        return gene


