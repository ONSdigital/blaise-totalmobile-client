import pytest

from datetime import datetime
from models.blaise.get_blaise_case_model import GetBlaiseCaseModel
from models.blaise.uac_model import UacModel, UacChunks
from tests.helpers import get_blaise_case_model_helper


def test_import_case_returns_a_populated_model():
    questionnaire_name = "LMS2101_AA1"

    case_data_dictionary = {
        "qiD.Serial_Number": "90000000",
        "dataModelName": "LM2007",
        "qDataBag.Wave": "1",
        "qDataBag.Prem1": "12 Blaise Street",
        "qDataBag.Prem2": "Blaise Hill",
        "qDataBag.Prem3": "Blaiseville",
        "qDataBag.District": "Gwent",
        "qDataBag.PostTown": "Newport",
        "qDataBag.PostCode": "FML134D",
        "qDataBag.TelNo": "07900990901",
        "qDataBag.TelNo2": "07900990902",
        "telNoAppt": "07900990903",
        "hOut": "301",
        "qDataBag.UPRN_Latitude": "10020202",
        "qDataBag.UPRN_Longitude": "34949494",
        "qDataBag.Priority": "1",
        "qDataBag.FieldCase": "Y",
        "qDataBag.FieldRegion": "gwent",
        "qDataBag.FieldTeam": "B-Team",
        "qDataBag.WaveComDTE": "31-01-2023"
    }

    result = GetBlaiseCaseModel.import_case(questionnaire_name, case_data_dictionary)

    assert result.questionnaire_name == "LMS2101_AA1"
    assert result.case_id == "90000000"
    assert result.data_model_name == "LM2007"
    assert result.wave == "1"
    assert result.address_details.address.address_line_1 == "12 Blaise Street"
    assert result.address_details.address.address_line_2 == "Blaise Hill"
    assert result.address_details.address.address_line_3 == "Blaiseville"
    assert result.address_details.address.county == "Gwent"
    assert result.address_details.address.town == "Newport"
    assert result.address_details.address.postcode == "FML134D"
    assert result.contact_details.telephone_number_1 == "07900990901"
    assert result.contact_details.telephone_number_2 == "07900990902"
    assert result.contact_details.appointment_telephone_number == "07900990903"
    assert result.outcome_code == 301
    assert result.address_details.address.coordinates.latitude == "10020202"
    assert result.address_details.address.coordinates.longitude == "34949494"
    assert result.priority == "1"
    assert result.field_region == "gwent"
    assert result.field_case == "Y"
    assert result.field_team == "B-Team"
    assert result.wave_com_dte == datetime(2023, 1, 31)


def test_import_case_returns_a_valid_object_when_a_blaise_field_is_incorrectly_typed():
    questionnaire_name = "LMS2101_AA1"

    case_data_dictionary = {
        "qdatabag.Serial_Number": "90000000",
        "dataModelName": "LM2007",
        "qDataBag.Wave": "1",
        "qDataBag.Prem1": "12 Blaise Street",
        "qDataBag.Prem2": "Blaise Hill",
        "qDataBag.Prem3": "Blaiseville",
        "qDataBag.District": "Gwent",
        "qDataBag.PostTown": "Newport",
        "qDataBag.PostCode": "FML134D",
        "qDataBag.TelNo": "07900990901",
        "qDataBag.TelNo2": "07900990902",
        "telNoAppt": "07900990903",
        "hOut": "301",
        "qDataBag.UPRN_Latitude": "10020202",
        "qDataBag.UPRN_Longitude": "34949494",
        "qDataBag.Priority": "1",
        "qDataBag.FieldRegion": "gwent",
        "qDataBag.FieldTeam": "B-Team",
        "qDataBag.WaveComDTE": "31-01-2023"
    }

    result = GetBlaiseCaseModel.import_case(questionnaire_name, case_data_dictionary)

    assert result.questionnaire_name == "LMS2101_AA1"
    assert result.case_id is None
    assert result.data_model_name == "LM2007"
    assert result.wave == "1"
    assert result.address_details.address.address_line_1 == "12 Blaise Street"
    assert result.address_details.address.address_line_2 == "Blaise Hill"
    assert result.address_details.address.address_line_3 == "Blaiseville"
    assert result.address_details.address.county == "Gwent"
    assert result.address_details.address.town == "Newport"
    assert result.address_details.address.postcode == "FML134D"
    assert result.contact_details.telephone_number_1 == "07900990901"
    assert result.contact_details.telephone_number_2 == "07900990902"
    assert result.contact_details.appointment_telephone_number == "07900990903"
    assert result.outcome_code == 301
    assert result.address_details.address.coordinates.latitude == "10020202"
    assert result.address_details.address.coordinates.longitude == "34949494"
    assert result.priority == "1"
    assert result.field_region == "gwent"
    assert result.field_team == "B-Team"
    assert result.wave_com_dte == datetime(2023, 1, 31)


def test_import_case_sets_outcome_code_to_zero_if_empty():
    questionnaire_name = "LMS2101_AA1"

    case_data_dictionary = {
        "hOut": "",
        "qDataBag.WaveComDTE": "31-01-2023"
    }

    result = GetBlaiseCaseModel.import_case(questionnaire_name, case_data_dictionary)

    assert result.outcome_code == 0


def test_import_case_sets_outcome_code_to_if_not_supplied():
    questionnaire_name = "LMS2101_AA1"

    case_data_dictionary = {
        "qDataBag.WaveComDTE": "31-01-2023"
    }

    result = GetBlaiseCaseModel.import_case(questionnaire_name, case_data_dictionary)

    assert result.outcome_code == 0


def test_import_case_returns_a_valid_object_when_an_optional_blaise_field_is_missing():
    questionnaire_name = "LMS2101_AA1"

    case_data_dictionary = {
        "dataModelName": "LM2007",
        "qDataBag.Wave": "1",
        "qDataBag.Prem1": "12 Blaise Street",
        "qDataBag.Prem2": "Blaise Hill",
        "qDataBag.Prem3": "Blaiseville",
        "qDataBag.District": "Gwent",
        "qDataBag.PostTown": "Newport",
        "qDataBag.PostCode": "FML134D",
        "qDataBag.TelNo": "07900990901",
        "qDataBag.TelNo2": "07900990902",
        "telNoAppt": "07900990903",
        "hOut": "301",
        "qDataBag.UPRN_Latitude": "10020202",
        "qDataBag.UPRN_Longitude": "34949494",
        "qDataBag.Priority": "1",
        "qDataBag.FieldRegion": "gwent",
        "qDataBag.FieldTeam": "B-Team",
        "qDataBag.WaveComDTE": "31-01-2023"
    }

    result = GetBlaiseCaseModel.import_case(questionnaire_name, case_data_dictionary)

    assert result.questionnaire_name == "LMS2101_AA1"
    assert result.case_id is None
    assert result.data_model_name == "LM2007"
    assert result.wave == "1"
    assert result.address_details.address.address_line_1 == "12 Blaise Street"
    assert result.address_details.address.address_line_2 == "Blaise Hill"
    assert result.address_details.address.address_line_3 == "Blaiseville"
    assert result.address_details.address.county == "Gwent"
    assert result.address_details.address.town == "Newport"
    assert result.address_details.address.postcode == "FML134D"
    assert result.contact_details.telephone_number_1 == "07900990901"
    assert result.contact_details.telephone_number_2 == "07900990902"
    assert result.contact_details.appointment_telephone_number == "07900990903"
    assert result.outcome_code == 301
    assert result.address_details.address.coordinates.latitude == "10020202"
    assert result.address_details.address.coordinates.longitude == "34949494"
    assert result.priority == "1"
    assert result.field_region == "gwent"
    assert result.field_team == "B-Team"
    assert result.wave_com_dte == datetime(2023, 1, 31)


def test_populate_uac_data_populates_uac_fields_if_supplied():
    case_model = get_blaise_case_model_helper.get_populated_case_model(case_id="10020")

    uac_model = UacModel(
        case_id="10020",
        uac_chunks=UacChunks(
            uac1="8176",
            uac2="4726",
            uac3="3992"
        )
    )

    case_model.populate_uac_data(uac_model)

    assert case_model.uac_chunks is not None
    assert case_model.uac_chunks.uac1 == "8176"
    assert case_model.uac_chunks.uac2 == "4726"
    assert case_model.uac_chunks.uac3 == "3992"


def test_populate_uac_data_does_not_populate_uac_fields_if_Not_supplied():
    case_model = get_blaise_case_model_helper.get_populated_case_model(case_id="10010")
    case_model.populate_uac_data(None)

    assert case_model.uac_chunks is None


def test_populate_uac_data_sets_date_to_none_if_date_is_an_empty_string():
    case_data_dictionary = {
        "qiD.Serial_Number": "90000000",
        "dataModelName": "LM2007",
        "qDataBag.TLA": "LMS",
        "qDataBag.Wave": "1",
        "qDataBag.Prem1": "12 Blaise Street",
        "qDataBag.Prem2": "Blaise Hill",
        "qDataBag.Prem3": "Blaiseville",
        "qDataBag.District": "Gwent",
        "qDataBag.PostTown": "Newport",
        "qDataBag.PostCode": "FML134D",
        "qDataBag.TelNo": "07900990901",
        "qDataBag.TelNo2": "07900990902",
        "telNoAppt": "07900990903",
        "hOut": "301",
        "qDataBag.UPRN_Latitude": "10020202",
        "qDataBag.UPRN_Longitude": "34949494",
        "qDataBag.Priority": "1",
        "qDataBag.FieldRegion": "gwent",
        "qDataBag.FieldTeam": "B-Team",
        "qDataBag.WaveComDTE": ""
    }

    result = GetBlaiseCaseModel.import_case("LMS", case_data_dictionary)

    assert result.wave_com_dte is None
