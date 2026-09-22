"""Compose group-owned task navigation without changing experiment evidence."""

from pathlib import Path

from . import core as c

DEFAULT_CATALOG = "presentation/task-explorer/catalog.json"


def collection(root, catalog, parents=()):
    path = c.inside(root, str(catalog))
    if path in parents:
        raise c.MedicalError("Task collection cycle: " + str(catalog))
    data = c.read(path)
    entries = list(data.get("entries", []))
    inventories = []
    if data.get("inventory"):
        for repo in c.read(c.inside(root, data["inventory"]))["repositories"]:
            inventories.append(
                {**repo, "require_brief_coverage": data.get("require_brief_coverage")}
            )
    families = dict(data.get("task_families", {}))
    contexts = dict(data.get("repository_contexts", {}))
    for child in data.get("collections", []):
        nested = collection(root, child, (*parents, path))
        entries.extend(nested["entries"])
        inventories.extend(nested["inventory"]["repositories"])
        for target, key in ((families, "task_families"), (contexts, "repository_contexts")):
            for name, value in nested[key].items():
                if name in target and target[name] != value:
                    raise c.MedicalError(f"Conflicting catalogue {key}: {name}")
                target[name] = value
    repo_ids = [repo["id"] for repo in inventories]
    if len(repo_ids) != len(set(repo_ids)):
        raise c.MedicalError("Duplicate inventory repository")
    return {
        **data,
        "entries": entries,
        "inventory": {"repositories": inventories},
        "task_families": families,
        "repository_contexts": contexts,
        "taxonomy": c.read(c.inside(root, data["taxonomy"])) if data.get("taxonomy") else {},
    }


def classify(root, data):
    """Validate navigation axes and resolve durable experiment IDs from records."""
    root = Path(root).resolve()
    taxonomy = data["taxonomy"]
    families = data["task_families"]
    family_axes = {}
    experiments = {}
    for path in sorted(root.glob("groups/*/experiments/*/experiment.toml")):
        row = c.read(path)
        if row["id"] in experiments:
            raise c.MedicalError("Duplicate experiment ID: " + row["id"])
        experiments[row["id"]] = {**row, "record_path": str(path.relative_to(root))}
    covered = set()
    for entry in data["entries"]:
        key = entry["id"]
        if taxonomy:
            for field, axis in (
                ("category", "categories"),
                ("role", "roles"),
                ("agent_work", "agent_work"),
            ):
                if entry.get(field) not in taxonomy[axis]:
                    raise c.MedicalError(f"{key}: unknown or missing {field}: {entry.get(field)}")
            operations = entry.get("operations", [])
            if len(operations) != len(set(operations)) or any(
                op not in taxonomy["categories"] or op == entry["category"] for op in operations
            ):
                raise c.MedicalError(f"{key}: invalid secondary operations")
            if entry["role"] != "task" and entry["agent_work"] != "none":
                raise c.MedicalError(f"{key}: supporting research must not imply an agent task")
            if entry["role"] == "task" and entry["agent_work"] == "none":
                raise c.MedicalError(f"{key}: task needs an agent-work description")
        family = entry.get("task_family")
        if family:
            if family not in families or not all(
                families[family].get(k) for k in ("title", "selector")
            ):
                raise c.MedicalError(f"{key}: unknown or incomplete task family: {family}")
            axes = (
                entry.get("repository_id", key),
                entry.get("category"),
                entry.get("role"),
                entry.get("agent_work"),
            )
            if family in family_axes and family_axes[family] != axes:
                raise c.MedicalError(
                    f"{key}: task family crosses repository or task axes: {family}"
                )
            family_axes[family] = axes
        seen = set()
        studies = []
        for link in entry.get("experiments", []):
            exp = experiments.get(link.get("id"))
            scope = link.get("scope")
            if not exp or not isinstance(scope, str) or not scope.strip() or link["id"] in seen:
                raise c.MedicalError(
                    f"{key}: unknown, duplicate or unscoped experiment link: {link}"
                )
            if exp["group_id"] != entry.get("owner_group"):
                raise c.MedicalError(f"{key}: experiment belongs to another research owner")
            seen.add(exp["id"])
            covered.add(exp["id"])
            protocol = c.inside(root, str(Path(exp["record_path"]).parent / exp["protocol"]))
            if not protocol.is_file():
                raise c.MedicalError(f"{key}: missing experiment protocol: {protocol}")
            studies.append(
                {
                    "id": exp["id"],
                    "title": exp["title"],
                    "scope": link["scope"],
                    "record_path": exp["record_path"],
                    "protocol": str(protocol.relative_to(root)),
                    "tasks": [task["id"] for task in exp.get("tasks", [])],
                }
            )
        entry["studies"] = studies
    if data.get("require_experiment_coverage"):
        missing = experiments.keys() - covered
        if missing:
            raise c.MedicalError(
                "Experiments missing task navigation: " + ", ".join(sorted(missing))
            )
    return len(covered)
