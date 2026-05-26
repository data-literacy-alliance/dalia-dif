"""Client to DALIA website."""

import pystow
import requests
from pydantic import BaseModel

from dalia_dif.dif13 import EducationalResourceDIF13

"""
Example input:

{
  "title": "string",
  "main_url": "string",
  "publication_date": "2026-05-26",
  "description": "string",
  "size_mb": "-9707.",
  "submitted_for_review": true,
  "submitted_at": "2026-05-26T10:42:37.303Z",
  "version": 2147483647,
  "is_active": true,
  "resource": 0,
  "created_by": 0,
  "submitted_by": 0,
  "languages": [
    0
  ],
  "people": [
    0
  ],
  "organizations": [
    0
  ],
  "learning_resource_types": [
    0
  ],
  "disciplines": [
    0
  ],
  "licenses": [
    0
  ],
  "proficiency_levels": [
    0
  ],
  "target_groups": [
    0
  ],
  "file_formats": [
    0
  ],
  "media_types": [
    0
  ]
}
"""


class DALIAUploadRequest(BaseModel):
    """The expected post request body for DALIA resource creation.

    See https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_create
    """


class DALIAUploadResponse(BaseModel):
    """The response returned by DALIA resource creation.

    See: https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_create
    """


class Client:
    """A client to the DALIA Web portal."""

    def __init__(self, *, base: str | None, token: str | None = None) -> None:
        """Initialize a client to the DALIA Web portal."""
        self.token = pystow.get_config("dalia", "token", passthrough=token, raise_on_missing=True)
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Token {self.token}"
        self.base = base or "https://search.dalia.education/api"

    def upload_dif13(self, r: EducationalResourceDIF13 | DALIAUploadRequest) -> DALIAUploadResponse:
        """Upload a learning resource to DALIA."""
        if isinstance(r, EducationalResourceDIF13):
            r = _convert(r)
        res = self.session.post(
            f"{self.base}/curation/resource-contents/",
            json=r.model_dump(exclude_none=True, exclude_unset=True),
        )
        res.raise_for_status()
        return DALIAUploadResponse.model_validate(res.json())


def _convert(r: EducationalResourceDIF13) -> DALIAUploadRequest:
    raise NotImplementedError
