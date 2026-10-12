"""Compose typed reader views around canonical plans; legacy stories retain their adapter."""

from pathlib import Path

from ..presentation_contracts import ExplainerView, StoryPlan
from .families.restoration import compile_view as restoration_view
from .native_trace import compile_view as native_view


def compile_view(root: Path, plan: StoryPlan) -> ExplainerView | None:
    return (
        native_view(root, plan)
        if plan["recipe"] == "native-trace-v1"
        else restoration_view(root, plan)
    )


def compile_views(root: Path, plans: dict[str, StoryPlan]) -> dict[str, ExplainerView]:
    if not plans:
        return {}
    return {
        key: view for key, plan in plans.items() if (view := compile_view(root, plan)) is not None
    }
