import os
import sys

from paths import REPOS_DIR, PDM_BIN_DIR
from multiprocess_utils import run_tasks_in_parallel_iter
from bash_utils import run_subprocess_shell
from install_single_repo import install_single_repo


def main():
    # Modify pdm
    print(f"Setting up pdm...")

    start, end, parallel = sys.argv[1:4]
    start = int(start)
    end = int(end)
    parallel = int(parallel)

    result = run_subprocess_shell(
        f"export PATH={PDM_BIN_DIR} \
            && pdm --version \
            && pdm config install.cache on \
            && pdm config venv.with_pip on \
            && pdm config venv.backend virtualenv \
            && pdm add -g setuptools \
            && pdm add -g wheel \
            && pip install pipreqs\
        ",
    )

    all_repos = sorted(os.listdir(REPOS_DIR))
    all_repos = all_repos[start:end]

    # temporary bugfix (these are all files, not directories)
    blocked_directories = ['.git', '.github', '.gitignore', 'LICENSE', 'README.md', 'assets', 'logs', 'poetry.lock', 'pyproject.toml']        
    all_repos = [i for i in all_repos if i not in blocked_directories]

    results = run_tasks_in_parallel_iter(
        install_single_repo,
        all_repos,
        num_workers=parallel,
        use_progress_bar=True,
    )

    for output in results:
        if output.is_success():
            pass
        else:
            print(output.exception_tb)


if __name__ == "__main__":
    main()
