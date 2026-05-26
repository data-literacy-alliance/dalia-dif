"""Client to DALIA website."""

import datetime
from typing import Annotated

import pystow
import requests
from pydantic import AnyHttpUrl, BaseModel, Field

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

    title: str
    main_url: AnyHttpUrl
    publication_date: Annotated[datetime.date, Field(default_factory=datetime.date.today)]
    description: str
    size_mb: Annotated[str | None, Field(examples=["-9707."])] = None  #
    submitted_for_review: bool = True
    submitted_at: Annotated[datetime.datetime, Field(default_factory=datetime.datetime.now)]
    version: int = 1
    is_active: bool = True
    resource: int
    created_by: int
    submitted_by: int
    languages: Annotated[list[int], Field(default_factory=list)]
    people: Annotated[list[int], Field(default_factory=list)]
    organizations: Annotated[list[int], Field(default_factory=list)]
    learning_resource_types: Annotated[list[int], Field(default_factory=list)]
    disciplines: Annotated[list[int], Field(default_factory=list)]
    licenses: Annotated[list[int], Field(default_factory=list)]
    proficiency_levels: Annotated[list[int], Field(default_factory=list)]
    target_groups: Annotated[list[int], Field(default_factory=list)]
    file_formats: Annotated[list[int], Field(default_factory=list)]
    media_types: Annotated[list[int], Field(default_factory=list)]


class DALIAUploadResponse(BaseModel):
    """The response returned by DALIA resource creation.

    See: https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_create
    """


class Client:
    """A client to the DALIA Web portal."""

    def __init__(self, *, base: str | None = None, token: str | None = None) -> None:
        """Initialize a client to the DALIA Web portal."""
        self.token = pystow.get_config("dalia", "token", passthrough=token, raise_on_missing=True)
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Token {self.token}"
        self.base = base or "https://search.dalia.education/api"
        self.module = pystow.module("dalia", "web-resources")

        # need to cache some stuff on first try
        self.relation_types = self.module.ensure_json(
            url=f"{self.base}/curation/relation-types/",
            name="relation-types.json",
        )
        self.target_groups = self.module.ensure_json(
            url=f"{self.base}/curation/target-groups/",
            name="target-groups.json",
        )
        self.proficiency_levels = self.module.ensure_json(
            url=f"{self.base}/curation/proficiency-levels/",
            name="proficiency-levels.json",
        )
        self.organizations = self.module.ensure_json(
            url=f"{self.base}/curation/organizations/",
            name="organizations.json",
        )
        self.media_types = self.module.ensure_json(
            url=f"{self.base}/curation/media-types/",
            name="media-types.json",
        )
        self.licenses = self.module.ensure_json(
            url=f"{self.base}/curation/licenses/",
            name="licenses.json",
        )
        self.learning_resource_types = self.module.ensure_json(
            url=f"{self.base}/curation/learning-resource-types/",
            name="learning-resource-types.json",
        )
        self.languages = self.module.ensure_json(
            url=f"{self.base}/curation/languages/",
            name="languages.json",
        )
        self.file_formats = self.module.ensure_json(
            url=f"{self.base}/curation/file-formats/",
            name="file-formats.json",
        )
        self.disciplines = self.module.ensure_json(
            url=f"{self.base}/curation/disciplines/",
            name="disciplines.json",
        )
        self.communities = self.module.ensure_json(
            url=f"{self.base}/curation/communities/",
            name="communities.json",
        )

    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest, *, parse: bool = False
    ) -> DALIAUploadResponse:
        """Upload a learning resource to DALIA."""
        if isinstance(r, EducationalResourceDIF13):
            r = self._convert(r)
        res = self.session.post(
            f"{self.base}/curation/resource-contents/",
            json=r.model_dump(exclude_none=True, exclude_unset=True),
        )
        res.raise_for_status()
        rv = res.json()
        if parse:
            rv = DALIAUploadResponse.model_validate(rv)
        return rv

    def _convert(self, r: EducationalResourceDIF13) -> DALIAUploadRequest:
        raise NotImplementedError


if __name__ == "__main__":
    client = Client()
