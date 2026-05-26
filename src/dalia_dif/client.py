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
    publication_date: datetime.date | None = None
    description: str | None = None
    size_mb: Annotated[str | None, Field(examples=["-9707."])] = None  #
    submitted_for_review: bool = True
    submitted_at: Annotated[datetime.datetime, Field(default_factory=datetime.datetime.now)]
    version: int = 1
    is_active: bool = True
    resource: int | None = None
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
        self.base = base or "https://search.dalia.education"
        self.module = pystow.module("dalia", "web-resources")

        # need to cache some stuff on first try
        self.relation_types = self.module.ensure_json(
            url=f"{self.base}/api/curation/relation-types/",
            name="relation-types.json",
        )
        self.target_groups = self.module.ensure_json(
            url=f"{self.base}/api/curation/target-groups/",
            name="target-groups.json",
        )
        self.proficiency_levels = self.module.ensure_json(
            url=f"{self.base}/api/curation/proficiency-levels/",
            name="proficiency-levels.json",
        )
        self.organizations = self.module.ensure_json(
            url=f"{self.base}/api/curation/organizations/",
            name="organizations.json",
        )
        self.media_types = self.module.ensure_json(
            url=f"{self.base}/api/curation/media-types/",
            name="media-types.json",
        )
        self.licenses = self.module.ensure_json(
            url=f"{self.base}/api/curation/licenses/",
            name="licenses.json",
        )
        self.license_lookup: dict[str, int] = {
            d['label']: d['id']
            for d in self.licenses
        }

        self.learning_resource_types = self.module.ensure_json(
            url=f"{self.base}/api/curation/learning-resource-types/",
            name="learning-resource-types.json",
        )
        self.languages = self.module.ensure_json(
            url=f"{self.base}/api/curation/languages/",
            name="languages.json",
        )
        self.file_formats = self.module.ensure_json(
            url=f"{self.base}/api/curation/file-formats/",
            name="file-formats.json",
        )
        self.disciplines = self.module.ensure_json(
            url=f"{self.base}/api/curation/disciplines/",
            name="disciplines.json",
        )
        self.communities = self.module.ensure_json(
            url=f"{self.base}/api/curation/communities/",
            name="communities.json",
        )
        self.current_user = self.module.ensure_json(
            url=f"{self.base}/api/v1/auth/me/",
            name=f"{self.token}.json",
        )
        self.current_user_id = self.current_user["id"]
        self.current_user_username = self.current_user["username"]
        self.current_user_email = self.current_user["email"]

    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest, *, parse: bool = False
    ) -> DALIAUploadResponse | requests.Response:
        """Upload a learning resource to DALIA."""
        if isinstance(r, EducationalResourceDIF13):
            r = self._convert(r)
        res = self.session.post(
            f"{self.base}/curation/resource-contents/",
            json=r.model_dump(exclude_none=True, exclude_unset=True),
        )
        res.raise_for_status()
        if parse:
            return DALIAUploadResponse.model_validate(res.json())
        return res

    def _convert(self, r: EducationalResourceDIF13) -> DALIAUploadRequest:
        if r.license is None:
            ll = None
        elif r.license.startswith("http://spdx.org/licenses/"):
            ll = self.license_lookup[r.license.removeprefix("http://spdx.org/licenses/")]
        elif str(r.license) == "https://purl.org/ontology/modalia#ProprietaryLicense":
            ll = 2
        else:
            print(f"CANT HANDLE LICENSE: {r.license}")
            ll = None

        if isinstance(r.publication_date, int):
            publication_date = datetime.date(year=r.publication_date, month=1, day=1)
        else:
            publication_date = r.publication_date

        return DALIAUploadRequest(
            title=r.title,
            main_url=r.links[0],
            publication_date=publication_date,
            description=r.description,
            created_by=self.current_user_id,
            submitted_by=self.current_user_id,
            licenses=[ll] if ll else [],
        )


def _demo() -> None:
    import dalia_dif.dif13

    # load example DIF13 data
    path = "/Users/cthoyt/dev/dalia-curation/curation/dalia_curation_2026_04.csv"
    resources = dalia_dif.dif13.read_dif13(path, ignore_missing_description=True)

    client = Client()

    import pprint

    # pprint.pprint(client.licenses)

    for resource in resources:
        client._convert(resource)
    # client.upload_dif13(resources[0])


if __name__ == "__main__":
    _demo()
