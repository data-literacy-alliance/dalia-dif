"""Client to DALIA website."""

import datetime
import logging
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Any, Self, cast

import click
import pystow
import requests
from pydantic import UUID4, AnyHttpUrl, BaseModel, Field
from pydantic_extra_types.language_code import _index_by_alpha2
from tqdm import tqdm
from unidecode import unidecode

import dalia_dif.dif13
from dalia_dif.dif13 import AuthorDIF13, EducationalResourceDIF13
from dalia_dif.dif13.community import read_communities

__all__ = [
    "Client",
    "DALIAUploadRequest",
]

from dalia_dif.dif13.community import Community

logger = logging.getLogger(__name__)


class PersonRequest(BaseModel):
    """A post request for a person."""

    first_name: str
    last_name: str
    orcid: Annotated[str | None, Field(pattern=r"^orcid:\d{4}-\d{4}-\d{4}-\d{3}(\d|X)$")] = None


class OrganizationRequest(BaseModel):
    """A post request for a community."""

    name: str
    ror_id: str | None = None
    homepage: str | None = None


def _slugify_community(s: str) -> str:
    return (
        cast(str, unidecode(s))
        .lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace("@", "")
        .replace("+", "plus")
        .replace("(", "")
        .replace(")", "")
        .replace("&", "and")
        .replace("--", "-")
    )


class CommunityRequest(BaseModel):
    """A post request for a community.

    See https://search.dalia.education/api/docs/#/Curation%20-%20Communities/api_curation_communities_create
    """

    title: str
    uuid: UUID4
    slug: str | None = None
    description: str | None = None

    @classmethod
    def from_community(cls, community: Community) -> Self:
        return cls(
            title=community.title,
            uuid=community.uuid,
            slug=_slugify_community(community.title),
        )


class RelationRequest(BaseModel):
    community: int
    relation_type: int
    content: int


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
    keywords: Annotated[list[str], Field(default_factory=list)]


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
        self.relation_type_slug = {rt["code"]: rt["id"] for rt in self.relation_types}

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
            url=f"{self.base}/api/curation/communities/", name="communities.json", force=True
        )
        self.uuid_to_community = {
            community["uuid"]: community["id"] for community in self.communities
        }
        self.slug_to_community: dict[str, int] = {
            community["slug"]: community["id"] for community in self.communities
        }

        self.organizations = self.module.ensure_json(
            url=f"{self.base}/api/curation/organizations/", name="organizations.json", force=True
        )
        self.name_to_organization: dict[str, int] = {
            organization["name"]: organization["id"] for organization in self.organizations
        }
        self.ror_uri_to_organization = {
            ror_uri: organization["id"]
            for organization in self.organizations
            if (ror_uri := organization.get("ror_id"))
        }

        self.people = self.module.ensure_json(
            url=f"{self.base}/api/curation/persons/",
            name="people.json",
            force=True,  # this is going to get updated each time
        )
        self.name_to_person: dict[tuple[str, str], int] = {
            (person["first_name"], person["last_name"]): person["id"] for person in self.people
        }
        self.orcid_to_person: dict[str, int] = {
            orcid: person["id"] for person in self.people if (orcid := person.get("orcid"))
        }

        self.current_user = self.module.ensure_json(
            url=f"{self.base}/api/v1/auth/me/",
            name=f"{self.token}.json",
        )
        self.current_user_id = self.current_user["id"]
        self.current_user_username = self.current_user["username"]
        self.current_user_email = self.current_user["email"]

    def upload_dif13(
        self, r: EducationalResourceDIF13, *, publish: bool = False, communities: list[Community]
    ) -> requests.Response:
        """Upload a learning resource to DALIA.

        See: https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_create
        """
        res = self.session.post(
            f"{self.base}/api/curation/resource-contents/",
            json=self._convert(r).model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        res_json = res.json()

        if publish:
            # important to use the uuid and not resource_uuid, these are different
            self.publish(res_json["uuid"])

        uuid_to_community_id: dict[str, int] = {
            str(community.uuid): xx
            for community in communities
            if (xx := self.slug_to_community.get(_slugify_community(community.title))) is not None
        }

        database_id = res_json["id"]
        # prepare https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20Relations/api_curation_community_relations_create
        for community_uris, relation_type in [
            (r.supporting_communities, self.relation_type_slug["supporting"]),
            (r.recommending_communities, self.relation_type_slug["recommending"]),
        ]:
            for community_uri in community_uris:
                community_uuid = community_uri.removeprefix("https://id.dalia.education/community/")
                if community_id := uuid_to_community_id.get(community_uuid):
                    relation_request = RelationRequest(
                        community=community_id, relation_type=relation_type, content=database_id
                    )
                    try:
                        self._upload_community_relation(relation_request)
                    except requests.exceptions.HTTPError as err:
                        tqdm.write(
                            f"unable to establish link between {r.title} (id:{database_id}) and "
                            f"community: {community_uri} (id:{community_id}). {err.response.text}"
                        )
        return res

    def _upload_community_relation(self, rr: RelationRequest) -> int:
        """See https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20Relations/api_curation_community_relations_create."""
        res = self.session.post(
            f"{self.base}/api/curation/community-relations/",
            json=rr.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        res_json = res.json()
        database_id = cast(int, res_json["id"])
        return database_id

    def publish(self, uuid_: str | uuid.UUID) -> requests.Response:
        """Publish a learning resource to DALIA.

        see: https://search.dalia.education/api/docs/#/Curation%20-%20Resource%20contents/api_curation_resource_contents_publish_create
        """
        res = self.session.post(
            f"{self.base}/api/curation/resource-contents/{uuid_}/publish/",
        )
        res.raise_for_status()
        return res

    def get_resources(self, *, page_size: int | None = None) -> list[dict[str, Any]]:
        """Get all resources."""
        if page_size is None:
            page_size = 1_000
        oers = []
        next_url = f"{self.base}/api/curation/resource-contents/"
        while next_url:
            res = self.session.get(next_url, params={"page_size": page_size})
            res.raise_for_status()
            res_json = res.json()
            oers.extend(res_json["results"])
            next_url = res_json.get("next")
        return oers

    def _create_community(self, community: CommunityRequest | Community) -> int:
        """Create a community and return their database ID.

        See: https://search.dalia.education/api/docs/#/Curation%20-%20Communities/api_curation_communities_create
        """
        if isinstance(community, Community):
            community = CommunityRequest.from_community(community)
        res = self.session.post(
            f"{self.base}/api/curation/communities/",
            json=community.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        res_json = res.json()
        database_id = cast(int, res_json["id"])
        return database_id

    def _create_author(self, person: PersonRequest) -> int:
        """Create a person and return their database ID."""
        res = self.session.post(
            f"{self.base}/api/curation/persons/",
            json=person.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        res_json = res.json()
        database_id = cast(int, res_json["id"])
        if person.orcid:
            self.orcid_to_person[person.orcid] = database_id
        self.name_to_person[person.first_name, person.last_name] = database_id
        return database_id

    def _create_organization(self, org: OrganizationRequest) -> int:
        res = self.session.post(
            f"{self.base}/api/curation/organizations/",
            json=org.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        res.raise_for_status()
        res_json = res.json()
        database_id = cast(int, res_json["id"])
        if org.ror_id:
            self.ror_uri_to_organization[org.ror_id] = database_id
        self.name_to_organization[org.name] = database_id
        return database_id

    def _convert(  # noqa:C901
        self,
        r: EducationalResourceDIF13,
        dry: bool = False,
    ) -> DALIAUploadRequest:
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

        people: list[int] = []
        organizations: list[int] = []
        for author in r.authors or []:
            if not isinstance(author, AuthorDIF13):
                if author.ror and (
                    lookup := self.ror_uri_to_organization.get(
                        author.ror.removeprefix("https://ror.org/")
                    )
                ):
                    organizations.append(lookup)
                elif lookup2 := self.name_to_organization.get(author.name):
                    organizations.append(lookup2)
                elif dry:
                    _write(f"  would create organization: {author.name} ({author.ror or 'no ROR'})")
                else:
                    organizations.append(
                        self._create_organization(
                            OrganizationRequest(name=author.name, ror_id=author.ror)
                        )
                    )
            else:
                if author.orcid and (
                    lookup := self.orcid_to_person.get(
                        author.orcid.removeprefix("https://orcid.org/")
                    )
                ):
                    people.append(lookup)
                elif lookup2 := self.name_to_person.get((author.given_name, author.family_name)):
                    people.append(lookup2)
                elif dry:
                    _write(
                        f"  would create author: {author.given_name} {author.family_name} "
                        f"({author.orcid or 'no orcid'})"
                    )
                else:
                    tqdm.write(
                        f"creating author: {author.given_name} {author.family_name} "
                        f"({author.orcid})"
                    )
                    people.append(
                        self._create_author(
                            PersonRequest(
                                first_name=author.given_name,
                                last_name=author.family_name,
                                orcid=author.orcid.removeprefix("https://orcid.org/")
                                if author.orcid
                                else None,
                            )
                        )
                    )

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
            keywords=r.keywords,
            people=people,
            organizations=organizations,
        )

    def soft_delete(self, resource_uuid: str) -> requests.Response:
        """Delete (soft) an OER."""
        res = self.session.post(
            f"{self.base}/api/curation/resource-contents/{resource_uuid}/soft-delete/"
        )
        res.raise_for_status()
        return res

    def _delete_made_by_charlie(self) -> None:
        oers = self.get_resources()
        for oer in tqdm(oers, desc="deleting OERs"):
            if oer["created_by"]["username"] == "cthoyt":
                self.soft_delete(oer["uuid"])

    def upload_communities_from_path(self, path: str | Path) -> None:
        """Upload communities."""
        communities = read_communities(path)
        for community in communities:
            slug = _slugify_community(community.title)
            if community.uuid in self.uuid_to_community or slug in self.slug_to_community:
                continue
            try:
                database_id = self._create_community(community)
            except requests.exceptions.HTTPError:
                tqdm.write(f"failed on community: {slug}")
                continue
            else:
                tqdm.write(f"created: {slug} with DB ID: {database_id}")


def _write(s: str) -> None:
    if s not in LOGGED:
        tqdm.write(s)
        LOGGED.add(s)


LOGGED: set[str] = set()


def _explore() -> None:
    from dalia_dif.dif13.community import get_communities_dict

    directory = Path("/Users/cthoyt/dev/dalia-curation")
    communities = get_communities_dict(directory.joinpath("communities.csv"))

    client = Client()
    for path in sorted(directory.joinpath("curation").glob("*.csv")):
        tqdm.write(path.name)
        resources = dalia_dif.dif13.read_dif13(
            path, ignore_missing_description=True, communities=communities
        )
        for resource in resources:
            client._convert(resource, dry=True)


def _demo() -> None:
    directory = Path("/Users/cthoyt/dev/dalia-curation")
    path = directory.joinpath("curation", "KODAQS_curation.csv")
    # load example DIF13 data

    communities_path = directory.joinpath("communities.csv")
    communities = read_communities(communities_path)

    client = Client()
    client._delete_made_by_charlie()
    resources = dalia_dif.dif13.read_dif13(
        path, ignore_missing_description=True, communities=communities
    )
    for resource in resources:
        res = client.upload_dif13(resource, publish=True, communities=communities)
        res_json = res.json()
        click.echo(f"Resource UUID: {res_json['resource_uuid']}")
    # TODO the resource page https://search.dalia.education/admin/curation/resource/
    #  does not have it as published yet


def _explore_communities() -> None:
    client = Client()
    directory = Path("/Users/cthoyt/dev/dalia-curation")
    path = directory.joinpath("communities.csv")
    client.upload_communities_from_path(path)


if __name__ == "__main__":
    _demo()
