"""Types shared by workbench services.

Records and external JSON/TOML documents have extensible, kind-specific fields.
Their payloads are dynamic at the serialization boundary; service arguments,
collections, paths and return shapes are annotated separately. Runtime validators
remain responsible for schema versions, required fields and scientific meaning.
"""

from os import PathLike
from typing import Any

type Pathish = str | PathLike[str]
type Document = dict[str, Any]
type Records = dict[str, Document]
