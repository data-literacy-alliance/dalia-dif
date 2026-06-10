"""Client to DALIA website."""

import datetime
import json
import logging
import uuid
from collections.abc import Iterable
from typing import Annotated, Literal, overload

import click
import pystow
import requests
from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic_extra_types.language_code import _index_by_alpha2

from dalia_dif.dif13 import EducationalResourceDIF13

__all__ = [
    "Client",
    "DALIAUploadRequest",
]

logger = logging.getLogger(__name__)


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
    version: int | None = None  # does this need to be set?
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
        self.target_groups = {
            part["uri"]: part["id"]
            for part in self.module.ensure_json(
                url=f"{self.base}/api/curation/target-groups/",
                name="target-groups.json",
            )
        }
        self.target_groups.update(
            {
                "https://purl.org/ontology/modalia#DataSteward": 3,
                "https://purl.org/ontology/modalia#TeacherHighEducation": 11,
            }
        )

        self.proficiency_levels = {
            d["uri"]: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/proficiency-levels/",
                name="proficiency-levels.json",
            )
        }
        self.organizations = self.module.ensure_json(
            url=f"{self.base}/api/curation/organizations/",
            name="organizations.json",
        )
        self.media_types = {
            d["uri"]: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/media-types/",
                name="media-types.json",
            )
        }
        self.licenses: dict[str, int] = {
            d["label"]: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/licenses/",
                name="licenses.json",
            )
        }
        self.learning_resource_types = {
            d["uri"]: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/learning-resource-types/",
                name="learning-resource-types.json",
            )
        }
        self.languages = {
            _index_by_alpha2()[d["code"]].alpha3: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/languages/",
                name="languages.json",
            )
        }
        self.file_formats = {
            d["label"].lower().removeprefix("."): d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/file-formats/",
                name="file-formats.json",
            )
        }
        self.file_formats.update(
            {"PDF": 14, "ZIP": 23, "PPTX": 16, "MD": 9, "MBZ": 8, "MP3": 10, "mpeg-4": 11}
        )
        self.disciplines = {
            d["uri"]: d["id"]
            for d in self.module.ensure_json(
                url=f"{self.base}/api/curation/disciplines/",
                name="disciplines.json",
            )
        }
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

    @overload
    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest
    ) -> requests.Response: ...

    @overload
    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest, *, publish: Literal[True] = ...
    ) -> tuple[requests.Response, requests.Response]: ...

    @overload
    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest, *, publish: Literal[False] = ...
    ) -> requests.Response: ...

    def upload_dif13(
        self, r: EducationalResourceDIF13 | DALIAUploadRequest, *, publish: bool = False
    ) -> requests.Response | tuple[requests.Response, requests.Response]:
        """Upload a learning resource to DALIA."""
        if isinstance(r, EducationalResourceDIF13):
            r = self._convert(r)
        res = self.session.post(
            f"{self.base}/api/curation/resource-contents/",
            json=r.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        if not publish:
            return res

        publish_res = self.publish(res.json()["resource_uuid"])
        return res, publish_res

    def publish(self, uuid_: str | uuid.UUID) -> requests.Response:
        """Publish a learning resource to DALIA.

        see: https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_publish_create
        """
        res = self.session.post(
            f"{self.base}/api/curation/resource-contents/{uuid_}/publish/",
        )
        res.raise_for_status()
        return res

    def _convert(self, r: EducationalResourceDIF13) -> DALIAUploadRequest:  # noqa:C901
        def _ll(lookup: dict[str, int], values: Iterable[str] | None, key: str) -> list[int]:
            rv = []
            for value in values or []:
                if numeric_id := lookup.get(str(value)):
                    rv.append(numeric_id)
                else:
                    logger.warning("missing value in %s: %s", key, value)
            return rv

        target_groups = _ll(self.target_groups, r.target_groups, "target group")
        proficiency_levels = _ll(
            self.proficiency_levels, r.proficiency_levels, "proficicency levels"
        )
        media_types = _ll(self.media_types, r.media_types, "media types")

        licenses = []
        if r.license is None:
            pass
        elif str(r.license) in {
            "http://spdx.org/licenses/unlicensed",
        }:
            pass
        elif str(r.license) == "https://purl.org/ontology/modalia#ProprietaryLicense":
            licenses.append(2)
        elif r.license.startswith("http://spdx.org/licenses/"):
            if license_id := self.licenses.get(r.license.removeprefix("http://spdx.org/licenses/")):
                licenses.append(license_id)
            else:
                logger.warning("could not lookup license: %s", r.license)
        else:
            logger.warning("could not lookup license: %s", r.license)

        learning_resource_types = _ll(
            self.learning_resource_types, r.learning_resource_types, "learning resource types"
        )
        languages = _ll(self.languages, r.languages, "languages")

        ff = (
            [zz for f in r.file_formats if (zz := f.removeprefix(".").lower().strip())]
            if r.file_formats
            else None
        )
        file_formats = _ll(self.file_formats, ff, "file formats")

        disciplines = _ll(self.disciplines, r.disciplines, "disciplines")

        publication_date: datetime.date | None
        if isinstance(r.publication_date, int):
            publication_date = datetime.date(year=r.publication_date, month=1, day=1)
        elif isinstance(r.publication_date, datetime.datetime):
            publication_date = r.publication_date.date()
        else:
            publication_date = r.publication_date

        return DALIAUploadRequest(
            title=r.title,
            main_url=AnyHttpUrl(str(r.links[0])),
            publication_date=publication_date,
            description=r.description,
            created_by=self.current_user_id,
            submitted_at=datetime.datetime.now(),
            submitted_by=self.current_user_id,
            licenses=licenses,
            target_groups=target_groups,
            media_types=media_types,
            proficiency_levels=proficiency_levels,
            learning_resource_types=learning_resource_types,
            languages=languages,
            file_formats=file_formats,
            disciplines=disciplines,
            people=[],
            organizations=[],
        )


def _demo() -> None:
    from pathlib import Path

    import dalia_dif.dif13

    directory = Path("/Users/cthoyt/dev/dalia-curation/curation")

    # load example DIF13 data

    client = Client()

    return
    for path in directory.glob("*.csv"):
        resources = dalia_dif.dif13.read_dif13(path, ignore_missing_description=True)
        for resource in resources:
            client._convert(resource)

    res = client.upload_dif13(resource)
    res_json = res.json()

    click.echo(json.dumps(res.json(), indent=2, ensure_ascii=False))
    res_json["resource_uuid"]  # 7a261e7e-b62a-4766-9767-e259c86eb8de
    # TODO the resource page https://search.dalia.education/admin/curation/resource/
    #  does not have it as published yet


if __name__ == "__main__":
    _demo()
