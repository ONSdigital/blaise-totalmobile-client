import json
from structlog.testing import capture_logs

from datetime import datetime
from unittest import mock
from cloud_functions.check_questionnaire_release_date import check_questionnaire_release_date, get_questionnaires_with_todays_release_date, map_questionnaire_case_task_models, QuestionnaireCaseTaskModel, prepare_questionnaire_tasks, create_questionnaire_task_name
from google.cloud import datastore

from appconfig import Config


def entity_builder(key, questionnaire, tmreleasedate):
    entity = datastore.Entity(
        datastore.Key("TmReleaseDate", key, project="test")
    )
    entity["questionnaire"] = questionnaire
    entity["tmreleasedate"] = tmreleasedate
    return entity


@mock.patch("cloud_functions.check_questionnaire_release_date.get_datastore_records")
def test_get_questionnaires_with_todays_release_date_only_returns_questionnaires_with_todays_date(mock_get_datastore_records):
    # arrange
    mock_datastore_entity = [
        entity_builder(
            1, "LMS2111Z", datetime.today()
        ),
        entity_builder(
            2, "LMS2000Z", datetime(2021, 12, 31)
        )
    ]
    mock_get_datastore_records.return_value = mock_datastore_entity

    # act
    result = get_questionnaires_with_todays_release_date()

    # assert
    assert result == ["LMS2111Z"]


@mock.patch("cloud_functions.check_questionnaire_release_date.get_datastore_records")
def test_get_questionnaires_with_todays_release_date_returns_an_empty_list_when_there_are_no_release_dates_for_today(mock_get_datastore_records):
    # arrange
    mock_datastore_entity = [
        entity_builder(
            1, "LMS2111Z", datetime(2021, 12, 31)
        ),
        entity_builder(
            2, "LMS2000Z", datetime(2021, 12, 31)
        )
    ]
    mock_get_datastore_records.return_value = mock_datastore_entity

    # act
    result = get_questionnaires_with_todays_release_date()

    # assert
    assert result == []


@mock.patch("cloud_functions.check_questionnaire_release_date.get_datastore_records")
def test_get_questionnaires_with_todays_release_date_returns_an_empty_list_when_there_are_no_records_in_datastore(mock_get_datastore_records):
    # arrange
    mock_get_datastore_records.return_value = []

    # act
    result = get_questionnaires_with_todays_release_date()

    # assert
    assert result == []


@mock.patch("cloud_functions.check_questionnaire_release_date.get_questionnaires_with_todays_release_date")
def test_check_questionnaire_returns_when_there_are_no_questionnaire_for_release(mock_get_questionnaires_with_todays_release_date):
    # arrange
    mock_get_questionnaires_with_todays_release_date.return_value = []

    # act
    with capture_logs() as cap_logs:
        result = check_questionnaire_release_date()

    # assert
    assert result == "There are no questionnaires for release today"
    assert {'event': 'There are no questionnaires for release today', 'log_level': 'info'} in cap_logs


def test_map_questionnaire_case_task_models_maps_the_correct_list_of_models():
    # arrange
    todays_questionnaires_for_release = ["LMS2111Z", "LMS2112T"]

    # act
    result = map_questionnaire_case_task_models(todays_questionnaires_for_release)

    # assert
    assert result == [QuestionnaireCaseTaskModel(questionnaire="LMS2111Z"), QuestionnaireCaseTaskModel(questionnaire="LMS2112T")]


@mock.patch.object(Config, "from_env")
def test_prepare_case_tasks_returns_an_expected_number_of_tasks_when_given_a_list_of_job_models(
        mock_config_from_env,
):
    # arrange
    mock_config_from_env.return_value = Config(
        "", "", "", "", "", "", "", "", "", "", ""
    )

    model1 = QuestionnaireCaseTaskModel("LMS2111Z")
    model2 = QuestionnaireCaseTaskModel("LMS2112T")

    # act
    result = prepare_questionnaire_tasks([model1, model2])

    # assert
    assert len(result) == 2
    assert result[0] != result[1]


@mock.patch.object(Config, "from_env")
def test_prepare_case_tasks_returns_expected_tasks_when_given_a_list_of_job_models(
        _mock_config_from_env,
):
    # arrange
    _mock_config_from_env.return_value = Config(
        "",
        "",
        "",
        "",
        "totalmobile_jobs_queue_id",
        "cloud_function_name",
        "project",
        "region",
        "rest_api_url",
        "gusty",
        "cloud_function_sa",
    )

    model1 = QuestionnaireCaseTaskModel("LMS2101A")
    model2 = QuestionnaireCaseTaskModel("LMS2101A")

    # act
    result = prepare_questionnaire_tasks([model1, model2])

    # assert
    assert result[0].parent == "totalmobile_jobs_queue_id"
    assert result[0].task.name.startswith(
        "totalmobile_jobs_queue_id/tasks/LMS2101A-"
    )
    assert (
            result[0].task.http_request.url
            == "https://region-project.cloudfunctions.net/cloud_function_name"
    )
    assert result[0].task.http_request.body == json.dumps({"questionnaire": "LMS2101A"}).encode()
    assert (
            result[0].task.http_request.oidc_token.service_account_email
            == "cloud_function_sa"
    )

    assert result[1].parent == "totalmobile_jobs_queue_id"
    assert result[1].task.name.startswith(
        "totalmobile_jobs_queue_id/tasks/LMS2101A-"
    )
    assert (
            result[1].task.http_request.url
            == "https://region-project.cloudfunctions.net/cloud_function_name"
    )
    assert result[1].task.http_request.body == json.dumps({"questionnaire": "LMS2101A"}).encode()
    assert (
            result[1].task.http_request.oidc_token.service_account_email
            == "cloud_function_sa"
    )


def test_create_questionnaire_task_name_returns_unique_name_each_time_when_passed_the_same_model():
    # arrange
    model = QuestionnaireCaseTaskModel("LMS2101A")

    # act
    result1 = create_questionnaire_task_name(model)
    result2 = create_questionnaire_task_name(model)

    # assert
    assert result1 != result2