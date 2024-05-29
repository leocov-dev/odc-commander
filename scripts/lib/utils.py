import contextlib
import os
from pathlib import Path
from collections.abc import Iterator

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()


@contextlib.contextmanager
def cd(target: Path | str) -> Iterator[Path]:
    target = Path(target)
    if target.parts[0] != "/":
        target = REPO_ROOT / target

    current = os.getcwd()
    os.chdir(target)
    yield target
    os.chdir(current)
