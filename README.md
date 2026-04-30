<div align="center">

# 🧹 imgclean

**Find duplicates, blur, corruption, leakage, and quality issues in image datasets before they ship.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/Weiykong/imgclean/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Weiykong/imgclean/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/badge/pypi-imgclean-orange?logo=pypi&logoColor=white)](https://pypi.org/project/imgclean/)
[![Tests](https://img.shields.io/badge/tests-50%20cases-brightgreen)](#-test-suite)

</div>

---

Most image datasets have hidden problems. imgclean makes them obvious in one pass, with a CLI that is fast to try and reports that are easy to review with a team.

```text
$ imgclean scan ./dataset --workers 8 --report-dir ./reports
                      Scan Summary
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric              ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total files         │ 12438 │
│ Scanned OK          │ 12397 │
│ Corrupted           │    41 │
│ Total findings      │  1525 │
│   ↳ near duplicate  │  1083 │
│   ↳ exact duplicate │   214 │
└─────────────────────┴───────┘
```

<p align="center">
  <img src="assets/imgclean-social-card.svg" alt="imgclean scans an image dataset and reports duplicates, corruption, leakage, and quality issues" width="920" />
</p>

## Highlights

- One command to scan a dataset and export HTML, JSON, and CSV reports.
- Built-in checks for corruption, blur, exposure, resolution, aspect ratio, duplicates, and split leakage.
- Parallel scan path with `--workers` and config-based `parallel.max_workers`.
- Works as both a CLI tool and a Python API for pipelines and notebooks.
- Safe cleanup workflow with `clean`, `quarantine`, and representative-keep actions.
- Test-backed core with 50 automated test cases and GitHub Actions CI.

## Try it in 60 seconds

```bash
pip install imgclean
imgclean clean ./dataset --workers 8 --report-dir ./reports
```

The command writes a shareable HTML report plus machine-readable JSON and CSV outputs in `./reports`, then previews the quarantine plan without moving anything unless you add `--execute`.

---

## Contents

- [Why imgclean](#-why-imgclean)
- [Highlights](#highlights)
- [Try it in 60 seconds](#try-it-in-60-seconds)
- [Compared with other workflows](#-compared-with-other-workflows)
- [Installation](#-installation)
- [Quick start](#-quick-start)
- [CLI reference](#-cli-reference)
- [Python API](#-python-api)
- [Configuration](#-configuration)
- [Checks](#-checks)
- [Outputs](#-outputs)
- [Architecture](#-architecture)
- [Optional: embeddings](#-optional-embedding-based-features)
- [Test suite](#-test-suite)
- [Contributing](#contributing)
- [Roadmap](#-roadmap)

---

## 🤔 Why imgclean

| Problem | What goes wrong |
|---|---|
| Exact duplicates in training data | Model memorises samples, inflated accuracy |
| Near-duplicates crossing train/val | Evaluation metrics are meaningless |
| Blurry or tiny images | Wasted annotation budget, noisy gradients |
| Corrupted files | Silent crashes in your data loader at 3 AM |
| Overexposed / underexposed frames | Class imbalance in lighting conditions |
| Mislabeled split assignments | You think your model generalises; it does not |

imgclean makes these problems **visible** in seconds and gives you tools to **fix** them.

---

## 🥊 Compared with other workflows

| Workflow | Duplicate + leakage checks | Cleanup actions | Shareable reports | Best fit |
|---|---|---|---|---|
| `imgclean` | ✅ built in | ✅ `clean` / `quarantine` | ✅ HTML + JSON + CSV | Pre-training dataset QA |
| `cleanvision` | ✅ focused on image issues | ❌ review-only | ⚠️ notebook/report oriented | Exploratory dataset analysis |
| `FiftyOne` | ⚠️ possible with app workflows | ⚠️ manual curation flows | ✅ interactive app views | Large visual review workflows |
| Manual scripts | ⚠️ custom only | ⚠️ custom only | ❌ usually none | One-off internal jobs |

---

## 📦 Installation

```bash
pip install imgclean
```

**Optional — CLIP-based near-duplicate detection and outlier analysis:**

```bash
pip install "imgclean[embeddings]"   # torch + open_clip + faiss-cpu
```

**Development install:**

```bash
git clone https://github.com/Weiykong/imgclean.git
cd imgclean
python3 -m pip install --user uv
make install
make test
```

**Supported formats:** JPEG · PNG · BMP · GIF · TIFF · WebP

---

## 🚀 Quick start

### CLI

```bash
# Full audit — produces HTML, JSON, and CSV reports
imgclean scan ./dataset --workers 8 --report-dir ./reports --open

# Duplicates only, strict threshold
imgclean dedup ./dataset --threshold 4 --workers 8

# Check train/val/test splits for data leakage
imgclean leakage ./train ./val ./test

# Quality checks (blur, exposure, resolution)
imgclean quality ./dataset --workers 8

# Scan and preview a cleanup plan in one step
imgclean clean ./dataset --issues corrupted,blurry --report-dir ./reports

# Preview what would be quarantined, then do it
imgclean quarantine ./dataset --issues corrupted,blurry
imgclean quarantine ./dataset --issues corrupted,blurry --execute
```

### Python API

```python
from imgclean import scan_dataset

report = scan_dataset("./dataset")
print(f"{report.summary.findings_count} issues found in {report.summary.duration_seconds:.1f}s")

# Specific checks only
report = scan_dataset(
    "./dataset",
    checks=["blur", "corruption", "duplicates"],
    thresholds={"blur_laplacian_min": 80.0, "min_width": 128},
)

# Split-aware scan (enables leakage detection)
report = scan_dataset(
    "./dataset",
    splits={"train": "./train", "val": "./val", "test": "./test"},
)

# Iterate findings
for f in report.findings:
    print(f"[{f.severity.value}] {f.issue_type.value}: {f.file_path.name}")
```

---

## 🖥️ CLI reference

### `imgclean scan` — full dataset audit

```bash
imgclean scan <path> [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--config, -c` | — | YAML or JSON config file |
| `--report-dir, -o` | `.` | Output directory for reports |
| `--no-html` | false | Skip HTML report |
| `--no-json` | false | Skip JSON report |
| `--no-csv` | false | Skip CSV report |
| `--open` | false | Open HTML in browser after scan |
| `--no-cache` | false | Disable feature cache |
| `--workers, -w` | auto | Max worker threads for image scanning |
| `--verbose, -v` | false | Debug logging |

```bash
imgclean scan ./dataset --workers 8 --report-dir ./audit --open --config imgclean.yaml
```

---

### `imgclean dedup` — duplicate detection

```bash
imgclean dedup <path> [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--method, -m` | `phash` | Duplicate method: `phash` for visual matches, `sha256` for byte-identical files |
| `--threshold, -t` | `8` | Max pHash Hamming distance for visual near-duplicates |
| `--report-dir, -o` | `.` | Output directory |
| `--workers, -w` | auto | Max worker threads for image scanning |

```bash
imgclean dedup ./dataset --threshold 6 --workers 8
imgclean dedup ./dataset --method sha256   # exact byte duplicates only
```

---

### `imgclean leakage` — split contamination check

```bash
imgclean leakage <train> [val] [test] [OPTIONS]
```

Detects images (exact or perceptually similar) that appear in more than one split.

```bash
imgclean leakage ./train ./val ./test --report-dir ./leakage_report
```

---

### `imgclean quality` — quality checks only

```bash
imgclean quality <path> [OPTIONS]
```

| Option | Description |
|---|---|
| `--blur/--no-blur` | Check for blur (default on) |
| `--exposure/--no-exposure` | Check over/underexposure (default on) |
| `--resolution/--no-resolution` | Check resolution (default on) |
| `--workers, -w` | Max worker threads for image scanning |

```bash
imgclean quality ./dataset --workers 8 --no-exposure
```

---

### `imgclean clean` — scan then quarantine

```bash
imgclean clean <path> [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--issues, -i` | all errors | Comma-separated issue types to quarantine |
| `--out, -o` | `./quarantine` | Destination folder |
| `--execute` | false | Actually move files (default is dry-run) |
| `--report-dir` | `.` | Output directory for HTML, JSON, and CSV reports |
| `--workers, -w` | auto | Max worker threads for image scanning |

```bash
# Preview cleanup + write reports
imgclean clean ./dataset --issues corrupted,blurry --workers 8 --report-dir ./reports

# Then execute
imgclean clean ./dataset --issues corrupted --out ./review --execute
```

---

### `imgclean quarantine` — move flagged files

```bash
imgclean quarantine <path> [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--issues, -i` | all errors | Comma-separated issue types |
| `--out, -o` | `./quarantine` | Destination folder |
| `--execute` | false | Actually move files (default is dry-run) |

```bash
# Preview first
imgclean quarantine ./dataset --issues corrupted,blurry

# Then execute
imgclean quarantine ./dataset --issues corrupted,blurry --out ./review --execute
```

**Valid issue types:** `corrupted` · `low_resolution` · `aspect_ratio` · `blurry` · `underexposed` · `overexposed` · `exact_duplicate` · `near_duplicate` · `embedding_duplicate` · `split_leakage` · `outlier`

---

### `imgclean report` — re-render HTML from JSON

```bash
imgclean report imgclean_report.json --open
imgclean report results.json --html report_v2.html
```

---

## 🐍 Python API

### `scan_dataset()`

```python
from imgclean import scan_dataset

report = scan_dataset(
    path,                  # str | Path  — dataset root
    config_file=None,      # str | Path  — YAML/JSON config
    checks=None,           # list[str]   — checks to run (None = all enabled)
    thresholds=None,       # dict        — threshold overrides
    splits=None,           # dict[str, Path] — split directories
    cache=True,            # bool        — disk feature cache
    verbose=False,         # bool        — debug logging
)
```

### Working with results

```python
# Summary
s = report.summary
print(s.total_files, s.findings_count, s.issue_counts)

# All findings
for f in report.findings:
    print(f.issue_type.value, f.severity.value, f.file_path, f.score)

# Grouped by type
by_type = report.findings_by_type()
blurry  = by_type.get("blurry", [])
dupes   = by_type.get("exact_duplicate", [])

# Duplicate clusters
groups = {}
for f in dupes:
    groups.setdefault(f.group_id, []).append(f.file_path)
```

### Post-scan actions

```python
from imgclean.actions import quarantine_findings, get_removal_candidates
from imgclean.reports import write_html, write_json
from pathlib import Path

# Write reports manually (API does not write files by default)
write_json(report, Path("report.json"))
write_html(report, Path("report.html"), open_browser=True)

# Quarantine problematic files (dry_run=True by default)
quarantine_findings(
    findings=report.findings,
    quarantine_dir=Path("./quarantine"),
    issue_filter=["corrupted", "blurry"],
    root=Path("./dataset"),
    dry_run=False,   # set True to preview
)

# Files to remove to deduplicate (keeps one representative per cluster)
to_remove = get_removal_candidates(report.findings)
```

### `Finding` fields

| Field | Type | Description |
|---|---|---|
| `issue_type` | `IssueType` | Enum: `corrupted`, `blurry`, `exact_duplicate`, … |
| `severity` | `Severity` | `error` · `warning` · `info` |
| `file_path` | `Path` | Absolute path to the affected file |
| `message` | `str` | Human-readable explanation |
| `score` | `float \| None` | Measured value (e.g. Laplacian variance, Hamming distance) |
| `threshold` | `float \| None` | Threshold that triggered the finding |
| `related_files` | `list[Path]` | Duplicate partners, leakage matches |
| `group_id` | `str \| None` | Cluster ID for grouped issues |
| `metadata` | `dict` | Extra context (brightness, width/height, …) |

---

## ⚙️ Configuration

```bash
imgclean scan ./dataset --config imgclean.yaml
```

<details>
<summary><strong>Full annotated imgclean.yaml</strong></summary>

```yaml
dataset:
  path: ./dataset
  recursive: true

checks:
  corruption: true
  resolution: true
  aspect_ratio: true
  blur: true
  exposure: true
  exact_duplicates: true
  perceptual_duplicates: true
  embedding_duplicates: false   # requires imgclean[embeddings]
  split_leakage: true
  outliers: false               # requires imgclean[embeddings]

thresholds:
  # Resolution
  min_width: 256
  min_height: 256

  # Aspect ratio  (width / height)
  aspect_ratio_min: 0.1         # flag very tall images
  aspect_ratio_max: 10.0        # flag very wide images

  # Blur  (Laplacian variance — higher = sharper)
  blur_laplacian_min: 60.0

  # Exposure  (mean pixel brightness 0–255)
  exposure_dark_max: 25.0
  exposure_bright_min: 230.0

  # Perceptual duplicates  (pHash Hamming distance)
  phash_hamming_max: 8

  # Embedding duplicates  (cosine similarity 0–1)
  embedding_similarity_min: 0.95

  # Outliers  (kNN on embedding space)
  outlier_knn_k: 5
  outlier_distance_percentile: 95.0

report:
  html: true
  json_report: true
  csv_report: true
  output_dir: ./reports
  open_browser: false

actions:
  quarantine: false
  quarantine_dir: ./quarantine
  dry_run: true          # always preview before executing

cache:
  enabled: true
  dir_name: .imgclean_cache

parallel:
  max_workers: null       # null = ThreadPoolExecutor default
```

</details>

**Merge priority (highest wins):** CLI flags → config file → built-in defaults

---

## 🔍 Checks

### File integrity

| Check | Issue | Severity | How |
|---|---|---|---|
| `corruption` | `corrupted` | 🔴 error | PIL two-pass: `verify()` (header/checksum) + `load()` (pixel decode) |

### Quality

| Check | Issue | Severity | How |
|---|---|---|---|
| `blur` | `blurry` | 🟡 warning | Variance of the Laplacian — low variance = uniform = blurry |
| `exposure` | `underexposed` | 🟡 warning | Mean brightness < `exposure_dark_max` (default 25) |
| `exposure` | `overexposed` | 🟡 warning | Mean brightness > `exposure_bright_min` (default 230) |
| `resolution` | `low_resolution` | 🟡 warning | Width or height below `min_width` / `min_height` |
| `aspect_ratio` | `aspect_ratio` | 🟡 warning | Ratio outside `[aspect_ratio_min, aspect_ratio_max]` |

### Duplicates

| Check | Issue | Severity | How |
|---|---|---|---|
| `exact_duplicates` | `exact_duplicate` | 🟡 warning | SHA-256 hash grouping |
| `perceptual_duplicates` | `near_duplicate` | 🟡 warning | pHash + Hamming distance ≤ threshold; union-find clustering |
| `embedding_duplicates` ✨ | `embedding_duplicate` | 🟡 warning | CLIP cosine similarity ≥ threshold |

### Split integrity

| Check | Issue | Severity | How |
|---|---|---|---|
| `split_leakage` (exact) | `split_leakage` | 🔴 error | Same SHA-256 across splits |
| `split_leakage` (perceptual) | `split_leakage` | 🟡 warning | pHash Hamming distance ≤ threshold across splits |

### Outliers

| Check | Issue | Severity | How |
|---|---|---|---|
| `outliers` ✨ | `outlier` | 🔵 info | Mean kNN cosine distance above the Nth percentile |

> ✨ Requires `pip install "imgclean[embeddings]"`

---

## 📄 Outputs

### HTML report

A self-contained HTML file (no external dependencies):

- **Summary cards** — total files, scanned OK, corrupted, findings by type
- **Per-issue tables** — file path · severity · score · threshold · message
- **Cluster view** — duplicate and leakage groups, representative highlighted

### JSON report

```jsonc
{
  "summary": {
    "total_files": 1000,
    "scanned_files": 997,
    "corrupted_files": 3,
    "findings_count": 142,
    "issue_counts": { "blurry": 31, "exact_duplicate": 44, "corrupted": 3 },
    "duration_seconds": 4.2
  },
  "findings": [
    {
      "issue_type": "blurry",
      "severity": "warning",
      "file_path": "dataset/train/img_042.jpg",
      "score": 12.3,
      "threshold": 60.0,
      "message": "Image appears blurry (Laplacian variance 12.3 < threshold 60.0)."
    }
  ]
}
```

### CSV report

One row per finding — ready for spreadsheet review or programmatic filtering:

```
issue_type,severity,file_path,score,threshold,group_id,related_files,message
blurry,warning,train/img_042.jpg,12.3,60.0,,,Image appears blurry...
exact_duplicate,warning,train/cat_001.jpg,,,a3b1c9,val/cat_001.jpg,Exact duplicate...
```

---

## 🏗️ Architecture

imgclean follows a strict layered design — each layer has a single responsibility and only depends on layers below it.

```
┌─────────────────────────────────────────────────────────────┐
│  cli/        Command-line interface (Typer + Rich)          │
│  api/        Public Python API  scan_dataset()              │
├─────────────────────────────────────────────────────────────┤
│  core/       Orchestration: scanner · pipeline · registry   │
├────────────────────────┬────────────────────────────────────┤
│  reports/              │  actions/                          │
│  HTML · JSON · CSV     │  quarantine · move · dedup         │
├─────────────────────────────────────────────────────────────┤
│  checks/     10 independent checks (BaseCheck subclasses)   │
├─────────────────────────────────────────────────────────────┤
│  features/   Laplacian · brightness · pHash · CLIP embeds   │
│  io/         filesystem · image loader · hashing · cache    │
├─────────────────────────────────────────────────────────────┤
│  models/     ImageRecord · Finding · Dataset · ScanReport   │
│  config/     Pydantic schema · YAML/JSON loader             │
│  utils/      logging · timing · parallel_map · thresholds   │
└─────────────────────────────────────────────────────────────┘
```

<details>
<summary><strong>Layer-by-layer breakdown</strong></summary>

### `models/` — pure data structures

| File | Class | Description |
|---|---|---|
| `image_record.py` | `ImageRecord` | One image: path, size, format, sha256, phash, corruption flag |
| `finding.py` | `Finding` | One issue: type, severity, score, threshold, related files, cluster id |
| `issue_types.py` | `IssueType`, `Severity` | Enums for all issue and severity types |
| `dataset.py` | `Dataset` | List of `ImageRecord`s with helpers (`valid()`, `by_split()`, `corrupted()`) |
| `report.py` | `ReportSummary`, `ScanReport` | Aggregated results: summary stats + all findings |
| `actions.py` | `ActionType`, `ActionPlan` | Describes a planned file operation |

---

### `config/` — typed configuration

| File | Purpose |
|---|---|
| `defaults.py` | Module-level constants for every threshold and setting |
| `schema.py` | Pydantic v2 models with validation (`Config`, `ChecksConfig`, `ThresholdsConfig`, …) |
| `loader.py` | `load_config(path, overrides)` — loads YAML/JSON and deep-merges CLI overrides |

---

### `io/` — all file access

| File | Key function(s) |
|---|---|
| `filesystem.py` | `discover_images(root, recursive)` — glob with extension filtering |
| `image_loader.py` | `load_image(path)` → `LoadResult` — **two-pass**: `verify()` then `load()` |
| `hashing.py` | `sha256(path)`, `phash(image)`, `dhash(image)`, `hamming_distance(h1, h2)` |
| `cache.py` | `FeatureCache` — JSON disk cache keyed by file path, invalidated on mtime change |

> **Why two-pass image loading?** PIL's `verify()` must be called *before* `load()` and checks headers/checksums. `load()` forces full pixel decoding and catches truncated files. They must run in separate `with Image.open()` blocks.

---

### `features/` — shared computation

| File | Functions | What |
|---|---|---|
| `quality.py` | `laplacian_variance(img)` | Blur score via OpenCV Laplacian |
| `quality.py` | `mean_brightness(img)` | Mean pixel intensity (greyscale, 0–255) |
| `perceptual.py` | `compute_phash(img)`, `compute_dhash(img)` | Perceptual hashes via `imagehash` |
| `metadata.py` | `file_metadata(path)`, `exif_metadata(img)` | File size, mtime, EXIF tags |
| `embeddings.py` | `embed_image(img)`, `cosine_similarity(a, b)` | CLIP embeddings (lazy-loaded, optional) |

---

### `checks/` — analysis logic

Every check inherits `BaseCheck` and implements one method:

```python
class BaseCheck(ABC):
    name: str           # used in config keys and reports
    description: str

    def run(self, dataset: Dataset) -> list[Finding]: ...
    def is_enabled(self) -> bool: ...   # reads config.checks.<name>
```

Checks are **stateless**, **independent**, and **testable in isolation**. They never read from disk — the scanner pre-populates all fields on `ImageRecord`.

| Class | `name` | Notes |
|---|---|---|
| `CorruptionCheck` | `corruption` | Reads `record.is_corrupted` set by scanner |
| `ResolutionCheck` | `resolution` | Compares `record.width/height` to thresholds |
| `AspectRatioCheck` | `aspect_ratio` | Uses `record.aspect_ratio` property |
| `BlurCheck` | `blur` | Re-loads image, calls `laplacian_variance()` |
| `ExposureCheck` | `exposure` | Re-loads image, calls `mean_brightness()` |
| `ExactDuplicatesCheck` | `exact_duplicates` | Groups by `record.sha256` |
| `PerceptualDuplicatesCheck` | `perceptual_duplicates` | Union-find on pHash Hamming distances |
| `EmbeddingDuplicatesCheck` | `embedding_duplicates` | CLIP cosine similarity (optional) |
| `SplitLeakageCheck` | `split_leakage` | SHA-256 and pHash cross-split comparison |
| `OutliersCheck` | `outliers` | kNN distance on CLIP embedding matrix (optional) |

---

### `core/` — orchestration

| File | Key function | What |
|---|---|---|
| `registry.py` | `build_checks(config)` | Instantiate enabled checks in execution order |
| `scanner.py` | `scan_directory()`, `scan_splits()` | Build `Dataset` from disk, populate `ImageRecord`s |
| `pipeline.py` | `run_pipeline(checks, dataset)` | Run each check, collect findings, log timing |
| `orchestrator.py` | `run_scan(paths, config, split_map)` | Top-level entry point |

**Execution order** (cheap per-file checks first, expensive group checks last):

```
Corruption → Resolution → AspectRatio → Blur → Exposure
→ ExactDuplicates → PerceptualDuplicates → EmbeddingDuplicates
→ SplitLeakage → Outliers
```

---

### `reports/` — output generation

| File | Output |
|---|---|
| `html.py` | Self-contained HTML via Jinja2 (`templates/report.html.j2`) |
| `json.py` | Full JSON (summary + all findings as dicts) |
| `csv.py` | One row per finding; `related_files` joined with `\|` |

---

### `actions/` — file operations

All functions accept `dry_run=True` so you can always preview before committing.

| File | Function | What |
|---|---|---|
| `quarantine.py` | `quarantine_findings(...)` | Move flagged files to a review folder |
| `move.py` | `move_files(paths, dest, root, dry_run)` | Move, preserving relative structure |
| `copy.py` | `copy_files(paths, dest, root, dry_run)` | Copy to destination |
| `keep_representative.py` | `select_representatives(findings)` | Pick one file per duplicate cluster |
| `keep_representative.py` | `get_removal_candidates(findings)` | Flat list of non-representative files |

</details>

---

## Data flow

```
images/
  ↓  filesystem.py       discover paths
  ↓  scanner.py          build ImageRecords (load · hash · cache)
  ↓
Dataset[ImageRecord]
  ↓  registry.py         build enabled checks
  ↓  pipeline.py         run each check in order
  ↓
list[Finding]
  ↓  orchestrator.py     build ScanReport + ReportSummary
  ↓
reports/   →  HTML · JSON · CSV
actions/   →  quarantine · dedup cleanup   (optional)
```

---

## ✨ Optional: embedding-based features

```bash
pip install "imgclean[embeddings]"
```

Enables two checks that use [CLIP](https://github.com/mlfoundations/open_clip) (ViT-B/32):

| Check | What it finds |
|---|---|
| `embedding_duplicates` | Visually similar images even when pHash disagrees — cropped, colour-shifted, or resized variants |
| `outliers` | Images that are visually isolated from the rest of the dataset |

```yaml
# imgclean.yaml
checks:
  embedding_duplicates: true
  outliers: true

thresholds:
  embedding_similarity_min: 0.95
  outlier_knn_k: 5
  outlier_distance_percentile: 95.0
```

```python
report = scan_dataset(
    "./dataset",
    checks=["embedding_duplicates", "outliers"],
)
```

GPU is used automatically when available; falls back to CPU.

---

## 🧪 Test suite

The repo currently ships with **50 automated tests** covering configuration, hashing, duplicate detection, parallel scan plumbing, CLI cleanup flows, reporting, and a synthetic end-to-end scan pipeline.

```bash
make test
make lint   # C901 complexity gate
```

CI runs on Python 3.10, 3.11, and 3.12 for pushes and pull requests.

---

## 🗺️ Roadmap

| Version | Features |
|---|---|
| **v1.1** | Thumbnail galleries in HTML report · Faster SQLite cache |
| **v1.2** | Class-aware analysis · Per-class outliers · Imbalance summary |
| **v1.3** | Bounding box sanity checks · Segmentation mask QA |
| **v2** | Interactive web UI · Dataset version comparison |

---

## Contributing

```bash
git clone https://github.com/Weiykong/imgclean.git
cd imgclean
python3 -m pip install --user uv
make install
make check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local setup, command reference, and PR checklist.

---

## License

[MIT](LICENSE) © Wei Yuan Kong

If imgclean saves you dataset cleanup time, consider starring the repo.
