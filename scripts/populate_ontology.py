from ista import FlatFileDatabaseParser, MySQLDatabaseParser
from ista.util import print_onto_stats

import owlready2

import mysecrets

import ipdb

# added the path of addictionkb ontology file
onto = owlready2.get_ontology("Path to addictionkb.rdf").load() 

# added the path of the directory where all the data sources are stored
data_dir = "Path to processed and filetered data sources" 

mysql_config = {
    'host': mysecrets.MYSQL_HOSTNAME,
    'user': mysecrets.MYSQL_USERNAME,
    'passwd': mysecrets.MYSQL_PASSWORD
}

# ignore the datasources epa, aopwiki, tox21
ncbigene = FlatFileDatabaseParser("ncbigene", onto, data_dir)
drugbank = FlatFileDatabaseParser("drugbank", onto, data_dir)
hetionet = FlatFileDatabaseParser("hetionet", onto, data_dir)
aopdb = MySQLDatabaseParser("aopdb", onto, mysql_config)
disgenet = FlatFileDatabaseParser("disgenet", onto, data_dir)


drugbank.parse_node_type(
    node_type="Drug", 
    source_filename="drug_links_v5.1.13.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "DrugBank ID",
        "headers": True,
        "data_property_map": {
            "DrugBank ID": onto.xrefDrugbank,
            "CAS Number": onto.xrefCasRN,
            "Name": onto.commonName,
        },
        "merge_column": {
            "source_column_name": "CAS Number",
            "data_property": onto.xrefCasRN,
        },
    },
    merge=False,
    skip=False
)

ncbigene.parse_node_type(
    node_type="Gene",
    source_filename="output.tsv",
    fmt="tsv-pandas",
    parse_config={
        "compound_fields": {
            "dbXrefs": {"delimiter": "|", "field_split_prefix": ":"}
        },
        "iri_column_name": "Symbol",
        "headers": True,
        "data_property_map": {
            "GeneID": onto.xrefNcbiGene,
            "Symbol": onto.geneSymbol,
            "type_of_gene": onto.typeOfGene,
            "Full_name_from_nomenclature_authority": onto.commonName,
            "MIM": onto.xrefOMIM,
            "HGNC": onto.xrefHGNC,
            "Ensembl": onto.xrefEnsembl,
            # TODO: Parse Feature_type and other columns
        },
    },
    merge=False,
    skip=False
)

hetionet.parse_node_type(
    node_type="DrugClass",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Pharmacologic Class",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefNciThesaurus,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)


hetionet.parse_node_type(
    node_type="Symptom",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Symptom",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefMeSH,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)

hetionet.parse_node_type(  # ANATOMY RESOLUTION NEEDS TO BE REFINED!
    node_type="BodyPart",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Anatomy",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefUberon,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)

hetionet.parse_node_type(
    node_type="BiologicalProcess",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Biological Process",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefGeneOntology,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)

hetionet.parse_node_type(
    node_type="MolecularFunction",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Molecular Function",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefGeneOntology,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)

hetionet.parse_node_type(
    node_type="CellularComponent",
    source_filename="nodes.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "name",
        "headers": True,
        "filter_column": "kind",
        "filter_value": "Cellular Component",
        "data_transforms": {
            "id": lambda x: x.split("::")[-1]
        },
        "data_property_map": {
            "id": onto.xrefGeneOntology,
            "name": onto.commonName
        }
    },
    merge=False,
    skip=False
)

aopdb.parse_node_type(
    node_type="Drug",
    source_table="chemical_info",
    parse_config={
        "iri_column_name": "DTX_id",
        "data_property_map": {"ChemicalID": onto.xrefMeSH},
        "merge_column": {
            "source_column_name": "DTX_id",
            "data_property": onto.xrefDTXSID
        }
    },
    merge=True,
    skip=False
)

aopdb.parse_node_type(
    node_type="Pathway",
    source_table="stressor_info",
    parse_config={
        "iri_column_name": "path_id",
        "data_property_map": {
            "path_id": onto.pathwayId,
            "path_name": onto.commonName,
            "ext_source": onto.sourceDatabase,
        },
        "custom_sql_query": "SELECT DISTINCT path_id, path_name, ext_source FROM aopdb.pathway_gene WHERE tax_id = 9606;"
    },
    merge=False,
    skip=False
)

disgenet.parse_node_type(
    node_type="Disease",
    source_filename="disease_mappings_to_attributes_addkb_all.tsv",  # Filtered for addictionkb
    fmt="tsv-pandas",
    parse_config={
        "iri_column_name": "diseaseId",
        "headers": True,
        "data_property_map": {
            "diseaseId": onto.xrefUmlsCUI,
            "name": onto.commonName,
        }
    },
    merge=False,
    skip=False
)

disgenet.parse_node_type(
    node_type="Disease",
    source_filename="disease_mappings_addkb_all.tsv",  # Filtered, as above
    fmt="tsv-pandas",
    parse_config={
        "iri_column_name": "diseaseId",
        "headers": True,
        "filter_column": "vocabulary",
        "filter_value": "DO",
        "merge_column": {
            "source_column_name": "diseaseId",
            "data_property": onto.xrefUmlsCUI
        },
        "data_property_map": {
            "code": onto.xrefDiseaseOntology
        }
    },
    merge=True,
    skip=False
)

disgenet.parse_relationship_type(
    relationship_type=onto.geneAssociatesWithDisease,
    source_filename="curated_gene_disease_associations.tsv", 
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "geneSymbol",
        "subject_match_property": onto.geneSymbol,
        "object_node_type": onto.Disease,
        "object_column_name": "diseaseId",
        "object_match_property": onto.xrefUmlsCUI,
        "filter_column": "diseaseType",
        "filter_value": "disease",
        "headers": True
    },
    merge=False,
    skip=False
)

hetionet.parse_relationship_type(
    relationship_type=onto.chemicalBindsGene,
    source_filename="edges.sif", # custom hetionet file
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Drug,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "CbG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.geneInteractsWithGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "GiG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]),
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.drugInClass,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Drug,
        "subject_column_name": "target",  # Note how we reverse the direction of the relationship here
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.DrugClass,
        "object_column_name": "source",
        "object_match_property": onto.xrefNciThesaurus,
        "filter_column": "metaedge",
        "filter_value": "PCiC",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: x.split("::")[-1]  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.drugCausesEffect,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Drug,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.ChemicalEffect,
        "object_column_name": "target",
        "object_match_property": onto.xrefUmlsCUI,
        "filter_column": "metaedge",
        "filter_value": "CcSE",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: x.split("::")[-1]
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.symptomManifestationOfDisease,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Symptom,
        "subject_column_name": "target", # Flip target and source
        "subject_match_property": onto.xrefMeSH,
        "object_node_type": onto.Disease,
        "object_column_name": "source",
        "object_match_property": onto.xrefDiseaseOntology,
        "filter_column": "metaedge",
        "filter_value": "DpS",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("DOID:")[-1], # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split("::")[-1]
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.drugTreatsDisease,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Drug,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Disease,
        "object_column_name": "target",
        "object_match_property": onto.xrefDiseaseOntology,
        "filter_column": "metaedge",
        "filter_value": "CtD",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: x.split(":")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(  # Hetionet makes a messy distinction between 'treats' and 'palliates' which we ignore
    relationship_type=onto.drugTreatsDisease,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Drug,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Disease,
        "object_column_name": "target",
        "object_match_property": onto.xrefDiseaseOntology,
        "filter_column": "metaedge",
        "filter_value": "CpD",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: x.split(":")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.diseaseLocalizesToAnatomy,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Disease,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDiseaseOntology,
        "object_node_type": onto.BodyPart,
        "object_column_name": "target",
        "object_match_property": onto.xrefUberon,
        "filter_column": "metaedge",
        "filter_value": "DlA",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split(":")[-1], # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split("::")[-1]
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.diseaseAssociatesWithDisease,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Disease,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDiseaseOntology,
        "object_node_type": onto.Disease,
        "object_column_name": "target",
        "object_match_property": onto.xrefDiseaseOntology,
        "filter_column": "metaedge",
        "filter_value": "DrD",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split(":")[-1], # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split(":")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.geneParticipatesInBiologicalProcess,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.BiologicalProcess,
        "object_column_name": "target",
        "object_match_property": onto.xrefGeneOntology,
        "filter_column": "metaedge",
        "filter_value": "GpBP",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]), # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split("::")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.geneAssociatedWithCellularComponent,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.CellularComponent,
        "object_column_name": "target",
        "object_match_property": onto.xrefGeneOntology,
        "filter_column": "metaedge",
        "filter_value": "GpCC",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]), # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split("::")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.geneHasMolecularFunction,
    source_filename="edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.MolecularFunction,
        "object_column_name": "target",
        "object_match_property": onto.xrefGeneOntology,
        "filter_column": "metaedge",
        "filter_value": "GpMF",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]), # Note: Because hetionet prefixes DOIDs with 'DOID:'
            "target": lambda x: x.split("::")[-1] # Note: Because hetionet prefixes DOIDs with 'DOID:'
        },
    },
    merge=False,
    skip=False
)

aopdb.parse_relationship_type(
    relationship_type=onto.geneInPathway,
    inverse_relationship_type=onto.PathwayContainsGene,
    parse_config = {
        "subject_node_type": onto.Gene,
        "subject_column_name": "entrez",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.Pathway,
        "object_column_name": "path_id",
        "object_match_property": onto.pathwayId,
        "custom_sql_query": "SELECT * FROM aopdb.pathway_gene WHERE tax_id = 9606;",
        "source_table_type": "foreignKey",
        "source_table": "pathway_gene",
    },
    merge=False,
    skip=False
)

hetionet.parse_relationship_type(
    relationship_type=onto.bodyPartOverExpressesGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.BodyPart,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefUberon,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "AuG",  # "anatomyUpregulatesGene"
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])
        },
    },
    merge=False,
    skip=False
)

hetionet.parse_relationship_type(
    relationship_type=onto.bodyPartUnderExpressesGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.BodyPart,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefUberon,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "AdG",  # "anatomyDownregulatesGene"
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])
        },
    },
    merge=False,
    skip=False
)

hetionet.parse_relationship_type(
    relationship_type=onto.geneRegulatesGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "Gr>G",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]),
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)


print_onto_stats(onto)

with open("Path to store populated rdf addkb-populated.rdf", 'wb') as fp:
    onto.save(file=fp, format="rdfxml")