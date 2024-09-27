import logging
from models.update.totalmobile_incoming_update_request_model import (
    TotalMobileIncomingUpdateRequestModel,
)
from models.update.totalmobile_incoming_update_frs_request_model import (
    TotalMobileIncomingUpdateFRSRequestModel,
)
from services.update.update_case_service import UpdateCaseService
from services.update.update_frs_case_allocation_service import UpdateFRSCaseService


def submit_form_result_request_handler(request, update_case_service: UpdateCaseService):
    data = request.get_json()
    totalmobile_case = TotalMobileIncomingUpdateRequestModel.import_request(data)
    update_case_service.update_case(totalmobile_case)

def create_visit_request_handler(request, update_frs_case_allocation_service: UpdateFRSCaseService):
    data = request.get_json()
    logging.info(str(data))
    totalmobile_frs_case = TotalMobileIncomingUpdateFRSRequestModel.import_request(data)
    logging.info(str(totalmobile_frs_case))
    update_frs_case_allocation_service.update_case(totalmobile_frs_case)
    

def update_visit_status_request_handler(request):
    data = request.get_json()
    return
