#!/usr/bin/env python3

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn, Optional, Sequence, Iterator
import enum
import contextlib
import textwrap
import tempfile
import os
import re
import shutil

SYSTEMD_REPO = "https://github.com/systemd/systemd"
AUTHOR = "CentOS Hyperscale SIG <centos-devel@centos.org>"


class LogFormatter(logging.Formatter):
    def __init__(self, fmt: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        fmt = fmt or "%(message)s"

        bold = "\033[0;1;39m" if sys.stderr.isatty() else ""
        gray = "\x1b[38;20m" if sys.stderr.isatty() else ""
        red = "\033[31;1m" if sys.stderr.isatty() else ""
        yellow = "\033[33;1m" if sys.stderr.isatty() else ""
        reset = "\033[0m" if sys.stderr.isatty() else ""

        self.formatters = {
            logging.DEBUG: logging.Formatter(f"‣ {gray}{fmt}{reset}"),
            logging.INFO: logging.Formatter(f"‣ {fmt}"),
            logging.WARNING: logging.Formatter(f"‣ {yellow}{fmt}{reset}"),
            logging.ERROR: logging.Formatter(f"‣ {red}{fmt}{reset}"),
            logging.CRITICAL: logging.Formatter(f"‣ {red}{bold}{fmt}{reset}"),
        }

        super().__init__(fmt, *args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        return self.formatters[record.levelno].format(record)


def need_verbose():
    return logging.getLogger().level == logging.DEBUG


def run(cmd: Sequence[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, *args, **kwargs, check=True, text=True)
    except FileNotFoundError:
        die(f"{cmd[0]} not found in PATH.")
    except subprocess.CalledProcessError as e:
        logging.error(
            f'"{" ".join(str(s) for s in cmd)}" returned non-zero exit code {e.returncode}.'
        )
        raise e


def die(message: str) -> NoReturn:
    logging.error(message)
    sys.exit(1)


@contextlib.contextmanager
def chdir(directory: Path) -> Iterator[None]:
    old = Path.cwd()

    if old == directory:
        yield
        return

    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old)


def do_build(git_dir: Path, args: argparse.Namespace) -> None:
    systemd_spec = Path.cwd() / "systemd.spec"
    logging.info(f"Copying systemd.spec to {systemd_spec}")
    shutil.copyfile(git_dir / "systemd.spec", systemd_spec)

    logging.info("Downloading sources")
    run(
        [
            "spectool",
            "--define",
            f"_sourcedir {git_dir}",
            "--define",
            "branch main",
            "--get-files",
            f"{systemd_spec}",
        ] + (["--debug"] if need_verbose() else []),
    )

    # We can't determine the version dynamically in the spec so we retrieve it
    # up front and pass it in via a macro.
    version = run(
        [
            "tar",
            "--gunzip",
            "--extract",
            "--to-stdout",
            "--file=main.tar.gz",
            "systemd-main/meson.version",
        ],
        stdout=subprocess.PIPE,
    ).stdout.strip()

    # The timestamp is to ensure the release is always monotonically increasing
    rpmrelease = datetime.now().strftime(r"%Y%m%d%H%M%S")

    logging.info("Modifing systemd.spec")
    systemd_spec.write_text(
        textwrap.dedent(
            f"""\
            %bcond upstream 1
            %define version_override {version}
            %define release_override {rpmrelease}
            %define branch main
            """
        )
        + systemd_spec.read_text()
    )

    if args.repo == "main":
        root = f"centos-stream-hyperscale-{args.release}-x86_64"
    else:
        root = f"centos-stream-hyperscale-{args.repo}-{args.release}-x86_64"

    logging.info("Building src.rpm")
    run(
        [
            "mock",
            "--root",
            root,
            f"--sources={git_dir}",
            "--spec=systemd.spec",
            "--enable-network",
            "--define",
            "%_disable_source_fetch 0",
            "--buildsrpm",
            "--resultdir=.",
        ] + (["--quiet"] if not need_verbose() else []),
    )

    srcrpm = next(Path.cwd().glob("*.src.rpm"))
    logging.info(f"Wrote: {srcrpm}")

    logging.info("Triggering CBS build")
    run(
        [
            "cbs",
            *(["--cert", args.cert] if args.cert else []),
            "build",
            "--wait",
            "--fail-fast",
            "--skip-tag",
            f"hyperscale{args.release}s-packages-{args.repo}-el{args.release}s",
            str(srcrpm),
        ],
    )

    if not args.publish:
        logging.info("Publishing not requested, not tagging builds in testing")
        return

    prefix = "hs+fb" if args.repo == "facebook" else "hs"

    run(
        [
            "cbs",
            *(["--cert", args.cert] if args.cert else []),
            "tag-build",
            f"hyperscale{args.release}s-packages-{args.repo}-testing",
            f"systemd-{version}-{rpmrelease}.{prefix}.el{args.release}",
        ]
    )


def download_rpms(task_id: str, arch: str) -> None:
    run(["cbs", "download-task", "--noprogress", "--arch", arch, str(task_id)])


def get_mkosi_version(file: Path) -> str:
    if m := re.search(r'uses: systemd/mkosi@([a-z0-9]+)', file.read_text()):
        return m.group(1)

    return None


def do_test(git_dir: Path, args: argparse.Namespace) -> None:
    if not args.task_id:
        die("Can't run tests without CBS build id")

    cwd = Path.cwd()

    logging.info("Downloading source RPM")
    download_rpms(args.task_id, "src")

    # it's important to search using args.repo/args.release because
    # otherwise task can be from difference environment
    prefix = "hs+fb" if args.repo == "facebook" else "hs"
    srcrpm_pattern = f"systemd-*-*.{prefix}.el{args.release}.src.rpm"
    srcrpms = list(cwd.glob(srcrpm_pattern))
    if len(srcrpms) != 1:
        die(f"Found no or more than one systemd source RPM ({srcrpm_pattern})")

    srcrpm = srcrpms[0]
    logging.info(f"Found source RPM {srcrpm}")

    logging.info(f"Unpacking {srcrpm}")
    with open(f"{srcrpm}.tar", "w") as rpmtar:
        # rpm2cpio rejects to create tar file itself when runs in a gitlab runner
        run(["rpm2cpio", "--nocompression", f"{srcrpm}"], stdout=rpmtar)
    run(["cpio", "--extract", "--make-directories", "--file", f"{srcrpm}.tar"] +
        (["--verbose"] if need_verbose() else []))

    tarball_pattern = "*.tar.gz"
    tarballs = list(cwd.glob(tarball_pattern))
    if len(tarballs) != 1:
        die("Found no or more than one tarball with glob {tarball_pattern}")

    tarball = tarballs[0]
    logging.info(f"Found tarball {tarball}")

    logging.info(f"Unpacking {tarball}")
    run(["tar", "--gunzip", "--extract", f"--file={tarball}"] +
        (["--verbose"] if need_verbose() else []))

    systemd_dir_pattern = "systemd-*"
    systemd_dirs = [p for p in cwd.glob(systemd_dir_pattern) if p.is_dir()]
    if len(systemd_dirs) != 1:
        die(f"Found no or more than one unpacked systemd directories with glob {systemd_dir_pattern}")

    systemd_dir = systemd_dirs[0]
    logging.info(f"Found unpacked tarball {systemd_dir}")

    logging.info("Setting up mkosi")
    mkosi_version_sha = get_mkosi_version(systemd_dir / ".github/workflows/mkosi.yml")
    if not mkosi_version_sha:
        die("Failed to extract mkosi version")

    logging.info(f"Found mkosi version SHA: {mkosi_version_sha}")

    mkosi_dir = cwd / "mkosi"
    logging.info(f"Cloning mkosi ({mkosi_version_sha}) in {mkosi_dir}")
    run(["git", "clone", "https://github.com/systemd/mkosi", f"{mkosi_dir}"] +
        (["--quiet"] if not need_verbose() else []))
    run(["git", "-C", f"{mkosi_dir}", "checkout", mkosi_version_sha] +
        (["--quiet"] if not need_verbose() else []))

    if not (mkosi_dir / "bin/mkosi").is_file():
        die("Failed to find cloned mkosi")

    os.environ["PATH"] = f"{mkosi_dir / 'bin'}:{os.environ['PATH']}"
    logging.debug(f"Updated PATH={os.environ['PATH']}")

    logging.info("Downloading systemd RPMs")
    packages_dir = systemd_dir / "packages"
    packages_dir.mkdir(exist_ok=True)
    with chdir(packages_dir):
        download_rpms(args.task_id, "noarch")
        download_rpms(args.task_id, os.uname().machine)

    rpm_pattern = "systemd-*.rpm"
    rpms = list(packages_dir.glob(rpm_pattern))
    if not rpms:
        die(f"No systemd RPMs found wih glob {rpm_pattern} in {packages_dir}")

    logging.info(f"Found {len(rpms)} RPMs in {packages_dir}")

    logging.info("Generating mkosi.local.conf")
    mkosi_local_conf = systemd_dir / "mkosi.local.conf"
    mkosi_local_conf.write_text(
        textwrap.dedent(
            f"""\
            [Distribution]
            Distribution=centos
            Release={args.release}
            Repositories=hyperscale-packages-main

            [Build]
            ToolsTreeDistribution=centos
            ToolsTreeRelease={args.release}
            BuildSourcesEphemeral=no
            Environment=NO_BUILD=1
            WithTests=yes

            [Content]
            PackageDirectories={packages_dir}
            SELinuxRelabel=yes
            """
        )
    )

    mkosi_test_env = {
        "NO_BUILD": "1",
        "TEST_SKIP": "TEST-21-DFUZZER",
    }

    # TODO: drop once BTRFS regression is fixed in kernel 6.13
    root_conf = systemd_dir / "mkosi.repart/10-root.conf"
    if root_conf.is_file():
        content = root_conf.read_text()
        root_conf.write_text(content.replace("Format=btrfs", "Format=ext4"))

    # Create missing mountpoint for mkosi sandbox.
    Path('/etc/pacman.d/gnupg').mkdir(parents=True, exist_ok=True)

    # some tunnings
    run(["setenforce", "0"], check=False)
    run(["sysctl", "fs.inotify.max_user_watches=65536"], check=False)
    run(["sysctl", "fs.inotify.max_user_instances=1024"], check=False)
    run(["modprobe", "kvm"], check=False)
    if not Path('/dev/kvm').exists():
        mkosi_test_env["TEST_NO_QEMU"] = "1"

    try:
        with chdir(systemd_dir):
            run(["mkosi", "genkey"])
            run(["mkosi", "-f", "sandbox", "--", "meson", "setup", "--buildtype=debugoptimized", "-Dintegration-tests=true", "build"])
            run(["mkosi", "-f", "sandbox", "--", "meson", "compile", "-C", "build", "mkosi"])
            run(
                [
                    "mkosi",
                    "-f",
                    "sandbox",
                    "--",
                    "meson",
                    "test",
                    "-C",
                    "build",
                    "--no-rebuild",
                    "--suite",
                    "integration-tests",
                    "--print-errorlogs",
                    "--no-stdsplit",
                ],
                env=os.environ | mkosi_test_env,
            )
    finally:
        # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        if os.environ.get("GITLAB_CI"):
            artifacts_dir = git_dir / "artifacts"
            artifacts_dir.mkdir(exist_ok=True)

            logging.info("Collecting logs")
            for log in (systemd_dir / "build/meson-logs").glob("*"):
                if log.is_file():
                    logging.info(f"Moving {log} into {artifacts_dir}")
                    shutil.copy(log, artifacts_dir)

            for log in (systemd_dir / "build/test/journal").glob("*"):
                if log.is_file():
                    logging.info(f"Moving {log} into {artifacts_dir}")
                    shutil.copy(log, artifacts_dir)

    logging.info("All done")


class Verb(enum.Enum):
    build = "build"
    test = "test"
    # publish = "publish" # perhaps should be a separate step, but we will see

    def __str__(self) -> str:
        return self.value

    def run(self, args: argparse.Namespace) -> None:
        if not Path(".git").exists():
            die("The verb must be run from the rpm git repository")

        func = {
            Verb.build: do_build,
            Verb.test: do_test,
        }[self]

        git_dir = Path.cwd()
        with tempfile.TemporaryDirectory(dir='.', prefix='systemd-releng-', delete=args.cleanup) as workdir:
            logging.info(f"Created temporary directory {workdir}, will use it for all further work.")
            if not args.cleanup:
                logging.info("The temporary directory will not be removed at the end!")
            with chdir(Path(workdir)):
                return func(git_dir, args)


def main() -> None:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(LogFormatter())
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel("INFO")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--release",
        help="CentOS Stream release to use (e.g 9)",
        metavar="RELEASE",
        default=9,
        choices=[9, 10],
        type=int,
    )
    parser.add_argument(
        "--repo",
        help="Hyperscale repository to build against",
        choices=["main", "facebook"],
        default="main",
    )
    parser.add_argument(
        "--cert",
        help="Path to the CentOS certificate to use",
        metavar="PATH",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish results of operation (by default only a dry-run is done)",
    )
    parser.add_argument(
        "--task-id",
        help="CBS's task ID to test or publish",
        type=int, # koji: ValueError: invalid literal for int() with base 10
    )
    parser.add_argument(
        "--cleanup",
        help="Clean up temporary files and directories after a run",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--log-level",
        help="Set log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    parser.add_argument(
        "verb",
        type=Verb,
        choices=list(Verb),
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    if args.cert:
        args.cert = args.cert.absolute()

    try:
        args.verb.run(args)
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        logging.error("Interrupted")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
