import json
from unittest import mock

import flask
import pytest
import logging
from models.case_model import CaseModel, UacChunks

from tests.helpers import config_helper
from client.optimise import OptimiseClient
from cloud_functions.create_questionnaire_case_tasks import (
    create_questionnaire_case_tasks,
    create_task_name,
    map_totalmobile_job_models,
    validate_request,
    append_uacs_to_retained_case,
    get_cases_with_valid_world_ids
)
from models.totalmobile_job_model import TotalmobileJobModel


def test_create_task_name_returns_correct_name_when_called():
    questionnaire_case_model = CaseModel(case_id ="90001")
    model = TotalmobileJobModel("OPN2101A", "world", questionnaire_case_model.to_dict())

    assert create_task_name(model).startswith("OPN2101A-90001-")


def test_create_task_name_returns_unique_name_each_time_when_passed_the_same_model():
    questionnaire_case_model = CaseModel(case_id ="90001")
    model = TotalmobileJobModel("OPN2101A", "world", questionnaire_case_model.to_dict())

    assert create_task_name(model) != create_task_name(model)



def test_map_totalmobile_job_models_maps_the_correct_list_of_models():
    # arrange
    questionnaire_name = "OPN2101A"

    case_data = [
        CaseModel(case_id ="10010", outcome_code ="110"),
        CaseModel(case_id ="10020", outcome_code ="120"),
        CaseModel(case_id ="10030", outcome_code ="130")
    ]

    world_ids = [
        "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "3fa85f64-5717-4562-b3fc-2c963f66afa9",
    ]

    # act
    result = map_totalmobile_job_models(case_data, world_ids, questionnaire_name)

    # assert
    assert result == [
        TotalmobileJobModel(
            "OPN2101A", "3fa85f64-5717-4562-b3fc-2c963f66afa6", case={'qiD.Serial_Number': '10010', 'dataModelName': '', 'qDataBag.TLA': '', 'qDataBag.Wave': '', 'qDataBag.Prem1': '', 'qDataBag.Prem2': '', 'qDataBag.Prem3': '', 'qDataBag.District': '', 'qDataBag.PostTown': '', 'qDataBag.PostCode': '', 'qDataBag.TelNo': '', 'qDataBag.TelNo2': '', 'telNoAppt': '', 'hOut': '110', 'qDataBag.UPRN_Latitude': '', 'qDataBag.UPRN_Longitude': '', 'qDataBag.Priority': '', 'qDataBag.FieldRegion': '', 'qDataBag.FieldTeam': '', 'qDataBag.WaveComDTE': '', 'uac_chunks': {'uac1': '', 'uac2': '', 'uac3': ''}}
        ),
        TotalmobileJobModel(
            "OPN2101A", "3fa85f64-5717-4562-b3fc-2c963f66afa7", case={'qiD.Serial_Number': '10020', 'dataModelName': '', 'qDataBag.TLA': '', 'qDataBag.Wave': '', 'qDataBag.Prem1': '', 'qDataBag.Prem2': '', 'qDataBag.Prem3': '', 'qDataBag.District': '', 'qDataBag.PostTown': '', 'qDataBag.PostCode': '', 'qDataBag.TelNo': '', 'qDataBag.TelNo2': '', 'telNoAppt': '', 'hOut': '120', 'qDataBag.UPRN_Latitude': '', 'qDataBag.UPRN_Longitude': '', 'qDataBag.Priority': '', 'qDataBag.FieldRegion': '', 'qDataBag.FieldTeam': '', 'qDataBag.WaveComDTE': '', 'uac_chunks': {'uac1': '', 'uac2': '', 'uac3': ''}}
        ),
        TotalmobileJobModel(
            "OPN2101A", "3fa85f64-5717-4562-b3fc-2c963f66afa9", case={'qiD.Serial_Number': '10030', 'dataModelName': '', 'qDataBag.TLA': '', 'qDataBag.Wave': '', 'qDataBag.Prem1': '', 'qDataBag.Prem2': '', 'qDataBag.Prem3': '', 'qDataBag.District': '', 'qDataBag.PostTown': '', 'qDataBag.PostCode': '', 'qDataBag.TelNo': '', 'qDataBag.TelNo2': '', 'telNoAppt': '', 'hOut': '130', 'qDataBag.UPRN_Latitude': '', 'qDataBag.UPRN_Longitude': '', 'qDataBag.Priority': '', 'qDataBag.FieldRegion': '', 'qDataBag.FieldTeam': '', 'qDataBag.WaveComDTE': '', 'uac_chunks': {'uac1': '', 'uac2': '', 'uac3': ''}}
        ),
    ]


def test_validate_request(mock_create_job_task):
    validate_request(mock_create_job_task)


def test_validate_request_when_missing_fields():
    with pytest.raises(Exception) as err:
        validate_request({"world_id": ""})
    assert (
            str(err.value) == "Required fields missing from request payload: ['questionnaire']"
    )


@mock.patch("cloud_functions.create_questionnaire_case_tasks.append_uacs_to_retained_case")
@mock.patch("services.world_id_service.get_world_ids")
@mock.patch("services.questionnaire_service.get_eligible_cases")
@mock.patch("services.questionnaire_service.get_uacs")
@mock.patch("cloud_functions.create_questionnaire_case_tasks.run_async_tasks")
@mock.patch("cloud_functions.create_questionnaire_case_tasks.get_cases_with_valid_world_ids")
def test_create_case_tasks_for_questionnaire(
        mock_get_cases_with_valid_world_ids,
        mock_run_async_tasks,
        mock_get_uacs,
        mock_get_eligible_cases,
        mock_get_world_ids,
        mock_append_uacs_to_retained_case
):
    # arrange
    config = config_helper.get_default_config()
    mock_request = flask.Request.from_values(json={"questionnaire": "LMS2101_AA1"})

    mock_get_eligible_cases.return_value = [
        CaseModel(
            case_id="10010",
            telephone_number_1="",
            telephone_number_2="",
            appointment_telephone_number="",
            wave="1",
            priority="1",
            outcome_code="310",
        ),
    ]

    mock_get_uacs.return_value = {
        "10010": {
            "instrument_name": "LMS2101_AA1",
            "case_id": "10010",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3991"
            },
            "full_uac": "817647263991"
        }
    }
    mock_append_uacs_to_retained_case.return_value = [
        CaseModel(
            case_id="10010",
            uac_chunks=UacChunks(
                uac1="8176",
                uac2="4726",
                uac3="3991"
            )
        )
    ]

    mock_get_world_ids.return_value = {
        "Region 1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }

    mock_get_cases_with_valid_world_ids.return_value = [
        CaseModel(
            case_id="10010",
            telephone_number_1="",
            telephone_number_2="",
            appointment_telephone_number="",
            wave="1",
            priority="1",
            outcome_code="310",
            uac_chunks=UacChunks(
                uac1="8176",
                uac2="4726",
                uac3="3991"
            )
        )]

    # act
    result = create_questionnaire_case_tasks(mock_request, config)

    # assert
    mock_get_world_ids.assert_called_with(config)
    mock_get_eligible_cases.assert_called_with("LMS2101_AA1", config)

    mock_run_async_tasks.assert_called_once()
    kwargs = mock_run_async_tasks.call_args.kwargs
    assert kwargs['cloud_function'] == "totalmobile_job_cloud_function"
    assert kwargs['queue_id'] == "totalmobile_jobs_queue_id"
    assert len(kwargs['tasks']) == 1
    task = kwargs['tasks'][0]
    assert task[0][0:3] == "LMS"
    assert json.loads(task[1]) == {
        'questionnaire': 'LMS2101_AA1',
        'world_id': 'Region 1',
        'case': {
            'qiD.Serial_Number': '10010',
            'dataModelName': '',
            'qDataBag.TLA': '',
            'qDataBag.Wave': '1',
            'qDataBag.Prem1': '',
            'qDataBag.Prem2': '',
            'qDataBag.Prem3': '',
            'qDataBag.District': '',
            'qDataBag.PostTown': '',
            'qDataBag.PostCode': '',
            'qDataBag.TelNo': '',
            'qDataBag.TelNo2': '',
            'telNoAppt': '',
            'hOut': '310',
            'qDataBag.UPRN_Latitude': '',
            'qDataBag.UPRN_Longitude': '',
            'qDataBag.Priority': '1',
            'qDataBag.FieldRegion': '',
            'qDataBag.FieldTeam': '',
            'qDataBag.WaveComDTE': '',
            'uac_chunks': {
                'uac1': '8176',
                'uac2': '4726',
                'uac3': '3991'
            }
        }
    }
    assert result == "Done"


@mock.patch("services.questionnaire_service.get_eligible_cases")
@mock.patch("cloud_functions.create_questionnaire_case_tasks.run_async_tasks")
def test_create_questionnaire_case_tasks_when_no_eligible_cases(
        mock_run_async_tasks,
        mock_get_eligible_cases
):
    # arrange
    mock_request = flask.Request.from_values(json={"questionnaire": "LMS2101_AA1"})
    config = config_helper.get_default_config()
    mock_get_eligible_cases.return_value = []

    # act
    result = create_questionnaire_case_tasks(mock_request, config)

    # assert
    mock_run_async_tasks.assert_not_called()
    assert result == "Exiting as no eligible cases to send for questionnaire LMS2101_AA1"


def test_create_questionnaire_case_tasks_errors_if_misssing_questionnaire():
    # arrange
    mock_request = flask.Request.from_values(json={"blah": "blah"})
    config = config_helper.get_default_config()
    # assert
    with pytest.raises(Exception) as err:
        create_questionnaire_case_tasks(mock_request, config)
    assert (
            str(err.value) == "Required fields missing from request payload: ['questionnaire']"
    )

@mock.patch.object(OptimiseClient, "get_worlds")
def test_get_cases_with_valid_world_ids_logs_a_console_error_when_given_an_unknown_region(_mock_optimise_client,
                                                                                          caplog):
    filtered_cases = [CaseModel(field_region="Risca")]
    world_ids = {
        "Region 1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }

    get_cases_with_valid_world_ids(filtered_cases, world_ids)

    assert ('root', logging.WARNING, 'Unsupported world: Risca') in caplog.record_tuples


@mock.patch.object(OptimiseClient, "get_worlds")
def test_get_cases_with_valid_world_ids_logs_a_console_error_and_returns_data_when_given_an_unknown_world_and_a_known_world(
        _mock_optimise_client, caplog):
    filtered_cases = [CaseModel(field_region="Risca"),
                      CaseModel(field_region="Region 1")]
    world_ids = {
        "Region 1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }

    cases_with_valid_world_ids = get_cases_with_valid_world_ids(filtered_cases, world_ids)

    assert len(cases_with_valid_world_ids) == 1
    assert cases_with_valid_world_ids == [CaseModel(field_region="Region 1")]
    assert ('root', logging.WARNING, 'Unsupported world: Risca') in caplog.record_tuples


@mock.patch.object(OptimiseClient, "get_worlds")
def test_get_cases_with_valid_world_ids_logs_a_console_error_when_field_region_is_an_empty_value(_mock_optimise_client,
                                                                                                 caplog):
    filtered_cases = [CaseModel(field_region="")]
    world_ids = {
        "Region 1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }

    get_cases_with_valid_world_ids(filtered_cases, world_ids)

    assert ('root', logging.WARNING, 'Case rejected. Missing Field Region') in caplog.record_tuples


@mock.patch.object(OptimiseClient, "get_worlds")
def test_get_world_ids_logs_a_console_error_and_returns_data_when_given_an_unknown_world_and_a_known_world_and_a_known_world(
        _mock_optimise_client, caplog):
    config = config_helper.get_default_config()

    filtered_cases = [CaseModel(field_region=""),
                      CaseModel(field_region="Region 1")]

    world_ids = {
        "Region 1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }

    cases_with_valid_world_ids = get_cases_with_valid_world_ids(filtered_cases, world_ids)

    assert len(cases_with_valid_world_ids) == 1
    assert cases_with_valid_world_ids == [CaseModel(field_region="Region 1")]
    assert ('root', logging.WARNING, 'Case rejected. Missing Field Region') in caplog.record_tuples


def test_uacs_are_correctly_appended_to_case_data():
    case_uacs = {
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

    filtered_cases = [CaseModel(
        case_id = "10030",
        telephone_number_1 = "", 
        telephone_number_2 = "", 
        appointment_telephone_number = "",
        wave = "1", 
        priority = "1", 
        outcome_code = "310")]    

    result = append_uacs_to_retained_case(filtered_cases, case_uacs)
    assert result == [CaseModel(
                case_id = "10030",
                telephone_number_1 = "", 
                telephone_number_2 = "", 
                appointment_telephone_number = "",
                wave = "1", 
                priority = "1", 
                outcome_code = "310",
                uac_chunks = UacChunks(
                    uac1 = "8176",
                    uac2 = "4726",
                    uac3 = "3993"
                ))]  


def test_uacs_with_blank_values_are_appended_to_case_data_when_case_id_not_found_in_bus():
    case_uacs = {
        "10000": {
            "instrument_name": "OPN2101A",
            "case_id": "10000",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3991"
            },
            "full_uac": "817647263991"
        },
    }

    filtered_cases = [CaseModel(
        case_id = "10030",
        telephone_number_1 = "", 
        telephone_number_2 = "", 
        appointment_telephone_number = "",
        wave = "1", 
        priority = "1", 
        outcome_code = "310")]    


    result = append_uacs_to_retained_case(filtered_cases, case_uacs)
    assert result == [CaseModel(
                case_id = "10030",
                telephone_number_1 = "", 
                telephone_number_2 = "", 
                appointment_telephone_number = "",
                wave = "1", 
                priority = "1", 
                outcome_code = "310",
                uac_chunks = UacChunks(
                    uac1 = "",
                    uac2 = "",
                    uac3 = ""
                ))]   
    

def test_an_error_is_logged_when_the_case_id_is_not_found_in_bus(caplog):
    case_uacs = {
        "10000": {
            "instrument_name": "OPN2101A",
            "case_id": "10000",
            "uac_chunks": {
                "uac1": "8176",
                "uac2": "4726",
                "uac3": "3991"
            },
            "full_uac": "817647263991"
        },
    }

    filtered_cases = [CaseModel(
        case_id = "10030",
        telephone_number_1 = "", 
        telephone_number_2 = "", 
        appointment_telephone_number = "",
        wave = "1", 
        priority = "1", 
        outcome_code = "310")]    

    result = append_uacs_to_retained_case(filtered_cases, case_uacs)
    assert ('root', logging.WARNING, 'Serial number 10030 not found in BUS') in caplog.record_tuples
