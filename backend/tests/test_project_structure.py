import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_backend_uses_uv_project_structure() -> None:
    """Verifies that backend setup uses uv without committing `.venv`.

    Assertions:
        - `backend/pyproject.toml` declares project metadata, runtime
          dependencies, dev dependency group, and `[tool.fastapi]`
          entrypoint `app.main:app`.
        - `backend/uv.lock` is present as the reproducible dependency lock.
        - `.gitignore` ignores `backend/.venv/` so the local environment
          remains untracked.
        - `backend/app/api`, `backend/app/core`, and
          `backend/app/features` are Python packages reserved for later
          routers and feature modules.
        - No `requirements.txt` is introduced for Phase 1.
    """
    pyproject = tomllib.loads((ROOT_DIR / "backend" / "pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "reconai-backend"
    assert pyproject["project"]["dependencies"]
    assert pyproject["dependency-groups"]["dev"]
    assert pyproject["tool"]["fastapi"]["entrypoint"] == "app.main:app"
    assert (ROOT_DIR / "backend" / "uv.lock").is_file()
    assert "backend/.venv/" in (ROOT_DIR / ".gitignore").read_text(encoding="utf-8")

    for package_dir in ("api", "core", "features"):
        assert (ROOT_DIR / "backend" / "app" / package_dir / "__init__.py").is_file()

    assert not (ROOT_DIR / "backend" / "requirements.txt").exists()
