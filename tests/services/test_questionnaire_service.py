import pytest

from services.questionnaire_service import get_cases, get_wave_from_questionnaire_name, get_uacs
from unittest import mock
from tests.helpers import config_helper


@mock.patch("services.blaise_restapi_service.get_questionnaire_case_data")
def test_get_cases_calls_the_service_with_the_correct_parameters(mock_restapi_service):
    config = config_helper.get_default_config()
    questionnaire_name = "LMS2101_AA1"

    # act
    get_cases(questionnaire_name, config)

    # assert
    mock_restapi_service.assert_called_with(questionnaire_name, config)


@mock.patch("services.blaise_restapi_service.get_questionnaire_case_data")
def test_get_cases_returns_a_list_of_questionnaire_models(mock_restapi_service):
    # arrange
    config = config_helper.get_default_config()
    mock_restapi_service.return_value = [
            {"qiD.Serial_Number": "10010", "hOut": "110"},
            {"qiD.Serial_Number": "10020", "hOut": "210"},
            {"qiD.Serial_Number": "10030", "hOut": "310"},
        ]

    questionnaire_name = "LMS2101_AA1"

    # act
    result = get_cases(questionnaire_name, config)

    # assert
    assert len(result) == 3

    assert result[0].case_id == "10010"
    assert result[0].outcome_code == "110"

    assert result[1].case_id == "10020"
    assert result[1].outcome_code == "210"

    assert result[2].case_id == "10030"
    assert result[2].outcome_code == "310"


@mock.patch("services.uac_restapi_service.get_questionnaire_uacs")
def test_get_uacs_calls_the_service_with_the_correct_parameters(mock_uac_service):
    # arrange
    config = config_helper.get_default_config()
    questionnaire_name = "LMS2101_AA1"

    # act
    get_uacs(questionnaire_name, config)

    # assert
    mock_uac_service.assert_called_with(questionnaire_name, config)


@mock.patch("services.uac_restapi_service.get_questionnaire_uacs")
def test_get_questionnaire_uacs_returns_a_list_of_uac_models(mock_uac_service):
    # arrange
    config = config_helper.get_default_config()
    mock_uac_service.return_value = {
        "10010": {
            "instrument_name": "OPN2101A",
            "case_id": "10010",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3991"
            },
            "full_uac": "817647263991"
        },
        "10020": {
            "instrument_name": "OPN2101A",
            "case_id": "10020",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3992"
            },
            "full_uac": "817647263992"
        },
        "10030": {
            "instrument_name": "OPN2101A",
            "case_id": "10030",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3993"
            },
            "full_uac": "817647263994"
        },
    }

    questionnaire_name = "LMS2101_AA1"

    # act
    result = get_uacs(questionnaire_name, config)

    # assert
    assert len(result) == 3


def test_get_wave_from_questionnaire_name_errors_for_non_lms_questionnaire():
    # arrange
    questionnaire_name = "OPN2101A"

    # act
    with pytest.raises(Exception) as err:
        get_wave_from_questionnaire_name(questionnaire_name)

    # assert
    assert str(err.value) == "Invalid format for questionnaire name: OPN2101A"


def test_get_wave_from_questionnaire_name():
    assert get_wave_from_questionnaire_name("LMS2101_AA1") == "1"
    assert get_wave_from_questionnaire_name("LMS1234_ZZ2") == "2"


def test_get_wave_from_questionnaire_name_with_invalid_format_raises_error():
    with pytest.raises(Exception) as err:
        get_wave_from_questionnaire_name("ABC1234_AA1")
    assert str(err.value) == "Invalid format for questionnaire name: ABC1234_AA1"