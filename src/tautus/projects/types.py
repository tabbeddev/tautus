import typing


class ProjectMetadata(typing.TypedDict):
    title: str
    name: str
    namespace: str
    description: str
    maintainer: str
    mail: str
    license: str
    copyright_year: str
    version: str


class ProjectQRCConfig(typing.TypedDict):
    auto_generate: bool
    paths: list[str]


class ProjectExtended(typing.TypedDict):
    is_extended: bool
    qrc: ProjectQRCConfig
    include_python_libs: bool
    cleanup_python_libs: bool


class ProjectManifest(typing.TypedDict):
    tautus_version: str
    clickable_version: str
    metadata: ProjectMetadata
    tautus_extended: ProjectExtended
    requirements: list[str]
    dev_requirements: list[str]
    pre_build_commands: list[str]
    pre_release_build_commands: list[str]
