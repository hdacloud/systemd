#!/usr/bin/env python3

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn, Optional, Sequence, Iterator
from types import FrameType
import contextlib
import textwrap
import tempfile
import os
import re
import shutil
import signal
import multiprocessing

SYSTEMD_REPO = "https://github.com/systemd/systemd"
AUTHOR = "CentOS Hyperscale SIG <centos-devel@centos.org>"
INTERRUPTED = False


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


def run(cmd: Sequence[str], dry_run: bool = False, check: bool = True, *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
    if dry_run:
        logging.info(f'DRY RUN: {" ".join(str(s) for s in cmd)}')
        return

    try:
        logging.info(f'$ {" ".join(str(s) for s in cmd)}')
        return subprocess.run(cmd, *args, **kwargs, check=check, text=True)
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


def get_build_root(args: argparse.Namespace) -> str:
    if args.repo == "main":
        return f"centos-stream-hyperscale-{args.release}-{os.uname().machine}"
    else:
        return f"centos-stream-hyperscale-{args.repo}-{args.release}-{os.uname().machine}"


def get_build_target(args: argparse.Namespace) -> str:
    return f"hyperscale{args.release}s-packages-{args.repo}-el{args.release}s"


def get_build_tag(args: argparse.Namespace) -> str:
    return f"hyperscale{args.release}s-packages-{args.repo}-{args.publish_repo}"


def get_rpm_suffix(args: argparse.Namespace) -> str:
    prefix = "hs+fb" if args.repo == "facebook" else "hs"
    return f"{prefix}.el{args.release}"


def get_task_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Created task:"):
            return line.removeprefix("Created task:").strip()

    return ""


def do_build(git_dir: Path, args: argparse.Namespace) -> None:
    logging.info(f"BUILD: repo={args.repo} release={args.release} source={args.source} scratch={args.scratch}")

    systemd_spec = Path.cwd() / "systemd.spec"
    logging.info(f"Copying systemd.spec to {systemd_spec}")
    shutil.copyfile(git_dir / "systemd.spec", systemd_spec)

    logging.info("Downloading sources")
    run(
        [
            "spectool",
            "--define",
            f"_sourcedir {git_dir}",
            "--get-files",
            f"{systemd_spec}",
            *(["--define", "branch main"] if args.source == "head" else []),
            *(["--debug"] if need_verbose() else []),
        ]
    )

    if args.source == "head":
        # we're building upstream HEAD.
        # Hence going to ignore all version/release/etc in the spec file.

        tarball_pattern = "*.tar.gz"
        tarballs = list(Path.cwd().glob(tarball_pattern))
        if len(tarballs) != 1:
            die("Found no or more than one tarball with glob {tarball_pattern}")

        tarball = tarballs[0]
        logging.info(f"Found tarball {tarball}")

        if tarball.name == "main.tar.gz":
            tarball_internal_dir = "systemd-main"
        elif tarball.match("systemd-*.tar.gz"):
            tarball_internal_dir = tarball.name.removesuffix(".tar.gz")
        else:
            die(f"Tarball {tarball} has unknown prefix")

        # We can't determine the version dynamically in the spec so we retrieve it
        # up front and pass it in via a macro.
        version = run(
            [
                "tar",
                "--gunzip",
                "--extract",
                "--to-stdout",
                f"--file={tarball}",
                f"{tarball_internal_dir}/meson.version",
            ],
            stdout=subprocess.PIPE,
        ).stdout.strip()

        # The timestamp is to ensure the release is always monotonically increasing
        release = datetime.now().strftime(r"%Y%m%d%H%M%S")

        logging.info(f"Modifing systemd.spec with version={version} release={release}")
        systemd_spec.write_text(
            textwrap.dedent(
                f"""\
                %bcond upstream 1
                %define version_override {version}
                %define release_override {release}
                %define branch main
                """
            )
            + systemd_spec.read_text()
        )

    logging.info("Building systemd src.rpm")
    run(
        [
            "mock",
            "--root=" + get_build_root(args),
            f"--sources={git_dir}",
            "--spec=systemd.spec",
            "--enable-network",
            "--define",
            "%_disable_source_fetch 0",
            "--buildsrpm",
            "--resultdir=.",
            *(["--quiet"] if not need_verbose() else []),
        ]
    )

    srcrpm = next(Path.cwd().glob("*.src.rpm"))
    logging.info(f"Wrote: {srcrpm}")

    build_target = get_build_target(args)
    logging.info(f"Triggering CBS build for {build_target}")
    cbs_build = run(
        [
            "cbs",
            *(["--cert", args.cert] if args.cert else []),
            "build",
            "--nowait",
            "--noprogress",
            "--fail-fast",
            "--skip-tag",
            build_target,
            str(srcrpm),
            *(["--scratch"] if args.scratch else []),
        ],
        stdout=subprocess.PIPE,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        return

    # explicetly not using logging.*
    print(cbs_build.stdout, end='', flush=True)

    task_id = get_task_id(cbs_build.stdout)
    if not task_id:
        die("'cbs build' completed but failed to found task id in CBS's output")

    try:
        run(
            [
                "cbs",
                *(["--cert", args.cert] if args.cert else []),
                "watch-task",
                task_id,
            ]
        )
    except (subprocess.CalledProcessError, KeyboardInterrupt) as e:
        # This logic is to cancel task id. In general, handing
        # KeyboardInterrupt should be enough. But in some case, the child
        # process receives and manages to exit faster then this process. As
        # result, we see and negative exit code (-15) instead of
        # KeyboardInterrupt.

        logging.info("CBS was interrupted or exited with an error")
        logging.info(f"Let's make sure task {task_id} has been cancelled!")
        cancel_process = run(["cbs", *(["--cert", args.cert] if args.cert else []), "cancel", f"{task_id}"], check=False)
        if cancel_process.returncode == 0:
            logging.info(f"Successfully cancelled task {task_id}.")
        else:
            logging.info(f"Failed to cancel task {task_id}. Check logs.")

        raise e

    logging.info(f"All done. Task ID: {task_id}")
    logging.info("")
    logging.info(f"$ ./releng.py --repo={args.repo} --release={args.release} test --task-id={task_id}")
    logging.info(f"$ ./releng.py --repo={args.repo} --release={args.release} publish --task-id={task_id}")

    # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    if os.environ.get("GITLAB_CI"):
        artifacts_dir = git_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        task_id_file = artifacts_dir / f"{build_target}-{args.source}-task-id.txt"
        logging.info("")
        logging.info(f"Dumping task id to {task_id_file}")
        task_id_file.write_text(task_id)


def do_publish(git_dir: Path, args: argparse.Namespace) -> None:
    if not args.task_id:
        die("Can't run tests without CBS build id")

    logging.info(f"PUBLISH: repo={args.repo} release={args.release} task_id={args.task_id} publish_repo={args.publish_repo}")

    logging.info("Downloading source RPM")
    download_rpms(args.task_id, "src")

    # it's important to search using args.repo/args.release because
    # otherwise task can be from difference environment
    rpm_suffix = get_rpm_suffix(args)
    srcrpm_pattern = f"systemd-*-*.{rpm_suffix}.src.rpm"
    srcrpms = list(Path.cwd().glob(srcrpm_pattern))
    if len(srcrpms) != 1:
        die(f"Found no or more than one systemd source RPM ({srcrpm_pattern})")

    srcrpm = srcrpms[0]
    logging.info(f"Found source RPM {srcrpm}")

    tag = get_build_tag(args)
    package = srcrpm.name.removesuffix(".src.rpm")
    logging.info(f"Tag package {package} with '{tag}' tag")

    run(
        [
            "cbs",
            *(["--cert", args.cert] if args.cert else []),
            "tag-build",
            tag,
            package,
        ],
        dry_run=args.dry_run,
    )

    # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    if os.environ.get("GITLAB_CI"):
        artifacts_dir = git_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        git_tag = package.replace("~", "-")  # TODO need comes up with a standard
        tag_file = artifacts_dir / f"{git_tag}-tag.txt"
        logging.info("")
        logging.info(f"Dumping git_tag {git_tag} to {tag_file}")
        tag_file.write_text(git_tag)


def download_rpms(task_id: str, arch: str) -> None:
    run(["cbs", "download-task", "--noprogress", "--arch", arch, str(task_id)])


def get_mkosi_version(file: Path) -> str:
    if m := re.search(r'uses: systemd/mkosi@([a-z0-9]+)', file.read_text()):
        return m.group(1)

    return None


def collect_build_and_test_logs(work_dir: Path, target_dir: Path):
    for log in (work_dir / "build/meson-logs").glob("*"):
        if log.is_file():
            logging.info(f"Moving {log} into {target_dir}")
            shutil.copy(log, target_dir)

    for log in (work_dir / "build/test/journal").glob("*"):
        if log.is_file():
            logging.info(f"Moving {log} into {target_dir}")
            shutil.copy(log, target_dir)


def do_test(git_dir: Path, args: argparse.Namespace) -> None:
    if not args.task_id:
        die("Can't run tests without CBS build id")

    logging.info(f"PUBLISH: repo={args.repo} release={args.release} task_id={args.task_id}")

    cwd = Path.cwd()

    logging.info("Downloading source RPM")
    download_rpms(args.task_id, "src")

    # it's important to search using args.repo/args.release because
    # otherwise task can be from difference environment
    rpm_suffix = get_rpm_suffix(args)
    srcrpm_pattern = f"systemd-*-*.{rpm_suffix}.src.rpm"
    srcrpms = list(cwd.glob(srcrpm_pattern))
    if len(srcrpms) != 1:
        die(f"Found no or more than one systemd source RPM ({srcrpm_pattern})")

    srcrpm = srcrpms[0]
    logging.info(f"Found source RPM {srcrpm}")

    logging.info(f"Unpacking {srcrpm}")
    with open(f"{srcrpm}.tar", "w") as rpmtar:
        # rpm2cpio rejects to create tar file itself when runs in a gitlab runner
        run(["rpm2cpio", f"{srcrpm}"], stdout=rpmtar)
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

    mkosi_version = run(["mkosi", "--version"], stdout=subprocess.PIPE).stdout.strip()
    mkosi_version_match = re.match(r"mkosi ([0-9]+)(~devel)?", mkosi_version)
    mkosi_dash_dash = mkosi_version_match and int(mkosi_version_match.group(1)) >= 26
    logging.debug(f"mkosi --version = {mkosi_version}. mkosi_dash_dash={mkosi_dash_dash}")

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

    mkosi_env = {
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
        mkosi_env["TEST_NO_QEMU"] = "1"
    if (cpu_count := multiprocessing.cpu_count()) > 10:
        mkosi_env["TEST_JOURNAL_USE_TMP"] = "1"
        nproc = int(cpu_count / 3)
    else:
        nproc = int(cpu_count - 1)

    logging.info(f"mkosi_env={mkosi_env}")

    if need_verbose():
        run(["id"], check=False)
        run(["lscpu"], check=False)
        run(["lsmem"], check=False)
        run(["lsmod"], check=False)

    try:
        with chdir(systemd_dir):
            if need_verbose():
                run(["mkosi", "summary"], dry_run=args.dry_run)

            run(["mkosi", "genkey"], dry_run=args.dry_run)
            run(
                [
                    "mkosi",
                    "-f",
                    "sandbox",
                    *(["--"] if mkosi_dash_dash else []),
                    "meson",
                    "setup",
                    "--buildtype=debugoptimized",
                    "-Dintegration-tests=true",
                    "build"
                ],
                env=os.environ | mkosi_env,
                dry_run=args.dry_run
            )

            run(
                [
                    "mkosi",
                    "-f",
                    "sandbox",
                    *(["--"] if mkosi_dash_dash else []),
                    "meson",
                    "compile",
                    "-C",
                    "build",
                    "mkosi"
                ],
                env=os.environ | mkosi_env,
                dry_run=args.dry_run
            )

            run(
                [
                    "mkosi",
                    "-f",
                    "sandbox",
                    *(["--"] if mkosi_dash_dash else []),
                    "meson",
                    "test",
                    "-C",
                    "build",
                    "--no-rebuild",
                    "--suite",
                    "integration-tests",
                    "--print-errorlogs",
                    "--no-stdsplit",
                    "--num-processes",
                    str(nproc),
                ],
                env=os.environ | mkosi_env,
                dry_run=args.dry_run,
            )
    finally:
        # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        if os.environ.get("GITLAB_CI"):
            artifacts_dir = git_dir / "artifacts"
            artifacts_dir.mkdir(exist_ok=True)
            logging.info(f"Collecting logs to {artifacts_dir}")
            collect_build_and_test_logs(systemd_dir, artifacts_dir)
        elif os.environ.get("TMT_TEST_DATA"):
            test_data_dir = Path(os.environ.get("TMT_TEST_DATA"))
            test_data_dir.mkdir(exist_ok=True)
            logging.info(f"Collecting logs to {test_data_dir}")
            collect_build_and_test_logs(systemd_dir, test_data_dir)

    logging.info("All done")


def onsignal(signal: int, frame: Optional[FrameType]) -> None:
    global INTERRUPTED
    if INTERRUPTED:
        return

    INTERRUPTED = True
    raise KeyboardInterrupt()


def main() -> None:
    signal.signal(signal.SIGINT, onsignal)
    signal.signal(signal.SIGTERM, onsignal)
    signal.signal(signal.SIGHUP, onsignal)

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(LogFormatter())
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel("INFO")

    parser = argparse.ArgumentParser(description='releng.py CLI')

    parser.add_argument(
        "--repo",
        help="Hyperscale repository to build against",
        choices=["main", "facebook"],
        default="main",
    )
    parser.add_argument(
        "--release",
        help="CentOS Stream release to use (e.g 9)",
        metavar="RELEASE",
        default=9,
        choices=[9, 10],
        type=int,
    )
    parser.add_argument(
        "--cert",
        help="Path to the CentOS certificate to use",
        metavar="PATH",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--cleanup",
        help="Clean up temporary files and directories after a run",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--dry-run",
        help="Activate dry run",
        action="store_true",
    )
    parser.add_argument(
        "--log-level",
        help="Set log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )

    subparsers = parser.add_subparsers(dest='verb')

    build_parser = subparsers.add_parser('build', help='Build command')
    build_parser.add_argument(
        "--source",
        choices=["head", "spec"],
        default="head",
        help="Do build using upstream HEAD or version from spec file",
    )
    build_parser.add_argument(
        "--scratch",
        help="Do scratch build",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    test_parser = subparsers.add_parser('test', help='Test command')
    test_parser.add_argument(
        "--task-id",
        required=True,
        help="CBS's task ID to test",
        type=int,  # koji: ValueError: invalid literal for int() with base 10
    )

    publish_parser = subparsers.add_parser('publish', help='Publish command')
    publish_parser.add_argument(
        "--task-id",
        required=True,
        help="CBS's task ID to publish",
        type=int,  # koji: ValueError: invalid literal for int() with base 10
    )
    publish_parser.add_argument(
        "--publish-repo",
        help="Publish package to 'release' or 'testing' repo",
        choices=['release', 'testing'],
        default='testing',
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    if args.cert:
        args.cert = args.cert.absolute()

    if not Path(".gitlab-ci.yml").exists():
        # testing-fram clones repo without .git
      die("The verb must be run from the rpm git repository")

    try:
        func = {
            "build": do_build,
            "test": do_test,
            "publish": do_publish,
        }[args.verb]

        git_dir = Path.cwd()
        with tempfile.TemporaryDirectory(dir='.', prefix='systemd-releng-', delete=args.cleanup) as workdir:
            logging.info(f"Created temporary directory {workdir}, will use it for all further work.")
            if not args.cleanup:
                logging.info("The temporary directory will not be removed at the end!")
            with chdir(Path(workdir)):
                return func(git_dir, args)
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        logging.error("Interrupted")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
