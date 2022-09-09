from collections import defaultdict

from models.totalmobile.totalmobile_jobs_response_model import (
    TotalmobileJobsResponseModel,
)
from models.totalmobile.totalmobile_world_model import TotalmobileWorldModel, World


def nested_dict() -> defaultdict:
    return defaultdict(nested_dict)


class FakeTotalmobileService:
    def __init__(self):
        self._jobs = {}
        self._delete_jobs = nested_dict()

    def add_job(self, reference: str) -> None:
        self._jobs[reference] = {}

    def delete_job(self, world_id: str, job: str, reason: str = "0") -> None:
        self._delete_jobs[job] = True

    def job_exists(self, reference: str) -> bool:
        return reference in self._jobs

    def delete_job_has_been_called(self, job: str) -> bool:
        return job in self._delete_jobs

    def get_world_model(self) -> TotalmobileWorldModel:
        return TotalmobileWorldModel(
            worlds=[World(region="Region 1", id="13013122-d69f-4d6b-gu1d-721f190c4479")]
        )

    def get_jobs_model(self, world_id: str) -> TotalmobileJobsResponseModel:
        for key in self._jobs.keys():
            return TotalmobileJobsResponseModel(
                [
                    {"visitComplete": False, "identity": {"reference": f"{key}"}},
                ]
            )

        raise Exception
