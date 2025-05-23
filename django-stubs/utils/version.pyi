from typing import TypeAlias

PYPY: bool

PY38: bool
PY39: bool
PY310: bool
PY311: bool
PY312: bool
PY313: bool
PY314: bool

_VT: TypeAlias = tuple[int, int, int, str, int]

def get_version(version: _VT | None = None) -> str: ...
def get_main_version(version: _VT | None = None) -> str: ...
def get_complete_version(version: _VT | None = None) -> _VT: ...
def get_docs_version(version: _VT | None = None) -> str: ...
def get_git_changeset() -> str | None: ...
def get_version_tuple(version: str) -> tuple[int, int, int]: ...
