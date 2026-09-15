# Interview report

`index.html` is the complete, tracked publication: overview and four studies,
embedded images, identity/overlay controls, case walkthroughs and trace details.
It opens directly in a browser and works under a GitHub project-site prefix.
Written evidence links open the repository. No local `runs/` assets are fetched.

## Publish with GitHub Pages

1. In the repository, open **Settings → Pages → Build and deployment** and select
   **GitHub Actions** as the source.
2. Push `main`, or run **Publish interview report** from the Actions tab.
3. The workflow publishes only `site/index.html`. The expected URL is
   `https://qianyizhang.github.io/tb3/`.

The workflow uses GitHub's [custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
This checkout has not been pushed or deployed by the report cleanup.

## Edit and preview

Edit the authored HTML chapters in `content/`, then run:

```sh
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 -m http.server 8767 --bind 127.0.0.1
```

Open `http://127.0.0.1:8767/site/index.html`. Commit both the changed chapter and
rebuilt `index.html`. `provenance.json` records the original presentation/image
hashes used in the migration. Frozen evidence stays at its original paths.
The narrowly scoped large-file receipts in `configs/artifact-policy.json` must
be refreshed for changed presentation files before staging.

The public aneurysm chapter includes the retained three-plane overview images
and full authored case narratives. Its full-resolution volume viewer remains
local: the original arrays total roughly 650 MB and are not publication assets.
No source scans or segmentation masks were rewritten for this presentation.
