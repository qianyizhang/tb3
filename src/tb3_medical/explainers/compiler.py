"""Compose typed reader views around canonical plans; legacy stories retain their adapter."""

from pathlib import Path

from ..presentation_contracts import RestorationView, StoryPlan
from .families.restoration import compile_view


def compile_views(root: Path, plans: dict[str, StoryPlan]) -> dict[str, RestorationView]:
    if not plans:
        return {}
    return {
        key: view for key, plan in plans.items() if (view := compile_view(root, plan)) is not None
    }
