#! /usr/bin/env python3
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Union
import venv


def _does_env_require_creation(where: Path) -> bool:
    python_in_env = where / 'bin' / 'python'
    pip_in_env = where / 'bin' / 'pip'
    if not python_in_env.exists() or not pip_in_env.exists():
        return True
    return False


class TestEnv():
    def __init__(self, where: Path) -> None:
        self.where = Path(where)
        if _does_env_require_creation(where):
            shutil.rmtree(where)
            venv.create(self.where, with_pip=True)

    def install(self, package: Union[Path, str]) -> None:
        package_as_path = Path(package)
        if package_as_path.exists():
            package_as_path = package_as_path.absolute()
            if str(package_as_path).endswith('.txt'):
                to_install = ['-r', str(package_as_path)]
            else:
                to_install = [str(package_as_path)]
        else:
            to_install = [str(package)]

        print(f'Installing: {package}')
        self.run('pip', ['install', '-q'] + to_install)

    def run(self, cmd, args=None):
        args = args or []
        env_bin_path = self.where / 'bin'
        env_exe = env_bin_path / cmd
        if env_exe.exists():
            exe = str(env_exe.absolute())
        else:
            exe = shutil.which(cmd)

        env = os.environ.copy()
        env.update({
            'PATH': f"{env_bin_path}:{env.get('PATH', '')}"
        })

        subprocess.check_call([exe] + args, env=env)

    def __exit__(self, exc_type, exc_val, traceback):
        self.dir.cleanup()


def _get_current_version() -> str:
    try:
        return Path('version.txt').read_text().strip()
    except FileNotFoundError:
        print('Tests expect to run from project root.', file=sys.stderr)
        raise


def _get_package_path() -> Path:
    version = _get_current_version()
    install_artefact = \
        Path().joinpath('dist',
                        f'webwatcher-{version}-py3-none-any.whl')

    if not install_artefact.exists():
        print('You need to build before running tests '
                '- try ci/build.sh. If you\'re running '
                'in a dev env, try doing a local install '
                'and testing with pytest', file=sys.stderr)

        raise RuntimeError('Package not build - not proceeding')
    return install_artefact


class LocalEnv:
    def __init__(self, where):
        self.name = where

    def __enter__(self):
        try:
            os.makedirs(self.name)
        except FileExistsError:
            if not Path(self.name).is_dir():
                raise

    def __exit__(self, *args, **kwargs):
        pass

    def cleanup(self):
        pass


@contextmanager
def test_env():
    local_env = Path('.testing_env')
    if os.getenv('CI'):
        e = tempfile.TemporaryDirectory()
    else:
        if '--clean' in sys.argv:
            shutil.rmtree(local_env)

        e = LocalEnv(local_env)

    try:
        yield e.name
    finally:
        e.cleanup()


def run_tests() -> None:
    artefact = _get_package_path()

    with test_env() as location:
        env = TestEnv(location)
        env.install(artefact)
        env.install(Path('test-requirements.txt'))
        env.run('pytest')


if __name__ == '__main__':
    run_tests()
