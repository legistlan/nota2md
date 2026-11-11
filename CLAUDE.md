# CLAUDE.md

This file guides Claude Code (claude.ai/code) in this repository. It says what the tree **is**, in
the present tense; a decision that outlives an issue is recorded here as a bullet.

## What this is

`nota2md` builds the Markdown of one legal provision of the *Diario Oficial de la Federación* (DOF),
Mexico's official gazette, identified by its `codNota`. `legal_provisions(codNota)` returns the
Suprema Corte de Justicia de la Nación's (SCJN) consolidated text of the whole law at that reform
when the `scjn-leyes` release covers the `codNota`, else the DOF's own HTML, image or PDF source
(`source="dof"` forces it); `reconstruct_legal_provisions` replays a law's current text from its
reform decrees; `nota2md.linking` matches an SCJN snapshot to the DOF `codNota` that produced it.
The DOF is the official source of legal text; the SCJN is not, and `fuente: scjn` in a provenance
header means exactly that.

It is one package of the Legistlan project (the `legistlan` organization), the one a caller reaches
for first: it requires `scjn>=0.5.1` and `dofjson>=0.5.0` from PyPI and re-exports their entry
points; nothing in either imports back from it. `document2md` is its optional `ocr` extra
(`document2md>=0.3.0`), imported lazily, for notes predating the HTML era (pre-1999). It was
`packages/nota2md` of a monorepo until 11 November 2026 (monorepo commit `f403872b1`); this
repository is that history filtered to the package, its three scripts, its documentation page and
the notes of its one release, so `git log` and `git blame` reach the first commit. A `#N` in a
commit message, a comment or a docstring is an issue of the monorepo, where those issues live.

## The package

- **Read order**, the way a note's Markdown gets built: `nota2md.builder` (the entry points
  `legal_provisions` and `get_document`, the dispatcher between the SCJN corpus and the DOF, the
  cut of a note out of its OCR'd page), `nota2md.linking` (the `codNota` seam), `nota2md.leyes`
  (`reconstruct_legal_provisions`), `nota2md.cache`, `nota2md.html_converter` (the one
  note-to-Markdown step), `nota2md.text`, `nota2md.cli` (`nota2md <codNota>`, `nota2md download`).
- **The nine entry points**, all in `__all__`: `legal_provisions`, `reconstruct_legal_provisions`,
  `get_document`; `fetch_daily_legal_provisions` and `legal_provisions_titles`, re-exported from
  `dofjson`; `download_scjn_leyes_corpus`, `download_scjn_leyes_index`,
  `download_scjn_leyes_catalog` and `iter_current_federal_laws`, re-exported from `scjn`. The
  re-exports exist so a caller does not need to know which package defines a name; the readers
  are `scjn`'s.
- **The dispatcher.** `legal_provisions` consults the reverse index
  (`download_scjn_leyes_index`) on every `source="auto"` call. A covered `codNota` is answered from
  the snapshot, with the outline markers taken out (`markdown_de_snapshot(..., outline=False)`,
  `scjn.outline.strip_markers`), written as `{slug}-{fecha}.md` with the corpus' `fuente: scjn`
  header intact; a DOF answer is written as `nota-{codNota}.md`, so the file alone says where it
  came from. A decree that reformed several laws raises `ValueError` listing the candidates
  (`instrumento=` says which). An uncovered `codNota`, an asset not on disk or a network failure
  reading the release fall back to the DOF, the last two with `warnings.warn`.
- **The DOF paths.** HTML (`beautifulsoup4` over `cadenaContenido`, standalone and the default DOF
  source) works for every note with digital text, including the days SIDOF lost, which `dofjson`
  recovers from `www.dof.gob.mx`; image and PDF OCR through `document2md` for the rest, with the
  note cut out of its page by fuzzy title matching against the day's index (`--min-confidence`,
  `--notas`). `--source image`/`pdf` on a note SIDOF does not have raises rather than fetching the
  wrong pages.
- **Linking** (`nota2md.linking`) is the one SCJN-adjacent concern kept here: a `codNota` is a DOF
  concept, and `scjn` imports no sibling. Title candidates first, the content-diff confirmation
  second; a `codNota` another snapshot already claimed is never taken; an `ambiguous` date is
  reported for a human. An absent link is worth more than a wrong one (monorepo issue #115).
- **Reconstruction** (`nota2md.leyes`) reads nothing from the SCJN. `source="html"` is its default,
  not `"auto"`: the article merge was validated on HTML-derived Markdown only. `nombre_ley` scopes
  a shared decree to one law.
- "Reform N" of a law is the SCJN reform table's chronological order; a law's reform history *is*
  the `scjn-leyes` release (`download_scjn_leyes_corpus`, oldest first). No source other than the
  SCJN and the DOF/SIDOF: the Cámara de Diputados (LeyesBiblio) is not a source.

## Data: the releases it reads and the caches

- **Data is never committed.** `nota2md` publishes no dataset of its own. It reads `scjn-leyes`
  (owner `legistlan/scjn`) and `notas-archivo` (owner `legistlan/dofjson`); `nota2md download`
  fetches those two plus `scjn-reglamentos`, `scjn-lineamientos` and `scjn-tratados`
  (`federal-laws`, `federal-regulations`, `federal-guidelines`, `international-treaties`,
  `gazette-metadata`, `all`), each into the cache of the package that owns it. Pointing a package
  at a mirror of its releases is that package's variable (`SCJN_RELEASE_REPOSITORY`,
  `DOFJSON_RELEASE_REPOSITORY`); `nota2md` has none, since it fetches nothing itself.
- **`historial-legislativo`** is this repository's one release, a frozen record whose notes are
  `.github/historial-legislativo.md`; nothing here can regenerate its assets and no workflow
  publishes them. `.github/migracion-diputados.md` is the audit that retired its source.
- **Three caches, none shared.** `nota2md.cache.CACHE_DIR` (`$NOTA2MD_CACHE_DIR`; platformdirs,
  `~/.cache/nota2md` on Linux) holds only what `nota2md` derives: `scjn-leyes/md/` (the one
  snapshot a caller asked for, extracted from `scjn`'s tarball, a cache proper keyed by file name
  and never revalidated: `refrescar=True` or a deleted file re-extracts it) and `dof/` (rebuilt on
  every call, no freshness). The release assets live in `scjn.cache.CACHE_DIR` and
  `dofjson.titulos.CACHE_DIR`. Every `scjn` reader is disk-first and raises `AssetNotCached` rather
  than downloading; `legal_provisions_titles` populates `dofjson`'s cache on first use.
- **The fixtures** `tests/fixtures/leyes/` (about 3 MB) are the one exception to "data is never
  committed": the SCJN's consolidated text of 42 laws at their newest reform, the ground truth
  `tests/test_leyes_44.py` compares a reconstruction against, regenerated only by
  `scripts/regenera_fixtures_leyes.py --escribe`.

## The scripts

`scripts/` holds the three scripts whose output or input is this package's own. They import
`nota2md` from the repository root and `scjn`/`dofjson` from PyPI; what they write goes under the
gitignored `scripts/scjn/` or `--outdir`. A human runs every publish step.

- `enlaza_scjn_legislacion.py` is step 4 of `scjn`'s crawl process (that repository's
  `fetch_scjn_legislacion.py` crawls, its packaging scripts build the release): it links every
  snapshot of a crawled law to its `codNota` and writes `indice.json` per law, saving the DOF
  notes it considered beside it. `--instrumento` narrows the run; it needs the `notas-archivo`
  cache (`nota2md download gazette-metadata`).
- `fetch_federal_law_metadata.py` records `materia`, `vigencia` and `resumen` per law from the
  SCJN's search, matched by `idOrdenamiento` so a wrong document is never described as the right
  one, into the crawl's `estado.json` files and the published `indice-global.json.gz`. The
  `gh release upload` line it prints names `scjn.release.release_repository()`.
- `regenera_fixtures_leyes.py` rewrites the fixtures above; a law whose history has a hole is
  excluded and reported.

## Documentation

One GitHub Pages site, `https://legistlan.github.io/nota2md/`, built and deployed by
`.github/workflows/website.yml` (the official Pages artifact flow, Pages source "GitHub Actions",
no `gh-pages` branch; pull requests only build, a push to `main` deploys). It has two halves with
no overlapping page:

- `docs/source/index.rst`, published under `/dev/`, is the **developer reference**: every name in
  `__all__` and every CLI subcommand gets a verified example, a live doctest run by the `docs` job
  of `test.yml` against SIDOF, the cached `lfca` law and the `notas-archivo` release; private
  helpers (leading underscore) get a full docstring and appear through `:private-members:` but
  need no example. The HTML build is strict (`-n -W`); a name defined in `dofjson`, `scjn` or
  `document2md` is cross-referenced through intersphinx to that package's own `/dev/` site, so a
  role names the defining module (`~scjn.release.download_scjn_leyes_corpus`,
  `~dofjson.titulos.legal_provisions_titles`), never the re-export. The strict build and the
  doctest stay in `test.yml`'s `docs` job as the pull request gate; `website.yml` builds HTML only
  and never touches the network.
- `website/` is the Quarto **user site** at the root, in English, written from the README and these
  notes: install, command line, Python, sources, linking, reconstruction, releases, scripts.
  `execute.enabled: false` (every example needs the cache or the network), no API reference; its
  code blocks are illustrative and the developer reference holds the verified ones.
  `tests/test_docs.py` keeps `website/pages/cli.qmd` naming every CLI option and subcommand and
  every `nota2md/*.py` module documented by exactly one `automodule` (`nota2md.text` is the one
  named exception, until it has a section).

Nothing in the tree names the former organization or the monorepo this package was extracted from:
provenance is said without naming ("the monorepo this package was extracted from"), links point at
`legistlan`, and `tests/test_docs.py` (`TestNoFormerOwnerNames`) fails on either name, in any letter
case, in any tracked file. A `#N` issue reference stays: it names nothing.

## Commands

```bash
pip install -e ".[test]"                                                  # ".[test,ocr]" also runs the four document2md tests
pytest tests --ignore=tests/test_leyes_44.py
pytest tests/test_leyes_44.py                                             # network: 42 laws replayed from SIDOF
scjn download --slug lfca                                                 # what the doctests read
python -m sphinx -n -W --keep-going -b html docs/source docs/build/html   # the strict build
quarto render website                                                     # the user site, into website/_site
python -m sphinx -b doctest docs/source docs/build/doctest                # the examples, network included
python scripts/check_package_versions.py                                  # one step ahead of PyPI
```

The `ocr` extra does not resolve on an Intel Mac (`onnxruntime` has no macOS x86_64 wheel past
1.23.2); the four tests of `test_builder.py` that patch `document2md.converter.*` skip themselves
there.

## Releases to PyPI

- The version is dynamic (`nota2md.__version__`) and at most one step ahead of PyPI (the next
  patch, or the next minor with patch 0): `check-package-versions` in `test.yml` is the gate.
- A tag `vX.Y.Z` on `main` runs `publish-pypi.yml`, which refuses a tag that does not match
  `__version__`, builds, checks and uploads with the organization's `TWINE` secret.
- Publish order across repositories: `scjn` and `dofjson` before the `nota2md` release that raises
  their floor, and `document2md` before any `nota2md` whose `ocr` extra requires it. A published
  package never carries a URL dependency.
- `[tool.uv] cache-keys` in `pyproject.toml` lists `nota2md/__init__.py` (with `pyproject.toml` and
  `setup.py`, which replacing uv's default list drops) so uv rebuilds the editable install when
  `__version__` changes. Development-only: nothing in the wheel or a release changes;
  `tests/test_packaging.py` pins it.

## Git workflow: branches, issues and PRs

- A branch is created to work on one particular issue, only at the moment, while on `main`, an
  issue is read and about to be implemented.
- A secondary issue that turns out necessary is done on the working branch; no new branch.
- A pull request is opened only when the user explicitly asks for it, after the main issue and
  every secondary one are done. `main` takes changes only through a pull request (ruleset).

## Language policy

- The implementation is in English: identifiers, comments, docstrings, commit messages and new
  documentation, whatever language the instructions were given in.
- The codebase still mixes Spanish identifiers (`_fusiona_articulo`, `resuelve_cache_dir`, the
  Spanish CLI help of the scripts, `historial-legislativo.md` and `migracion-diputados.md`, which
  are frozen records). Leave existing Spanish as it is when touching unrelated lines, no drive-by
  renames; new code, and code rewritten anyway, is English.
- Domain terms that are proper nouns or established Mexican legal vocabulary (`DOF`, `codNota`,
  `SIDOF`, `SCJN`, `abrev`, law abbreviations like `cpeum`/`lft`) are names, not translated.

## Working conventions

- Naming favours precision over brevity: `codNota`, `legal_provisions`,
  `download_scjn_leyes_corpus` are the domain's vocabulary (a DOF "nota" is a legal provision).
- Comments record the incident or the numeric check that justified a design choice (why
  treaty-name matching is rarity-weighted, why a version floor is pinned, why the merge defaults to
  HTML); read them before "simplifying" the code they are attached to.
- The HTML path works standalone and is the default DOF source; the OCR paths depend on
  `document2md` and `mineru`, which are heavy, so `document2md` stays an optional extra imported
  lazily.
- A behaviour that moves a document's output is proved, not argued: by `tests/test_leyes_44.py`
  over the 42 fixture laws for the reconstruction, and by the linking's status counts for a change
  in `nota2md.linking`.
