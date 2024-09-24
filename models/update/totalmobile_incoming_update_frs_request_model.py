from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from app.exceptions.custom_exceptions import InvalidTotalmobileUpdateRequestException
from models.base_model import BaseModel
from models.common.totalmobile.totalmobile_reference_frs_model import (
    IncomingRequest,
    TotalmobileReferenceFRSModel,
)

T = TypeVar("T", bound="TotalMobileIncomingUpdateFRSRequestModel")


@dataclass
class TotalMobileIncomingUpdateFRSRequestModel(BaseModel):
    questionnaire_guid: str
    questionnaire_name: str
    case_id: str
    interviewer_name: str
    interviewer_blaise_login: str

    @classmethod
    def import_request(cls: Type[T], incoming_request: IncomingRequest) -> T:
        if not (cls.dictionary_keys_exist(incoming_request, "Visit", "Identity", "User", "UserAttributes") or cls.dictionary_keys_exist(incoming_request, "Visit", "Identity", "Guid")):
            logging.error("The Totalmobile payload appears to be malformed")
            raise InvalidTotalmobileUpdateRequestException

        reference_model = TotalmobileReferenceFRSModel.from_request(incoming_request)

        total_mobile_case = cls(
            questionnaire_guid= reference_model.questionnaire_guid,
            questionnaire_name=reference_model.questionnaire_name,
            case_id=reference_model.case_id,
            interviewer_name = reference_model.interviewer_name,
            interviewer_blaise_login = reference_model.interviewer_blaise_login,
        )

        return total_mobile_case
