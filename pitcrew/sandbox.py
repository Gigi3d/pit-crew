"""Where a bay's patch is applied, tested, and timed.

LocalSandbox runs it in a temp copy on this machine, with zero API keys. It is a
faithful stand-in for a Daytona bay: same steps, same measurement discipline.

DaytonaSandbox is the Friday swap. Same interface, but each bay is a real remote
sandbox. The ONE rule you must not break is in its docstring: destroy in finally,
always, or idle sandboxes quietly burn credits.
"""
from __future__ import annotations

import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from typing import Dict, Tuple

_IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc", ".venv")


class LocalSandbox:
    """A disposable temp copy of the target repo. Use as a context manager."""

    def __init__(self, target_repo: str):
        self.target_repo = os.path.abspath(target_repo)
        self.dir: str | None = None

    def __enter__(self) -> "LocalSandbox":
        self.dir = tempfile.mkdtemp(prefix="pitcrew-bay-")
        # copy the repo contents into the (already-created) temp dir
        for name in os.listdir(self.target_repo):
            src = os.path.join(self.target_repo, name)
            dst = os.path.join(self.dir, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=_IGNORE)
            else:
                shutil.copy2(src, dst)
        return self

    def __exit__(self, *exc):
        if self.dir and os.path.isdir(self.dir):
            shutil.rmtree(self.dir, ignore_errors=True)

    # --- primitives ----------------------------------------------------------

    def read(self, rel: str) -> str:
        with open(os.path.join(self.dir, rel)) as f:
            return f.read()

    def write(self, files: Dict[str, str]) -> None:
        for rel, src in files.items():
            path = os.path.join(self.dir, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(src)

    def run_tests(self) -> Tuple[int, int, bool]:
        """Return (passed, total, ok)."""
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"],
            cwd=self.dir, capture_output=True, text=True, timeout=120,
        )
        passed = _count(r.stdout, "passed")
        failed = _count(r.stdout, "failed") + _count(r.stdout, "error")
        return passed, passed + failed, r.returncode == 0

    def _time_once(self, source: str, fixture: str, iters: int) -> float:
        self.write({"app/events.py": source})
        r = subprocess.run(
            [sys.executable, "bench/run.py", fixture, str(iters)],
            cwd=self.dir, capture_output=True, text=True, timeout=120,
        )
        return float(r.stdout.strip().splitlines()[-1])

    def bench_interleaved(self, baseline_src: str, candidate_src: str,
                          fixture: str, rounds: int = 4, iters: int = 3
                          ) -> Tuple[float, float]:
        """Interleave baseline and candidate so host jitter hits both equally.
        Discard the first round as warm-up, return (median baseline, median candidate).
        """
        base, cand = [], []
        for i in range(rounds):
            b = self._time_once(baseline_src, fixture, iters)
            c = self._time_once(candidate_src, fixture, iters)
            if i > 0:                      # drop warm-up
                base.append(b)
                cand.append(c)
        return statistics.median(base), statistics.median(cand)


def _count(text: str, word: str) -> int:
    import re
    m = re.search(r"(\d+)\s+" + word, text)
    return int(m.group(1)) if m else 0


class DaytonaSandbox:
    """Friday swap. Same interface as LocalSandbox, backed by a real remote sandbox.

    Skeleton only: needs DAYTONA_API_KEY. The critical invariant is __exit__:
    the sandbox MUST be destroyed even on error, or it keeps billing. Never move
    the destroy out of the finally/__exit__ path.
    """

    def __init__(self, target_repo: str, snapshot: str | None = None):
        raise NotImplementedError(
            "DaytonaSandbox needs DAYTONA_API_KEY and the daytona SDK. "
            "Implement create() in __enter__ and destroy() in __exit__ "
            "(always, even on exception), mirroring LocalSandbox's methods."
        )
