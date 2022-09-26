from collections import defaultdict
from typing import Callable, List

from models.totalmobile.totalmobile_get_jobs_response_model import (
    TotalmobileGetJobsResponseModel,
)
from models.totalmobile.totalmobile_world_model import TotalmobileWorldModel, World


class FakeTotalmobileService:
    def __init__(self):
        self._jobs = {}
        self._delete_jobs = defaultdict(lambda: 0)
        self._errors_when_method_is_called = []

    def method_throws_exception(self, method_name: str):
        self._errors_when_method_is_called.append(method_name)

    def add_job(self, reference: str, visit_complete: bool = False) -> None:
        self._jobs[reference] = {
            "visitComplete": visit_complete,
            "identity": {"reference": reference},
        }

    def job_exists(self, reference: str) -> bool:
        return reference in self._jobs

    def delete_job_has_been_called(self, job: str) -> bool:
        return job in self._delete_jobs

    def delete_job(self, world_id: str, job: str, reason: str = "0") -> None:
        if "delete_job" in self._errors_when_method_is_called:
            raise Exception("get_jobs_model has errored")

        self._delete_jobs[job] += 1

    def get_world_model(self) -> TotalmobileWorldModel:
        if "get_world_model" in self._errors_when_method_is_called:
            raise Exception("get_jobs_model has errored")

        return TotalmobileWorldModel(
            worlds=[World(region="Region 1", id="13013122-d69f-4d6b-gu1d-721f190c4479")]
        )

    def get_jobs_model(self, world_id: str) -> TotalmobileGetJobsResponseModel:
        if "get_jobs_model" in self._errors_when_method_is_called:
            raise Exception("get_jobs_model has errored")

        if not self._jobs:
            raise Exception

        return TotalmobileGetJobsResponseModel.from_get_jobs_response(
            self._jobs.values()
        )
