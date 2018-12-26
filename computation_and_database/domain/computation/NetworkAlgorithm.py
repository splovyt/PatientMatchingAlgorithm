from domain.computation.SimilarPatientsComputationMethod import SimilarPatientComputationMethod
from domain.state.SimilarPatient import SimilarPatient
from domain.state.Biology import Biology
from domain.state.SimilarPatientList import SimilarPatientList
from domain.state.Patient import Patient
from domain.DomainInitializer import DomainInitializer
import numpy as np
import datetime
from typing import Iterable

# PARAMETERS:
number_of_similar_patients = 7
filter_out_genes_not_in_interaction_network = True

mutation_vaf_threshold = 0.4
binary_expression_percentile = 1
# set the following to False when we don't want to use a database patient
# as main patient, but a 'real' input patient instead
test_database_patient_id = '2790b964-63e3-49aa-bf8c-9a00d3448c25'
test_database_patient_id = False

# Choose which method to use:
# 3 = Laplacian exponential diffusion kernel on the entire adjacency matrix
# 2 = Random walker on the entire adjacency matrix
# 1 = The simulated random walker (standard because very fast)
similar_patients_computation_method = 1
method_1_iterations = 10000
random_walker_reset_chance = 0.2
laplacian_exponential_diffusion_kernel_parameter = 0.05


class NetworkAlgorithm(SimilarPatientComputationMethod):
    def name(self):
        return 'NetworkAlgorithm'
    # FUNCTIONS THAT SHOULD BE REPLACED BY IMPORTING FROM STATES:
    def __import_reactome_interactions(self):
        '''
        1. Import the reactome interactions.
        2. Convert to dictionary and return in the following format:
        Every gene from the interaction network has the 'int_' prefix and is a key in the dictionary.
        The values of the keys are sets with the interaction partners.
        3. Go over every interacting node and collect all nodes that we will have to create in the
        self.all_nodes_collection
        NOTE: prefixes should be added when adding to the set.
        :return: {int_ENSG00000277075': {'int_ENSG00000159055', 'int_ENSG00000167491'}, ...}
        '''
        # print('importing reactome network')
        # filecontent = np.genfromtxt("data/ensembl_reactome.txt", delimiter='\t', dtype=np.str)
        # reactome_no_headers = filecontent[1:]
        #
        # interaction_dict = dict()
        # for interaction in reactome_no_headers:
        #     gene1 = interaction[0]
        #     gene2 = interaction[1]
        #
        #     # We also exclude if two genes are the same, so no self loops included
        #     if gene1 != gene2:
        #         gene1_ens = 'int_' + gene1
        #         gene2_ens = 'int_' + gene2
        #
        #         if gene1_ens in interaction_dict:
        #             interaction_dict[gene1_ens].update([gene2_ens])
        #         else:
        #             interaction_dict[gene1_ens] = set([gene2_ens])
        #
        #         if gene2_ens in interaction_dict:
        #             interaction_dict[gene2_ens].update([gene1_ens])
        #         else:
        #             interaction_dict[gene2_ens] = set([gene1_ens])
        interaction_dict =  dict()
        for gene_object in self.biology.genes:
            interacting_genes = gene_object.interacting_genes
            if interacting_genes != frozenset():
                gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                for gene_name in gene_names:
                    interaction_dict["int_" + gene_name] = set()
                    for interacting_gene_object in interacting_genes:
                        for interacting_gene_name in self.gene_nomenclature.get_names_for_object(interacting_gene_object):
                            interaction_dict["int_" + gene_name].update(["int_" + interacting_gene_name])

        print('amount of genes in interaction network: ', len(interaction_dict), '\n')

        print('collecting prior knowledge (interaction network) nodes')
        for gene_node in interaction_dict:
            gene_interacting_genes = interaction_dict[gene_node]
            self.all_nodes_collection.update([gene_node])
            for interacting_gene in gene_interacting_genes:
                self.all_nodes_collection.update([interacting_gene])

        return interaction_dict

    def __import_database_mutation_data(self, database_patients,
                                        filter=filter_out_genes_not_in_interaction_network,
                                        vaf_threshold=mutation_vaf_threshold):
        '''
        1. Import mutation data
        2. Combine the mutation data from different sources
        3. :param filter: If specified, filter out the genes that are not present in the interaction network.
        4. :param vaf_threshold: Make the data binary using a threshold on the vaf score.
        5. Go over every entry in the data and collect all nodes that we will create in the
        set self.all_nodes_collection and all the patient nodes in the set self.patient_nodes_collection
        NOTE: prefixes should be added when adding to the set.
        --> pat_ before a patient node
        --> mut_ before a mutated gene node
        6. While going over every entry, also create a dictionary linking the patients (keys) to a set of
        mutated genes (values)
        :return: the dictionary with patients as keys and corresponding set of mutated genes as value
        Example: {'pat_2c6f1862-bb82-4e7e-9cb3-338bdf022ff4': {'mut_ENSG00000185504'}, 'pat_35ceba07-0759-4fbe-b076-af821a528cf0': {'mut_ENSG00000128872', 'mut_ENSG00000196712', 'mut_ENSG00000173757'}}
        '''
        print('importing mutation data')
        patient_mutation_dict = dict()

        print('collecting patient & mutation nodes')
        # get database patients
        for patient in database_patients:
            patient_name = patient.name
            self.patient_name_object_dict[patient_name] = patient
            self.patient_nodes_collection.update([patient_name])
            for aberration_set in patient.mutation_record.aberration_sets:
                mutation_set = aberration_set.gene_scores
                if len(mutation_set) > 0:
                    for (gene_object, vaf) in mutation_set:
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    try:
                                        if float(vaf) >= vaf_threshold:
                                            if patient_name in patient_mutation_dict:
                                                patient_mutation_dict[patient_name].update(['mut_' + gene_name])
                                            else:
                                                patient_mutation_dict[patient_name] = set(['mut_' + gene_name])
                                            self.all_nodes_collection.update([patient_name])
                                            self.all_nodes_collection.update(['mut_' + gene_name])
                                    except:
                                        print('patient {} was not added to the mutation dict'.format(patient_name))
                            else:
                                try:
                                    if float(vaf) >= vaf_threshold:
                                        if patient_name in patient_mutation_dict:
                                            patient_mutation_dict[patient_name].update(['mut_' + gene_name])
                                        else:
                                            patient_mutation_dict[patient_name] = set(['mut_' + gene_name])
                                        self.all_nodes_collection.update([patient_name])
                                        self.all_nodes_collection.update(['mut_' + gene_name])
                                except:
                                    print('patient {} was not added to the mutation dict'.format(patient_name))
        return patient_mutation_dict
    def __import_database_expression_data(self, database_patients, filter=filter_out_genes_not_in_interaction_network,
                                    percentile=binary_expression_percentile):
        '''
        1. Import expression data
        2. Combine the expression data from different sources if necessary
        3. :param filter: If specified, filter out the genes that are not present in the interaction network.
        4. Go over every entry in the data and collect all nodes that we will create in the
        set self.all_nodes_collection and all the patient nodes in the set self.patient_nodes_collection
        NOTE: prefixes should be added when adding to the set.
        --> pat_ before a patient node
        --> exp_ before a differentially expressed gene node
        5. While going over every entry, also create a dictionary linking the patients (keys) to a set of
        DE genes (values)
        :return: the dictionary with patients as keys and corresponding set of DE genes as value
        Example: {'pat_2c6f1862-bb82-4e7e-9cb3-338bdf022ff4': {'exp_ENSG00000185504'}, 'pat_35ceba07-0759-4fbe-b076-af821a528cf0': {'exp_ENSG00000128872', 'exp_ENSG00000196712', 'exp_ENSG00000173757'}}
        '''
        # importing data and filtering based on reactome network
        print('importing expression data')

        print('collecting patient & mutation nodes')

        # make data binary
        # a. collect all values
        gene_expression_observation_dict = dict()
        for patient in database_patients:
            self.patient_name_object_dict[patient.name] = patient
            for aberration_set in patient.differential_expression_record.aberration_sets:
                expression_set = aberration_set.gene_scores
                if len(expression_set) > 0:
                    for (gene_object, expression_value) in expression_set:
                        assert expression_value == float(expression_value)
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    if gene_name not in gene_expression_observation_dict:
                                        gene_expression_observation_dict[gene_name] = [expression_value]
                                    else:
                                        gene_expression_observation_dict[gene_name].append(expression_value)
                            else:
                                if gene_name not in gene_expression_observation_dict:
                                    gene_expression_observation_dict[gene_name] = [expression_value]
                                else:
                                    gene_expression_observation_dict[gene_name].append(expression_value)
        # b. define gene thresholds based on the chosen percentiles
        self.gene_threshold_dict = dict()
        for gene in gene_expression_observation_dict:
            all_expression_values = np.array(gene_expression_observation_dict[gene])
            low_perc = np.percentile(all_expression_values, percentile)
            median_perc = np.percentile(all_expression_values, 50)
            high_perc = np.percentile(all_expression_values, (100 - percentile))

            low_diff = abs(median_perc - low_perc)
            high_diff = abs(high_perc - median_perc)
            # find smallest difference and mirror it
            if low_diff <= high_diff:
                lower_bound = low_perc
                upper_bound = median_perc + low_diff
                bound_type = 'overexpression'
                bound = upper_bound
            else:
                lower_bound = median_perc - high_diff
                upper_bound = high_perc
                bound_type = 'underexpression'
                bound = lower_bound
            self.gene_threshold_dict[gene] = (bound_type, bound)

        # add the nodes and link patient to DE genes
        patient_expression_dict = dict()
        print('collecting patient & DE nodes')
        for patient in database_patients:
            patient_name = patient.name
            self.patient_nodes_collection.update([patient_name])
            for aberration_set in patient.differential_expression_record.aberration_sets:
                expression_set = aberration_set.gene_scores
                if len(expression_set) > 0:
                    for (gene_object, expression_value) in expression_set:
                        assert expression_value == float(expression_value)
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            self.all_nodes_collection.update([patient_name])
                            self.all_nodes_collection.update(['exp_' + gene_name])
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    (bound_type, bound) = self.gene_threshold_dict[gene_name]
                                    if bound_type == 'overexpression':
                                        if float(expression_value) >= bound:
                                            if patient_name in patient_expression_dict:
                                                patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                            else:
                                                patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                                    elif bound_type == 'underexpression':
                                        if float(expression_value) <= bound:
                                            if patient in patient_expression_dict:
                                                patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                            else:
                                                patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                            else:
                                (bound_type, bound) = self.gene_threshold_dict[gene_name]
                                if bound_type == 'overexpression':
                                    if float(expression_value) >= bound:
                                        if patient_name in patient_expression_dict:
                                            patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                        else:
                                            patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                                elif bound_type == 'underexpression':
                                    if float(expression_value) <= bound:
                                        if patient in patient_expression_dict:
                                            patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                        else:
                                            patient_expression_dict[patient_name] = set(['exp_' + gene_name])

        ##
        # print('importing expression data from {}'.format(filepath))
        # filecontent = np.genfromtxt(filepath, delimiter="\t", dtype=np.str)
        # database_expression_data = filecontent[1:]
        # if filter:
        #     filtered_data = []
        #     for data_entry in database_expression_data:
        #         if ('int_' + data_entry[3]) in self.reactome_interaction_network:
        #             filtered_data.append(data_entry)
        # database_expression_data = np.array(filtered_data)
        #
        # # make data binary
        # # a. collect all values
        # gene_expression_observation_dict = dict()
        # for entry in database_expression_data:
        #     gene = entry[3]
        #     expression_value = float(entry[1])
        #     if gene not in gene_expression_observation_dict:
        #         gene_expression_observation_dict[gene] = [expression_value]
        #     else:
        #         gene_expression_observation_dict[gene].append(expression_value)
        # # b. define gene thresholds based on the chosen percentiles
        # gene_threshold_dict = dict()
        # for gene in gene_expression_observation_dict:
        #     all_expression_values = np.array(gene_expression_observation_dict[gene])
        #     low_perc = np.percentile(all_expression_values, percentile)
        #     median_perc = np.percentile(all_expression_values, 50)
        #     high_perc = np.percentile(all_expression_values, (100-percentile))
        #
        #     low_diff = abs(median_perc - low_perc)
        #     high_diff = abs(high_perc - median_perc)
        #     # find smallest difference and mirror it
        #     if low_diff <= high_diff:
        #         lower_bound = low_perc
        #         upper_bound = median_perc + low_diff
        #         bound_type = 'overexpression'
        #         bound = upper_bound
        #     else:
        #         lower_bound = median_perc - high_diff
        #         upper_bound = high_perc
        #         bound_type = 'underexpression'
        #         bound = lower_bound
        #     gene_threshold_dict[gene] = (bound_type, bound)
        #
        # # add the nodes and link patient to DE genes
        # patient_expression_dict = dict()
        # print('collecting patient & DE nodes')
        # for entry in database_expression_data:
        #
        #     # update collection of patient nodes
        #     patient = 'pat_' + entry[0]
        #     self.patient_nodes_collection.update([patient])
        #
        #     # extract expression value
        #     expression_value = entry[1]
        #
        #     # making sure there is an ensembl id, because this doesnt always seem to be the case
        #     if 'ENS' in entry[3]:
        #         ensembl_id = 'exp_' + entry[3]
        #
        #         # add patient node and gene node to the set
        #         self.all_nodes_collection.update([patient])
        #         self.all_nodes_collection.update([ensembl_id])
        #
        #
        #         # link patient to gene if gene is DE (one way only)
        #         (bound_type, bound) = gene_threshold_dict[entry[3]]
        #         if bound_type == 'overexpression':
        #             if float(expression_value) >= bound:
        #                 if patient in patient_expression_dict:
        #                     patient_expression_dict[patient].update([ensembl_id])
        #                 else:
        #                     patient_expression_dict[patient] = set([ensembl_id])
        #         elif bound_type == 'underexpression':
        #             if float(expression_value) <= bound:
        #                 if patient in patient_expression_dict:
        #                     patient_expression_dict[patient].update([ensembl_id])
        #                 else:
        #                     patient_expression_dict[patient] = set([ensembl_id])
        return patient_expression_dict
    def __import_database_cnv_data(self,
                                   filter=filter_out_genes_not_in_interaction_network):
        '''
        1. Import copy number abberation data
        2. Combine the copy number abberation data from different sources if necessary
        3. :param filter: If specified, filter out the genes that are not present in the interaction network.
        4. Go over every entry in the data and collect all nodes that we will create in the
        set self.all_nodes_collection and all the patient nodes in the set self.patient_nodes_collection
        NOTE: prefixes should be added when adding to the set.
        --> pat_ before a patient node
        --> cnv_ before a cnv gene node
        5. While going over every entry, also create a dictionary linking the patients (keys) to a set of
        cnv genes (values)
        :return: the dictionary with patients as keys and corresponding set of cnv genes as value
        Example: {'pat_2c6f1862-bb82-4e7e-9cb3-338bdf022ff4': {'cnv_ENSG00000185504'}, 'pat_35ceba07-0759-4fbe-b076-af821a528cf0': {'cnv_ENSG00000128872', 'cnv_ENSG00000196712', 'cnv_ENSG00000173757'}}
        '''
        return {}
    def __import_database_methylation_data(self,
                                           filter=filter_out_genes_not_in_interaction_network):
        '''
        1. Import methylation data
        2. Combine the methylation data from different sources if necessary
        3. :param filter: If specified, filter out the genes that are not present in the interaction network.
        4. Go over every entry in the data and collect all nodes that we will create in the
        set self.all_nodes_collection and all the patient nodes in the set self.patient_nodes_collection
        NOTE: prefixes should be added when adding to the set.
        --> pat_ before a patient node
        --> met_ before a methylated gene node
        5. While going over every entry, also create a dictionary linking the patients (keys) to a set of
        methylated genes (values)
        :return: the dictionary with patients as keys and corresponding set of methylated genes as value
        Example: {'pat_2c6f1862-bb82-4e7e-9cb3-338bdf022ff4': {'met_ENSG00000185504'}, 'pat_35ceba07-0759-4fbe-b076-af821a528cf0': {'met_ENSG00000128872', 'met_ENSG00000196712', 'met_ENSG00000173757'}}
        '''
        return {}

    def __import_main_patient(self, main_patient_object, filter=filter_out_genes_not_in_interaction_network,
                                    vaf_threshold = mutation_vaf_threshold, percentile=binary_expression_percentile):
        '''
        Import genome abberation sets from the input patient and return the preprocessed
        information in a dictionary.
        If we still need to preprocess (make data binary etc.)
        we have to make sure we use the same parameters as in the other methods.

        :param database_patient_id: If there is a database patient ID specified, it means that we are
        performing a test and that we will take the abberation data from the database.

        :return: A dictionary with the following structure:
        {'mutation_data' : set(mut_g1, mut_g2,..),
         'expression_data' : set(),
         'cnv_data' : set(),
         'methylation_data' : set()}
        '''
        main_patient_mutation_data = set()
        main_patient_expression_data = set()
        main_patient_cnv_data = set()
        main_patient_methylation_data = set()

        # MUTATIONS
        for aberration_set in main_patient_object.mutation_record.aberration_sets:
            mutation_set = aberration_set.gene_scores
            if len(mutation_set) > 0:
                for (gene_object, vaf) in mutation_set:
                    gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                    for gene_name in gene_names:
                        assert 'ENS' in gene_name
                        if filter:
                            if ('int_' + gene_name) in self.reactome_interaction_network:
                                if float(vaf) >= vaf_threshold:
                                    main_patient_mutation_data.update(['mut_' + gene_name])
                        else:
                            if float(vaf) >= vaf_threshold:
                                main_patient_mutation_data.update(['mut_' + gene_name])

        # EXPRESSION
        for aberration_set in main_patient.differential_expression_record.aberration_sets:
            expression_set = aberration_set.gene_scores
            if len(expression_set) > 0:
                for (gene_object, expression_value) in expression_set:
                    assert expression_value == float(expression_value)
                    gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                    for gene_name in gene_names:
                        assert 'ENS' in gene_name
                        if filter:
                            if ('int_' + gene_name) in self.reactome_interaction_network:
                                (bound_type, bound) = self.gene_threshold_dict[gene_name]
                                if bound_type == 'overexpression':
                                    if float(expression_value) >= bound:
                                        main_patient_expression_data.update(['exp_' + gene_name])
                                elif bound_type == 'underexpression':
                                    if float(expression_value) <= bound:
                                        main_patient_expression_data.update(['exp_' + gene_name])
                        else:
                            (bound_type, bound) = self.gene_threshold_dict[gene_name]
                            if bound_type == 'overexpression':
                                if float(expression_value) >= bound:
                                    main_patient_expression_data.update(['exp_' + gene_name])
                            elif bound_type == 'underexpression':
                                if float(expression_value) <= bound:
                                    main_patient_expression_data.update(['exp_' + gene_name])

        return {'mutation_data': main_patient_mutation_data,
                'expression_data': main_patient_expression_data,
                'cnv_data': main_patient_cnv_data,
                'methylation_data': main_patient_methylation_data}
        # main_patient_mutation_data = set()
        # main_patient_expression_data = set()
        # main_patient_cnv_data = set()
        # main_patient_methylation_data = set()
        #
        # if database_patient_id != 'MAIN_PATIENT':
        #     # We need to take a database patient
        #     database_patient_id = 'pat_' + database_patient_id
        #     if database_patient_id in self.database_mutation_dict:
        #         main_patient_mutation_data = self.database_mutation_dict[database_patient_id]
        #     if database_patient_id in self.database_expression_dict:
        #         main_patient_expression_data = self.database_expression_dict[database_patient_id]
        #     if database_patient_id in self.database_cnv_dict:
        #         main_patient_cnv_data = self.database_cnv_dict[database_patient_id]
        #     if database_patient_id in self.database_methylation_dict:
        #         main_patient_methylation_data = self.database_methylation_dict[database_patient_id]
        #
        #     return {'mutation_data': main_patient_mutation_data,
        #      'expression_data': main_patient_expression_data,
        #      'cnv_data': main_patient_cnv_data,
        #      'methylation_data': main_patient_methylation_data}
        #
        # elif database_patient_id == 'MAIN_PATIENT':
        #     # Insert import from state here:
        #     raise ValueError('Importing the main patient from the states is not implemented yet!')
        #
        #     # We need to import the input patient (= main patient)
        #     return {'mutation_data': main_patient_mutation_data,
        #             'expression_data': main_patient_expression_data,
        #             'cnv_data': main_patient_cnv_data,
        #             'methylation_data': main_patient_methylation_data}
    def __import_patient_subtypes_into_dict(self):
        '''
        Returns a dictionary with as key the patient id and as value the subtype
        :param subtypes_filepath: Should be replaced by state import later.
        :return: Dictionary with keys the patients and values their cancer subtype.
        '''
        BRCA_patient_subtypes_dict = dict()
        database_patients = self.domain_initializer.persisted_patients
        for patient in database_patients:
            subtype = self.subtype_nomenclature.get_names_for_object(patient.cancer_subtype)
            assert subtype is not frozenset()
            BRCA_patient_subtypes_dict[patient.name] = subtype
        return BRCA_patient_subtypes_dict
        # BRCA_patient_subtypes = np.genfromtxt(BRCA_patient_subtypes_filepath, delimiter="\t",
        #                                           dtype=np.str)[1:]
        # BRCA_patient_subtypes_dict = dict()
        # for entry in BRCA_patient_subtypes:
        #     BRCA_patient_subtypes_dict[entry[0]] = entry[1]
        # return BRCA_patient_subtypes_dict
    def __import_BRCA_mutation_file(self,filter=filter_out_genes_not_in_interaction_network,
                                    vaf_threshold = mutation_vaf_threshold):


        '''
        :param filepath: The filepath to the BRCA mutation file.
        :return: The mutation data converted to a np.array.
        '''

        print('importing mutation data')
        patient_mutation_dict = dict()

        print('collecting patient & mutation nodes')
        # get database patients
        database_patients = self.domain_initializer.persisted_patients
        for patient in database_patients:
            patient_name = patient.name
            self.patient_nodes_collection.update([patient_name])
            for aberration_set in patient.mutation_record.aberration_sets:
                mutation_set = aberration_set.gene_scores
                if len(mutation_set) > 0:
                    for (gene_object, vaf) in mutation_set:
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    try:
                                        if float(vaf) >= vaf_threshold:
                                            if patient_name in patient_mutation_dict:
                                                patient_mutation_dict[patient_name].update(['mut_' + gene_name])
                                            else:
                                                patient_mutation_dict[patient_name] = set(['mut_' + gene_name])
                                            self.all_nodes_collection.update([patient_name])
                                            self.all_nodes_collection.update(['mut_' + gene_name])
                                    except:
                                        print('patient {} was not added to the mutation dict'.format(patient_name))
                            else:
                                try:
                                    if float(vaf) >= vaf_threshold:
                                        if patient_name in patient_mutation_dict:
                                            patient_mutation_dict[patient_name].update(['mut_' + gene_name])
                                        else:
                                            patient_mutation_dict[patient_name] = set(['mut_' + gene_name])
                                        self.all_nodes_collection.update([patient_name])
                                        self.all_nodes_collection.update(['mut_' + gene_name])
                                except:
                                    print('patient {} was not added to the mutation dict'.format(patient_name))
        return patient_mutation_dict
        # print('importing mutation data')
        # filecontent = np.genfromtxt(filepath, delimiter="\t", dtype=np.str)
        # matrix = filecontent[1:]
        # database_mutation_data = [matrix]
        # if filter:
        #     filtered_data = []
        #     for subdata in database_mutation_data:
        #         filtered_subdata = []
        #         for data_entry in subdata:
        #             if ('int_' + data_entry[3]) in self.reactome_interaction_network:
        #                 filtered_subdata.append(data_entry)
        #         filtered_data.append(np.array(filtered_subdata, dtype='<U36'))
        #     database_mutation_data = np.array(filtered_data)
        # print('collecting patient & mutation nodes')
        # patient_mutation_dict = dict()
        # for subdata in database_mutation_data:
        #     for data_entry in subdata:
        #         # add prefix
        #         patient = 'pat_' + data_entry[0]
        #         # update collection of patient nodes
        #         self.patient_nodes_collection.update([patient])
        #         # extract vaf score
        #         vaf = data_entry[1]
        #         # making sure there is an ensembl id, because this doesnt always seem to be the case
        #         if 'ENS' in data_entry[3]:
        #             ensembl_id = 'mut_' + data_entry[3]
        #
        #             # add patient node and gene node to the set
        #             self.all_nodes_collection.update([patient])
        #             self.all_nodes_collection.update([ensembl_id])
        #
        #             # link patient to mutation
        #             try:  # sometimes there is an error in the vaf number, the number is blank or NA or ...
        #                 if float(vaf) >= vaf_threshold:
        #                     if patient in patient_mutation_dict:
        #                         patient_mutation_dict[patient].update([ensembl_id])
        #                     else:
        #                         patient_mutation_dict[patient] = set([ensembl_id])
        #             except:
        #                 print('The following patient was not added to the mutation dict: ', patient)
        #                 pass
        # return patient_mutation_dict

    def __import_BRCA_expression_file(self,filter=filter_out_genes_not_in_interaction_network,
                                    percentile=binary_expression_percentile):

        '''
        :param filepath: The filepath to the BRCA expression file.
        :return: The expression data made binary and converted to a np.array.
        '''
        # importing data and filtering based on reactome network
        print('importing expression data')

        print('collecting patient & mutation nodes')
        # get database patients
        database_patients = self.domain_initializer.persisted_patients

        # make data binary
        # a. collect all values
        gene_expression_observation_dict = dict()
        for patient in database_patients:
            for aberration_set in patient.differential_expression_record.aberration_sets:
                expression_set = aberration_set.gene_scores
                if len(expression_set) > 0:
                    for (gene_object, expression_value) in expression_set:
                        assert expression_value == float(expression_value)
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    if gene_name not in gene_expression_observation_dict:
                                        gene_expression_observation_dict[gene_name] = [expression_value]
                                    else:
                                        gene_expression_observation_dict[gene_name].append(expression_value)
                            else:
                                if gene_name not in gene_expression_observation_dict:
                                    gene_expression_observation_dict[gene_name] = [expression_value]
                                else:
                                    gene_expression_observation_dict[gene_name].append(expression_value)
        # b. define gene thresholds based on the chosen percentiles
        self.gene_threshold_dict = dict()
        for gene in gene_expression_observation_dict:
            all_expression_values = np.array(gene_expression_observation_dict[gene])
            low_perc = np.percentile(all_expression_values, percentile)
            median_perc = np.percentile(all_expression_values, 50)
            high_perc = np.percentile(all_expression_values, (100-percentile))

            low_diff = abs(median_perc - low_perc)
            high_diff = abs(high_perc - median_perc)
            # find smallest difference and mirror it
            if low_diff <= high_diff:
                lower_bound = low_perc
                upper_bound = median_perc + low_diff
                bound_type = 'overexpression'
                bound = upper_bound
            else:
                lower_bound = median_perc - high_diff
                upper_bound = high_perc
                bound_type = 'underexpression'
                bound = lower_bound
            self.gene_threshold_dict[gene] = (bound_type, bound)

        # add the nodes and link patient to DE genes
        patient_expression_dict = dict()
        print('collecting patient & DE nodes')
        for patient in database_patients:
            patient_name = patient.name
            self.patient_nodes_collection.update([patient_name])
            for aberration_set in patient.differential_expression_record.aberration_sets:
                expression_set = aberration_set.gene_scores
                if len(expression_set) > 0:
                    for (gene_object, expression_value) in expression_set:
                        assert expression_value == float(expression_value)
                        gene_names = self.gene_nomenclature.get_names_for_object(gene_object)
                        for gene_name in gene_names:
                            assert 'ENS' in gene_name
                            self.all_nodes_collection.update([patient_name])
                            self.all_nodes_collection.update(['exp_' + gene_name])
                            if filter:
                                if ('int_' + gene_name) in self.reactome_interaction_network:
                                    (bound_type, bound) = self.gene_threshold_dict[gene_name]
                                    if bound_type == 'overexpression':
                                        if float(expression_value) >= bound:
                                            if patient_name in patient_expression_dict:
                                                patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                            else:
                                                patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                                    elif bound_type == 'underexpression':
                                        if float(expression_value) <= bound:
                                            if patient in patient_expression_dict:
                                                patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                            else:
                                                patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                            else:
                                (bound_type, bound) = self.gene_threshold_dict[gene_name]
                                if bound_type == 'overexpression':
                                    if float(expression_value) >= bound:
                                        if patient_name in patient_expression_dict:
                                            patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                        else:
                                            patient_expression_dict[patient_name] = set(['exp_' + gene_name])
                                elif bound_type == 'underexpression':
                                    if float(expression_value) <= bound:
                                        if patient in patient_expression_dict:
                                            patient_expression_dict[patient_name].update(['exp_' + gene_name])
                                        else:
                                            patient_expression_dict[patient_name] = set(['exp_' + gene_name])

        ##
        # print('importing expression data from {}'.format(filepath))
        # filecontent = np.genfromtxt(filepath, delimiter="\t", dtype=np.str)
        # database_expression_data = filecontent[1:]
        # if filter:
        #     filtered_data = []
        #     for data_entry in database_expression_data:
        #         if ('int_' + data_entry[3]) in self.reactome_interaction_network:
        #             filtered_data.append(data_entry)
        # database_expression_data = np.array(filtered_data)
        #
        # # make data binary
        # # a. collect all values
        # gene_expression_observation_dict = dict()
        # for entry in database_expression_data:
        #     gene = entry[3]
        #     expression_value = float(entry[1])
        #     if gene not in gene_expression_observation_dict:
        #         gene_expression_observation_dict[gene] = [expression_value]
        #     else:
        #         gene_expression_observation_dict[gene].append(expression_value)
        # # b. define gene thresholds based on the chosen percentiles
        # gene_threshold_dict = dict()
        # for gene in gene_expression_observation_dict:
        #     all_expression_values = np.array(gene_expression_observation_dict[gene])
        #     low_perc = np.percentile(all_expression_values, percentile)
        #     median_perc = np.percentile(all_expression_values, 50)
        #     high_perc = np.percentile(all_expression_values, (100-percentile))
        #
        #     low_diff = abs(median_perc - low_perc)
        #     high_diff = abs(high_perc - median_perc)
        #     # find smallest difference and mirror it
        #     if low_diff <= high_diff:
        #         lower_bound = low_perc
        #         upper_bound = median_perc + low_diff
        #         bound_type = 'overexpression'
        #         bound = upper_bound
        #     else:
        #         lower_bound = median_perc - high_diff
        #         upper_bound = high_perc
        #         bound_type = 'underexpression'
        #         bound = lower_bound
        #     gene_threshold_dict[gene] = (bound_type, bound)
        #
        # # add the nodes and link patient to DE genes
        # patient_expression_dict = dict()
        # print('collecting patient & DE nodes')
        # for entry in database_expression_data:
        #
        #     # update collection of patient nodes
        #     patient = 'pat_' + entry[0]
        #     self.patient_nodes_collection.update([patient])
        #
        #     # extract expression value
        #     expression_value = entry[1]
        #
        #     # making sure there is an ensembl id, because this doesnt always seem to be the case
        #     if 'ENS' in entry[3]:
        #         ensembl_id = 'exp_' + entry[3]
        #
        #         # add patient node and gene node to the set
        #         self.all_nodes_collection.update([patient])
        #         self.all_nodes_collection.update([ensembl_id])
        #
        #
        #         # link patient to gene if gene is DE (one way only)
        #         (bound_type, bound) = gene_threshold_dict[entry[3]]
        #         if bound_type == 'overexpression':
        #             if float(expression_value) >= bound:
        #                 if patient in patient_expression_dict:
        #                     patient_expression_dict[patient].update([ensembl_id])
        #                 else:
        #                     patient_expression_dict[patient] = set([ensembl_id])
        #         elif bound_type == 'underexpression':
        #             if float(expression_value) <= bound:
        #                 if patient in patient_expression_dict:
        #                     patient_expression_dict[patient].update([ensembl_id])
        #                 else:
        #                     patient_expression_dict[patient] = set([ensembl_id])
        return patient_expression_dict

    # OTHER PRIVATE FUNCTIONS THAT DO NOT HAVE TO BE REPlACED:
    def __create_node_index_list(self):
        '''
        Make a dictionary with the index of every node in the adjacency matrix.
        :return: The dictionary. Keys are the nodes and the values the positions.
        Example: {'mut_ENSG00000011465': 8613, 'mut_ENSG00000159720': 13356, 'int_ENSG00000068745': 535, 'pat_e45f3391-2e74-4767-817a-280cebac7c57': 18509}
        '''
        sorted_all_nodes_list = sorted(list(self.all_nodes_collection))
        index = 0
        node_indices = dict()
        # Matrix is symmetric. Thus, we do not need two coordinates.
        for node in sorted_all_nodes_list:
            node_indices[node] = index
            index += 1
        return node_indices
    def __reverse_dictionary(self, dictionary):
        '''
        :return: The reverse of the input dictionary (keys -> values and values -> keys).
        '''
        reverse_dict = dict()
        for key in dictionary:
            value = dictionary[key]
            reverse_dict[value] = key
        return reverse_dict
    def __fill_adjacency_matrix_with_data_dictionary(self, matrix, data_dictionary):
        '''
        Add every connection in the data dictionary to the adjacency matrix
        :param matrix: The adjacency matrix
        :param data_dictionary: The dictionary where patients are the keys and the gene abberations sets the values.
        :return: updated adjacency matrix
        '''
        for patient in data_dictionary:
            gene_abberation_set = data_dictionary[patient]
            patient_coordinate = self.node_coordinates[patient]
            for gene in gene_abberation_set:
                gene_coordinate = self.node_coordinates[gene]
                # now fill in (symmetric so also the other way around)
                matrix[patient_coordinate][gene_coordinate] = 1
                matrix[gene_coordinate][patient_coordinate] = 1
        return matrix
    def __connecting_gene_nodes_by_interaction_network(self, matrix):
        '''
        Completing the adjacency matrix by interconnecting the gene nodes through
        the info stored in the interaction network.
        NOTE: Different version of a gene will never be directly connected. For example, the mutated version
        of a gene will not be connected to the differentially expressed version of the gene.
        However, for example the mut_ and exp_ versions of the genes are both connected to the
        interaction network version (int_ version of the gene).
        NOTE2: Patients will also never be interconnected.
        :return: The updated adjacency matrix.
        '''
        for gene_node in self.reactome_interaction_network:
            interacting_genes = self.reactome_interaction_network[gene_node]
            # A. Interconnecting the genes from the interaction network (int_ prefix)
            for interacting_gene_node in interacting_genes:
                gene_node_coordinate = self.node_coordinates[gene_node]
                interacting_gene_node_coordinate = self.node_coordinates[interacting_gene_node]
                # now fill in (symmetric so both ways)
                matrix[gene_node_coordinate][interacting_gene_node_coordinate] = 1
                matrix[interacting_gene_node_coordinate][gene_node_coordinate] = 1

            # B. Connecting the genes from the interacting network (int_ genes)
            # with the other versions of the same gene
            # (connect int_ genes with the mut_, exp_, cnv_ and met_ versions of the same gene)
            for data_type_prefix in ['mut_', 'exp_', 'cnv_', 'met_']:  # here add the data type prefixes
                gene_node_interaction_network = gene_node
                gene_node_other_datatype = data_type_prefix + gene_node[4:]

                if gene_node_other_datatype in self.node_coordinates:  # only if the node in other datatype exists
                    gene_node_interaction_network_coordinate = self.node_coordinates[gene_node_interaction_network]
                    gene_node_other_datatype_coordinate = self.node_coordinates[gene_node_other_datatype]

                    # now fill in (symmetric so both ways)
                    matrix[gene_node_interaction_network_coordinate][gene_node_other_datatype_coordinate] = 1
                    matrix[gene_node_other_datatype_coordinate][gene_node_interaction_network_coordinate] = 1
        return matrix
    def __add_new_patient_to_adjacency_matrix(self):
        '''
        :param adjacency_matrix: The precalculated adjacency matrix.
        :param node_coordinates: The indices of every node in the adjacency matrix.
        :param main_patient_id: The ID of the patient under study.
        :param main_patient_data_dict: {'mutation_data' : {mut_gene1, mut_gene2,..}, 'expression_data' : {}, 'cnv_data' : {}, 'methylation_data' : {}}
        :return: The adjacency matrix with the new patient added and the new coordinates dictionary.
        '''
        # Find the dimensions of the numpy array
        r, c = self.adjacency_matrix.shape

        # and blank column and row to the end of the matrix
        adjacency_matrix_with_new_patient = self.adjacency_matrix
        node_coordinates_with_new_patient = self.node_coordinates
        blank_col = np.zeros((r, 1))
        adjacency_matrix_with_new_patient = np.append(adjacency_matrix_with_new_patient, blank_col, axis=1)
        blank_row = np.zeros((1, c + 1))
        adjacency_matrix_with_new_patient = np.append(adjacency_matrix_with_new_patient, blank_row, axis=0)

        # the index of the last column/row (symmetric) are the coordinates of the new patient
        main_patient_coordinate = r
        node_coordinates_with_new_patient[self.main_patient_id] = main_patient_coordinate

        # add the connection to the existing nodes for every data type
        for data_type in ['mutation_data', 'expression_data', 'cnv_data', 'methylation_data']:
            affected_geneset = self.main_patient_data_dict[data_type]
            if affected_geneset != set():  # check if there is actually data available
                for prefix_ensembl_gene_id in affected_geneset:
                    if (prefix_ensembl_gene_id) in self.node_coordinates:
                        connection_position = node_coordinates_with_new_patient[prefix_ensembl_gene_id]
                        adjacency_matrix_with_new_patient[connection_position][main_patient_coordinate] = 1
                        adjacency_matrix_with_new_patient[main_patient_coordinate][connection_position] = 1
        return adjacency_matrix_with_new_patient, node_coordinates_with_new_patient
    def __simulated_random_walker(self):
        '''
        Simulate a random walker starting from the main patient node. This is the standard
        method to find similar patients because of the low resources required.

        NOTE: The main patient will NOT be counted!
        :return: Sorted list of patients based on number of occurence of other patient nodes by random walks.
        '''
        print('calculating the patients similar to patient {} with random walks'.format(self.main_patient_id))
        import random
        nearby_patient_count_dict = dict()
        for i in range(0, method_1_iterations):
            # find the connections to other nodes from the starting patient
            node_index = self.node_coordinates_with_main_patient[self.main_patient_id]
            while True:
                # pick random connected node (1) and set current node to this node
                node_connectivity = self.adjacency_matrix_with_main_patient[:, node_index]
                connections = np.where(node_connectivity == 1)[0]
                if len(connections) == 0:
                    print('No connections to other nodes could be made from the input patient..')
                    break
                next_node_index = random.choice(connections)
                node_index = next_node_index

                # Check if current node is patient, if yes increase count in dictionary
                node_name = self.node_coordinates_with_main_patient_reverse[node_index]
                if node_name[0:4] == 'pat_' and node_name != self.main_patient_id and node_name != ('pat_' + self.main_patient_id):
                    if node_name not in nearby_patient_count_dict:
                        nearby_patient_count_dict[node_name] = 1
                    else:
                        nearby_patient_count_dict[node_name] += 1

                # Now check if we keep continuing from the current node or stop
                if random.uniform(0, 1) <= random_walker_reset_chance:
                    break

        # sort found patients based on occurence count
        sorted_patients_list = sorted(nearby_patient_count_dict.items(), key=lambda t: t[1], reverse=1)
        return sorted_patients_list
    def __find_connected_patients_list(self, K):
        '''
        1. Extract row of the input patient.
        2. Go over the values in the row.
        3. If we encounter a value bigger than 0 (after rounding because numeric problems), we know the node is
           connected to our input patient.
        4. Check if the node is a patient node. If yes, collect the value together with the node label.
        5. Sort the connected patients based on their connectivity.

        NOTE: The input patient will not be in the returned list!

        :param K:
        :return: A sorted list of patients with their scores.
        EXAMPLE:
        [(pat_3, 309), (pat_1, 205), (pat_2, 24)]
        '''
        connectivity_scores_of_main_patient = K[self.node_coordinates_with_main_patient[self.main_patient_id]]
        connected_patient_score_list = {}
        for index in range(0, len(connectivity_scores_of_main_patient)):
            connectivy_of_node = connectivity_scores_of_main_patient[index]
            if round(connectivy_of_node, 10) > 0:
                node_label = self.node_coordinates_with_main_patient_reverse[index]
                if node_label[0:4] == 'pat_':
                    if node_label != self.main_patient_id and node_label != 'pat_' + self.main_patient_id:
                        connected_patient_score_list[node_label] = connectivy_of_node

        sorted_patients_list = sorted(connected_patient_score_list.items(), key=lambda t: t[1], reverse=1)
        return sorted_patients_list
    def __adjacency_random_walker_matrix(self):
        '''
        Random walker method applied to the entire adjacency matrix
        to return a list with connected patients sorted
        on their connectivity to the main patient.
        The higher the score, the more 'similar' to the input patient.

        NOTE: The main patient will NOT be counted!

        MATLAB IMPLEMENTATION:
        case 'RWR'
            Ds=sum(A,2);
            D=diag(Ds);
            a=param1;
            K=(D-a*A)^(-1)*D;
        '''
        print('Calculating random walks on the entire adjacency matrix..')
        Ds = np.sum(self.adjacency_matrix_with_main_patient, axis=1)
        D = np.diag(Ds)
        K = np.dot(np.linalg.pinv(D - random_walker_reset_chance * self.adjacency_matrix_with_main_patient), D)
        return K
    def __adjacency_laplacian_exponential_diffusion_kernel_matrix(self):
        '''
        Apply the laplacian exponential diffusion kernel to the entire
        adjacency matrix and return a list with connected patients sorted
        on their connectivity to the main patient.
        The higher the score, the more 'similar' to the input patient.

        NOTE: The main patient will NOT be counted!

        MATLAB IMPLEMENTATION:
        case 'LEXP'
            L = laplacian(A);
            K = expm(-param1 * L)
        '''
        print('Calculating laplacian exponential diffusion kernel on the entire adjacency matrix..')
        from scipy.sparse import csgraph
        import scipy.linalg
        L = csgraph.laplacian(self.adjacency_matrix_with_main_patient)
        K = scipy.linalg.expm(-laplacian_exponential_diffusion_kernel_parameter * L)
        return K
    def __list_similar_patients(self, method=1):
        '''
        :param method:
        :param max_number:
        :return:
        '''
        if method == 1: # The simulated random walker
            similar_patients_list = self.__simulated_random_walker()

        elif method == 2:
            converted_matrix = self.__adjacency_random_walker_matrix()
            similar_patients_list = self.__find_connected_patients_list(converted_matrix)
            del converted_matrix

        elif method == 3:
            converted_matrix = self.__adjacency_laplacian_exponential_diffusion_kernel_matrix()
            similar_patients_list = self.__find_connected_patients_list(converted_matrix)
            del converted_matrix

        return similar_patients_list


    def __backup_data_variable_content(self):
        '''
        Make a backup in the self.backup variable of the following 'important' precalculated variables:
        - self.all_nodes_collection:
        - self.patient_nodes_collection:
        - self.reactome_interaction_network:
        - self.database_mutation_dict:
        - self.database_expression_dict:
        - self.database_cnv_dict:
        - self.database_methylation_dict:
        - self.node_coordinates:
        - self.adjacency_matrix:
        :return: Assign tuple with the elements to the self.backup variable
        '''
        return (self.all_nodes_collection,
                self.patient_nodes_collection,
                self.reactome_interaction_network,
                self.database_mutation_dict,
                self.database_expression_dict,
                self.database_cnv_dict,
                self.database_methylation_dict,
                self.node_coordinates,
                self.adjacency_matrix)
    def __remove_created_data_variables(self):
        '''
        Return to the state before the validation; delete the created variables.
        :return:
        '''
        if 'all_nodes_collection' in dir(self):
            del self.all_nodes_collection
        if 'patient_nodes_collection' in dir(self):
            del self.patient_nodes_collection
        if 'database_mutation_dict' in dir(self):
            del self.database_mutation_dict
        if 'database_expression_dict' in dir(self):
            del self.database_expression_dict
        if 'database_cnv_dict' in dir(self):
            del self.database_cnv_dict
        if 'database_methylation_dict' in dir(self):
            del self.database_methylation_dict
        if 'node_coordinates' in dir(self):
            del self.node_coordinates
        if 'adjacency_matrix' in dir(self):
            del self.adjacency_matrix
        if 'main_patient_data_dict' in dir(self):
            del self.main_patient_data_dict
        if 'main_patient_id' in dir(self):
            del self.main_patient_id
        if 'adjacency_matrix_with_main_patient' in dir(self):
            del self.adjacency_matrix_with_main_patient
        if 'node_coordinates_with_main_patient' in dir(self):
            del self.node_coordinates_with_main_patient
        if 'node_coordinates_with_main_patient_reverse' in dir(self):
            del self.node_coordinates_with_main_patient_reverse
        if 'similar_patient_list' in dir(self):
            del self.similar_patient_list
        return
    def __restore_original_data_variable_content(self):
        '''
        Restore everything in the self.backup variable to the following original variables:
        - self.all_nodes_collection:
        - self.patient_nodes_collection:
        - self.reactome_interaction_network:
        - self.database_mutation_dict:
        - self.database_expression_dict:
        - self.database_cnv_dict:
        - self.database_methylation_dict:
        - self.node_coordinates:
        - self.adjacency_matrix:
        :return: Restore data tuple with the elements from the self.backup variable
        '''
        (self.all_nodes_collection,
         self.patient_nodes_collection,
         self.reactome_interaction_network,
         self.database_mutation_dict,
         self.database_expression_dict,
         self.database_cnv_dict,
         self.database_methylation_dict,
         self.node_coordinates,
         self.adjacency_matrix) = self.backup
        del self.backup
        return
    def __LOO_cross_validation(self, subtype_dict):
        '''
        Loops over the BRCA patients and tries to predict the subtype of the
        patient based on the similar patients.
        :param subtype_dict: Dictionary with the subtype (value) of the patients (key)
        :return: The prediction accuracy
        '''
        # DEFINE VARIABLES USED TO CALCULATE ACCURACY
        accurate_predictions = 0
        predictions_done = 0
        patients_done = 0
        patients_with_no_connections = 0


        for patient in self.patient_nodes_collection:
            # RESETTING VARIABLES FROM PREVIOUS LOOPS
            self.adjacency_matrix_with_main_patient = None
            self.node_coordinates_with_main_patient = None
            self.node_coordinates_with_main_patient_reverse = None
            self.main_patient_id = None
            self.main_patient_data_dict = None
            self.similar_patient_list = None
            prediction = set()

            # IMPORT PATIENT DATA (= MAIN PATIENT)
            self.main_patient_id = 'MAIN_PATIENT'
            if self.BRCA_mutation_dict != {} and patient in self.BRCA_mutation_dict:
                mutation_data = list(self.BRCA_mutation_dict[patient])
            else:
                mutation_data = set()

            if self.BRCA_expression_dict != {} and patient in self.BRCA_expression_dict:
                expression_data = list(self.BRCA_expression_dict[patient])
            else:
                expression_data = set()

            if self.BRCA_cnv_dict != {} and patient in self.BRCA_cnv_dict:
                cnv_data = list(self.BRCA_cnv_dict[patient])
            else:
                cnv_data = set()

            if self.BRCA_methylation_dict != {} and patient in self.BRCA_methylation_dict:
                methylation_data = list(self.BRCA_methylation_dict[patient])
            else:
                methylation_data = set()

            patient_subtype = subtype_dict[patient]

            self.main_patient_data_dict = {'mutation_data': mutation_data,
                                'expression_data': expression_data,
                                'cnv_data': cnv_data,
                                'methylation_data': methylation_data}

            # ADD NEW PATIENT TO ADJACENCY MATRIX AND TO CORRESPONDING INDEX DICTIONARY / PATIENT NODE COLLECTION
            self.adjacency_matrix_with_main_patient, \
            self.node_coordinates_with_main_patient = self.__add_new_patient_to_adjacency_matrix()

            # WE WILL ALSO REQUIRE THE REVERSED DICTIONARY
            self.node_coordinates_with_main_patient_reverse = \
                self.__reverse_dictionary(self.node_coordinates_with_main_patient)

            # COMPUTE SIMILAR PATIENT LIST
            similar_patients_list = self.__list_similar_patients(method=similar_patients_computation_method)
            if similar_patients_list != []:
                    # We add the 'new patient' to the matrix and it is already there as database patient, thus
                    # we will always get the duplicate as first hit. Therefore we start from index 1.
                    self.similar_patient_list = similar_patients_list[1:number_of_similar_patients + 1]
            print(self.similar_patient_list)
            # COUNT SUBTYPE REPRESENTATION IN TOP PATIENTS
            subtype_count = dict()
            if self.similar_patient_list != []:
                for top_patient in self.similar_patient_list:
                    subtype = subtype_dict[top_patient[0]]
                    if subtype not in subtype_count:
                        subtype_count[subtype] = 1
                    else:
                        subtype_count[subtype] += 1
                highest_count = 0
                for subtype in subtype_count:
                    if subtype_count[subtype] > highest_count:
                        prediction = set([subtype])
                        highest_count = subtype_count[subtype]
                    if subtype_count[subtype] == highest_count:
                        prediction.update([subtype])
                if len(prediction) == 1:
                    if list(prediction)[0] == patient_subtype:
                        accurate_predictions += 1
                    else:
                        accurate_predictions += 0
                else:
                    if patient_subtype in prediction:
                        accurate_predictions += 1 / len(prediction)
                    else:
                        accurate_predictions += 0
                predictions_done += 1
            else:
                patients_with_no_connections += 1
            patients_done += 1
            print('Patient {} from {} completed'.format(patients_done, len(self.patient_nodes_collection)))
            print('real: {} --> pred: {}'.format(patient_subtype, prediction))
            print('intermediate accuracy: ', accurate_predictions*100 / predictions_done, '%\n')
        accuracy = accurate_predictions / predictions_done
        print('Final accuracy: ', round(accuracy, 6)*100, '%')
        print('Patients without connections: ', patients_with_no_connections)
        return accuracy

    # MAIN FUNCTIONS
    def compute_similar_patients(self, biology: Biology, main_patient: Patient,
                                 database_patients: Iterable[Patient]) -> SimilarPatientList:
        #########################################################
        # COMPUTING THE ADJACENCY MATRIX WITH DATABASE PATIENTS #
        #########################################################
        # INITIALIZE IMPORT
        self.biology = biology
        self.gene_metanomenclature = self.biology.gene_metanomenclature
        self.gene_nomenclature = self.gene_metanomenclature.get_nomenclature('ensembl')
        self.subtype_metanomenclature = self.biology.cancer_subtype_metanomenclature
        self.subtype_nomenclature = self.subtype_metanomenclature.get_nomenclature("default")


        # CREATE VARIABLES TO STORE INFORMATION ABOUT THE NODES
        self.all_nodes_collection = set()
        self.patient_nodes_collection = set()
        self.patient_name_object_dict = dict()

        # IMPORT REACTOME INTERACTION NETWORK (PRIOR KNOWLEDGE)
        self.reactome_interaction_network = self.__import_reactome_interactions()

        # IMPORT DATABASE PATIENT DATA
        self.database_mutation_dict = self.__import_database_mutation_data(database_patients)
        self.database_expression_dict = self.__import_database_expression_data(database_patients)
        self.database_cnv_dict = {}
        self.database_methylation_dict = {}

        # CREATING BLANK ADJACENCY MATRIX
        adjacency_matrix = np.zeros(shape=(len(self.all_nodes_collection), len(self.all_nodes_collection)))

        # MAKE DICTIONARY OF THE INDEX OF EVERY NODE IN THE ADJACENCY MATRIX
        self.node_coordinates = self.__create_node_index_list()

        # FILL IN THE ADJACENCY MATRIX
        if self.database_mutation_dict != {}:
            print('Adding mutated genes to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix, self.database_mutation_dict)
        if self.database_expression_dict != {}:
            print('Adding differentially expressed genes to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix, self.database_expression_dict)
        if self.database_cnv_dict != {}:
            print('Adding genes varying in copy number to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix, self.database_cnv_dict)
        if self.database_methylation_dict != {}:
            print('Adding hypo- and hypermethylated genes to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix, self.database_methylation_dict)

        # CONNECTING GENE NODES THROUGH THE REACTOME INTERACTION NETWORK
        print('Connecting the gene nodes by making use of the interaction network..\n')
        adjacency_matrix = self.__connecting_gene_nodes_by_interaction_network(adjacency_matrix)
        self.adjacency_matrix = adjacency_matrix

        # IMPORT NEW PATIENT DATA (= MAIN PATIENT)
        self.main_patient_data_dict = self.__import_main_patient(main_patient)
        self.main_patient_id = 'MAIN_PATIENT'

        # ADD NEW PATIENT TO ADJACENCY MATRIX AND TO CORRESPONDING INDEX DICTIONARY / PATIENT NODE COLLECTION
        self.adjacency_matrix_with_main_patient, \
        self.node_coordinates_with_main_patient = self.__add_new_patient_to_adjacency_matrix()
        # WE WILL ALSO REQUIRE THE REVERSED DICTIONARY
        self.node_coordinates_with_main_patient_reverse = self.__reverse_dictionary(self.node_coordinates_with_main_patient)

        # COMPUTE SIMILAR PATIENT LIST
        self.similar_patient_list = self.__list_similar_patients(method = similar_patients_computation_method)
        self.similar_patient_list = self.similar_patient_list[0:number_of_similar_patients]

        # create SimilarPatientList object
        temp_list = list()
        if similar_patients_computation_method == 1:
            sim_measure = 'RW_local'
        elif similar_patients_computation_method == 2:
            sim_measure = 'RW_adjacency'
        elif similar_patients_computation_method == 3:
            sim_measure = 'LEXP'

        for (patient_name, score) in self.similar_patient_list:
            print(patient_name)
            patient_obj = self.patient_name_object_dict[patient_name]
            similar_patient_object = SimilarPatient(patient=patient_obj, similarity_explanation=sim_measure,
                                                    similarity_score=float(score))
            temp_list.append(similar_patient_object)
        self.similar_patient_list = temp_list

        return SimilarPatientList(patient=main_patient, similar_patients=self.similar_patient_list,
                                  used_data_sources=self.main_patient_data_dict, creation_date=datetime.datetime.now(),
                                  used_method=self)

    def BRCA_LOO_cross_validation(self):
        # INITIALIZE IMPORT
        self.domain_initializer = DomainInitializer()
        self.biology = self.domain_initializer.biology
        self.gene_metanomenclature = self.biology.gene_metanomenclature
        self.gene_nomenclature = self.gene_metanomenclature.get_nomenclature('ensembl')
        self.subtype_metanomenclature = self.biology.cancer_subtype_metanomenclature
        self.subtype_nomenclature = self.subtype_metanomenclature.get_nomenclature("default")

        # WE WILL REUSE EXISTING FUNCTIONS,
        # THUS WE MUST MAKE A BACKUP OF THE CONTENT OF THE ORIGINAL DATA
        if 'adjacency_matrix' in dir(self): # if there is useful data to back up
            self.backup = self.__backup_data_variable_content()
        else:
            self.backup = None

        # DEFINE / RESET OTHER VARIABLES
        self.all_nodes_collection = set()
        self.patient_nodes_collection = set()

        # IMPORT REACTOME INTERACTION NETWORK (PRIOR KNOWLEDGE)
        self.reactome_interaction_network = self.__import_reactome_interactions()

        # IMPORT CROSS VALIDATION BRCA DATASET
        #self.BRCA_mutation_dict = {}
        #self.BRCA_expression_dict = {}
        self.BRCA_mutation_dict = self.__import_BRCA_mutation_file()
        self.BRCA_expression_dict = self.__import_BRCA_expression_file()
        self.BRCA_cnv_dict = {}
        self.BRCA_methylation_dict = {}

        # CREATE BLANK ADJACENCY MATRIX
        adjacency_matrix = np.zeros(shape=(len(self.all_nodes_collection), len(self.all_nodes_collection)))

        # MAKE DICTIONARY OF THE INDEX OF EVERY NODE IN THE ADJACENCY MATRIX
        self.node_coordinates = self.__create_node_index_list()

        # FILL IN THE ADJACENCY MATRIX
        if self.BRCA_mutation_dict != {}:
            print('Adding mutated genes to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix,
                                                                                 self.BRCA_mutation_dict)
        if self.BRCA_expression_dict != {}:
            print('Adding DE genes to the adjacency matrix..\n')
            adjacency_matrix = self.__fill_adjacency_matrix_with_data_dictionary(adjacency_matrix,
                                                                                 self.BRCA_expression_dict)


        # CONNECTING GENE NODES THROUGH THE REACTOME INTERACTION NETWORK
        print('Connecting the gene nodes by making use of the interaction network..\n')
        adjacency_matrix = self.__connecting_gene_nodes_by_interaction_network(adjacency_matrix)
        self.adjacency_matrix = adjacency_matrix

        # IMPORT AND CREATE A SUBTYPE DICTIONARY
        BRCA_patient_subtypes_dict = self.__import_patient_subtypes_into_dict()


        # PERFORM THE LEAVE ONE OUT CROSS VALIDATION LOOP METHOD
        accuracy = self.__LOO_cross_validation(BRCA_patient_subtypes_dict)

        # REMOVE VARIABLES FOR VALIDATION AND RESTORE OLD DATA IN VARIABLES
        if self.backup is None:
            self.__remove_created_data_variables()
        else:
            self.__remove_created_data_variables()
            self.__restore_original_data_variable_content()
        return accuracy


#
network_algorithm = NetworkAlgorithm()
domain_initializer = DomainInitializer()
bio = domain_initializer.biology
database_patients = domain_initializer.persisted_patients

main_patient = set(domain_initializer.persisted_patients).pop()
print(main_patient.name)

print(network_algorithm.compute_similar_patients(biology=bio, main_patient=main_patient, database_patients=database_patients))
#print(network_algorithm.BRCA_LOO_cross_validation())





