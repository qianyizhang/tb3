"""Plot native reference volumes; all inputs and outputs are author-only."""

import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    b = Path(__file__).resolve().parents[4] / ".local/longitudinal-ct-case02"
    g = json.loads((b / "review/geometry.json").read_text())
    by = {v: {r["id"]: r for r in d["labels"]} for v, d in g["visits"].items()}
    ids = range(1, 16)
    y = np.arange(15)
    fig, ax = plt.subplots(figsize=(10, 7), layout="constrained")
    for v, offset, color, label in [
        ("baseline", -0.17, "#4e79a7", "Baseline"),
        ("followup", 0.17, "#e58c3c", "Follow-up"),
    ]:
        a = [by[v].get(i, {}).get("volume_ml", np.nan) for i in ids]
        ax.scatter(a, y + offset, color=color, label=label, s=46, zorder=3)
        for n, x in enumerate(a):
            if np.isfinite(x):
                ax.text(x * 1.07, n + offset, f"{x:.2f}", fontsize=8, va="center", color=color)
    ax.set_yticks(
        y, [f"{i}: {by['followup'][i]['anatomy']}" + (" (new)" if i >= 8 else "") for i in ids]
    )
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.1, 700)
    ax.set_xlabel("Reference volume, mL (logarithmic axis)")
    ax.grid(axis="x", alpha=0.2)
    ax.legend(loc="upper right")
    ax.set_title(
        "Second CT case: 7 persistent identities + 8 new lesions\nOne large lesion contains 84.6% / 94.9% of baseline / follow-up GT volume"
    )
    fig.text(
        0.5,
        -0.04,
        "Native mask-derived volumes. GT/private author view; no solver hints. Longitudinal-CT v3, FDAT, CC BY-NC 4.0.",
        ha="center",
        fontsize=8,
    )
    fig.savefig(b / "review/volume-profile.png", dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main()
