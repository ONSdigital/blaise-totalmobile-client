from services.blaise_service import IBlaiseService
from services.delete_totalmobile_job_service import DeleteTotalmobileJobService
from services.delete_totalmobile_jobs_service import DeleteTotalmobileJobsService
from services.logging_totalmobile_service import LoggingTotalmobileService
from services.totalmobile_service import ITotalmobileService


def delete_totalmobile_jobs_completed_in_blaise(
    blaise_service: IBlaiseService, totalmobile_service: ITotalmobileService
):
    logging_totalmobile_service = LoggingTotalmobileService(totalmobile_service)
    DeleteTotalmobileJobsService(
        totalmobile_service=logging_totalmobile_service,
        blaise_service=blaise_service,
        delete_totalmobile_job_service=DeleteTotalmobileJobService(
            logging_totalmobile_service
        ),
    ).delete_jobs_for_completed_cases()

    return "Done"
