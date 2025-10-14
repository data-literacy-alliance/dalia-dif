import pytest

from dalia_dif.dif13.legacy import constants as s
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from dalia_dif.dif13.legacy.learning_resource import parse_dif13_row_legacy
from tests.util import same_graphs


def test_dif_learning_resource_to_graph():
    g = graph()
    row = {
        s.DIF_HEADER_ID: "b3763080-15a4-4de4-b99b-c9b337644904",
        s.DIF_HEADER_AUTHORS: "Mertzen, Daniela : {https://orcid.org/0000-0003-4471-9255} * Neuroth, Heike",  # ...
        s.DIF_HEADER_LICENSE: "CC-BY-4.0",
        s.DIF_HEADER_LINK: "https://doi.org/10.5281/zenodo.11564808",
        s.DIF_HEADER_TITLE: 'Zertifikatskurs "Forschungsdatenmanagement für Studierende": Spring School 2024 der ...',
        s.DIF_HEADER_COMMUNITY: "FDM-BB (SR)",
        s.DIF_HEADER_DESCRIPTION: "Der Zertifikatskurs Forschungsdatenmanagement (FDM) für Studierende wurde im ...",
        s.DIF_HEADER_DISCIPLINE: "https://w3id.org/kim/hochschulfaechersystematik/n0",
        s.DIF_HEADER_FILE_FORMAT: "PDF * ODP",
        s.DIF_HEADER_KEYWORDS: "research data management * certificate course * lesson * training * students",
        s.DIF_HEADER_LANGUAGE: "de",
        s.DIF_HEADER_LEARNING_RESOURCE_TYPE: "Lecture",
        s.DIF_HEADER_MEDIA_TYPE: "presentation * text",
        s.DIF_HEADER_PROFICIENCY_LEVEL: "novice * advanced beginner",
        s.DIF_HEADER_PUBLICATION_DATE: "2024-07-01",
        s.DIF_HEADER_TARGET_GROUP: "student (BA) * student (MA) * teacher (higher education)",
        s.DIF_HEADER_RELATED_WORK: "",
        s.DIF_HEADER_SIZE: "47.2",
        s.DIF_HEADER_VERSION: "2024",
    }
    parse_dif13_row_legacy(g, 1, row)

    expected = graph().parse(
        data=r"""
        @prefix bflr: <http://bibfra.me/vocab/relation/> .
        @prefix dalia-community: <https://id.dalia.education/community/> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix ec: <https://github.com/tibonto/educor#> .
        @prefix fabio: <http://purl.org/spar/fabio/> .
        @prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
        @prefix mo: <https://purl.org/ontology/modalia#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rec: <http://purl.org/ontology/rec/core#> .
        @prefix schema: <https://schema.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        <https://id.dalia.education/learning-resource/b3763080-15a4-4de4-b99b-c9b337644904> a ec:EducationalResource ;
            schema:author (
                [
                    a schema:Person ;
                    schema:familyName "Mertzen" ;
                    schema:givenName "Daniela" ;
                    m4i:orcidId "https://orcid.org/0000-0003-4471-9255"
                ]
                [
                    a schema:Person ;
                    schema:familyName "Neuroth" ;
                    schema:givenName "Heike"
                ]
            ) ;
            <https://dalia.education/authorUnordered> [
                a schema:Person ;
                schema:familyName "Mertzen" ;
                schema:givenName "Daniela" ;
                m4i:orcidId "https://orcid.org/0000-0003-4471-9255"
            ] ,
            [
                a schema:Person ;
                schema:familyName "Neuroth" ;
                schema:givenName "Heike"
            ] ;
            dcterms:license <http://spdx.org/licenses/CC-BY-4.0> ;
            schema:url <https://doi.org/10.5281/zenodo.11564808> ;
            dcterms:title "Zertifikatskurs \"Forschungsdatenmanagement für Studierende\"" ;
            fabio:hasSubtitle "Spring School 2024 der ..." ;
            bflr:supportinghost dalia-community:e26f5af3-96e5-43ce-9e36-c61a1e513a1b ;
            rec:recommender dalia-community:e26f5af3-96e5-43ce-9e36-c61a1e513a1b ;
            dcterms:description "Der Zertifikatskurs Forschungsdatenmanagement (FDM) für Studierende wurde im ..." ;
            fabio:hasDiscipline <https://w3id.org/kim/hochschulfaechersystematik/n0> ;
            dcterms:format "ODP", "PDF" ;
            schema:keywords "certificate course", "lesson", "research data management", "students", "training" ;
            dcterms:language <http://lexvo.org/id/iso639-3/deu> ;
            mo:hasLearningType mo:Lecture ;
            mo:hasMediaType schema:Text, schema:PresentationDigitalDocument ;
            mo:requiresProficiencyLevel mo:Beginner, mo:Novice ;
            schema:datePublished "2024-07-01"^^xsd:date ;
            mo:hasTargetGroup mo:BachelorStudent, mo:MastersStudent, mo:TeacherHighEducation ;
            schema:fileSize "47.2 MB" ;
            schema:version "2024" .
    """
    )

    assert same_graphs(g, expected)


def test_dif_learning_resource_to_graph_adds_no_learning_resource_for_empty_id():
    g = graph()
    row = {
        s.DIF_HEADER_ID: "",
        s.DIF_HEADER_AUTHORS: "Mertzen, Daniela : {https://orcid.org/0000-0003-4471-9255} * Neuroth, Heike",  # ...
        s.DIF_HEADER_LICENSE: "CC-BY-4.0",
        s.DIF_HEADER_LINK: "https://doi.org/10.5281/zenodo.11564808",
        s.DIF_HEADER_TITLE: 'Zertifikatskurs "Forschungsdatenmanagement für Studierende": Spring School 2024 der ...',
        s.DIF_HEADER_COMMUNITY: "FDM-BB (SR)",
        s.DIF_HEADER_DESCRIPTION: "Der Zertifikatskurs Forschungsdatenmanagement (FDM) für Studierende wurde im ...",
        s.DIF_HEADER_DISCIPLINE: "https://w3id.org/kim/hochschulfaechersystematik/n0",
        s.DIF_HEADER_FILE_FORMAT: "PDF * ODP",
        s.DIF_HEADER_KEYWORDS: "research data management * certificate course * lesson * training * students",
        s.DIF_HEADER_LANGUAGE: "de",
        s.DIF_HEADER_LEARNING_RESOURCE_TYPE: "Lecture",
        s.DIF_HEADER_MEDIA_TYPE: "presentation * text",
        s.DIF_HEADER_PROFICIENCY_LEVEL: "novice * advanced beginner",
        s.DIF_HEADER_PUBLICATION_DATE: "2024-07-01",
        s.DIF_HEADER_TARGET_GROUP: "student (BA) * student (MA) * teacher (higher education)",
        s.DIF_HEADER_RELATED_WORK: "",
        s.DIF_HEADER_SIZE: "47.2",
        s.DIF_HEADER_VERSION: "2024",
    }
    parse_dif13_row_legacy(g, 1, row)

    expected = graph()

    assert same_graphs(g, expected)


def test_dif_learning_resource_to_graph_raises_value_error_on_invalid_id():
    row = {s.DIF_HEADER_ID: "abc"}
    expected_error_msg = "badly formed hexadecimal UUID string"

    with pytest.raises(ValueError, match=expected_error_msg):
        parse_dif13_row_legacy(graph(), 1, row)
