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
import shutil
import signal
import urllib.request
import time
import re

REPOS = ["main", "facebook"]
RELEASES = [9, 10]
SOURCES = ["head", "spec"]
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


def get_build_tag_for(release: str, repo: str, publish_repo: str = "") -> str:
    return f"hyperscale{release}s-packages-{repo}-{publish_repo if publish_repo else publish_repo}"


def get_build_tag(args: argparse.Namespace, publish_repo: str = "") -> str:
    return get_build_tag_for(args.release, args.repo, publish_repo)


def get_rpm_suffix_for(release: str, repo: str) -> str:
    prefix = "hs+fb" if repo == "facebook" else "hs"
    return f"{prefix}.el{release}"


def get_rpm_suffix(args: argparse.Namespace) -> str:
    return get_rpm_suffix_for(args.release, args.repo)


def get_task_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Created task:"):
            return line.removeprefix("Created task:").strip()

    return ""


def update_spec_for_head_build(args: argparse.Namespace, original_systemd_spec: Path, latest_sha: str) -> Path:
    # we're building upstream HEAD.
    # Hence going to ignore all version/release/etc in the spec file.

    systemd_spec = Path.cwd() / "systemd.spec"
    logging.info(f"Copying {original_systemd_spec} to {systemd_spec}")
    shutil.copyfile(original_systemd_spec, systemd_spec)

    tarball = Path(f"systemd-{latest_sha}.tar.gz")
    if not tarball.exists():
        die(f"Tarball f{tarball} does not exist")

    # We can't determine the version dynamically in the spec so we retrieve it
    # up front and pass it in via a macro.
    version = run(
        [
            "tar",
            "--gunzip",
            "--extract",
            "--to-stdout",
            f"--file={tarball}",
            f"systemd-{latest_sha}/meson.version",
        ],
        stdout=subprocess.PIPE,
    ).stdout.strip()

    # The timestamp is to ensure the release is always monotonically increasing
    release_date = datetime.now().strftime(r"%Y%m%d%H%M%S")
    release_extra = f".{args.rpm_extra_info}" if args.scratch and args.rpm_extra_info else ""
    release = f"{release_date}{release_extra}"

    logging.info(f"Modifing {systemd_spec} with version={version} release={release} commit={latest_sha}")
    systemd_spec.write_text(
        textwrap.dedent(
            f"""\
            %bcond upstream 1
            %define version_override {version}
            %define release_override {release}
            %define commit {latest_sha}
            """
        )
        + systemd_spec.read_text()
    )

    return systemd_spec


def update_spec_for_spec_scratch_build(args: argparse.Namespace, original_systemd_spec: Path) -> Path:
    # we're building from spec, but it's a scratch build.
    # So, need to include extra info for debugability

    systemd_spec = Path.cwd() / "systemd.spec"
    logging.info(f"Copying {original_systemd_spec} to {systemd_spec}")
    shutil.copyfile(original_systemd_spec, systemd_spec)

    release_spec = rpmspec_query(args, systemd_spec, "%{release}")
    if not release_spec:
        die("Failed to get systemd release from systemd.spec")

    release_date = datetime.now().strftime(r"%Y%m%d%H%M%S")
    release_extra = f".{args.rpm_extra_info}" if args.rpm_extra_info else ""
    release = f"{release_spec}~{release_date}{release_extra}"

    logging.info(f"Modifing {systemd_spec} with release={release}")
    systemd_spec.write_text(f"%define release_override {release}\n" + systemd_spec.read_text())
    return systemd_spec


def rpmspec_query(args: argparse.Namespace, systemd_spec: Path, query: str, undef_list=None) -> str:
    if undef_list is None:
        undef_list = ["dist"]

    return run(
        [
            "rpmspec",
            "--define",
            f"_sourcedir {args.git_dir}",
            "--query",
            "--queryformat",
            query,
            *(sum((["--undefine", f"{item}"] for item in undef_list), [])),
            "--srpm",
            f"{systemd_spec}",
        ],
        stdout=subprocess.PIPE,
    ).stdout.strip()


def get_latest_build_systemd_version(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("systemd-"):
            return line.split()[0].strip()

    return ""


def updated_sources_checksum_and_upload(args: argparse.Namespace, systemd_spec: Path) -> None:
    version = rpmspec_query(args, systemd_spec, "%{version}")
    if not version:
        die("Failed to get systemd version from systemd.spec")

    tarball = Path(f"systemd-{version}.tar.gz")
    if not tarball.exists():
        die(f"Tarball {tarball} does not exist")

    sources_file = args.git_dir / "sources"
    if not sources_file.exists():
        die(f"{sources_file} does not exist")

    old_checksum = sources_file.read_text().strip()

    logging.info(f"Updating {sources_file} with tarball's checksum")
    with open(sources_file, "w") as f:
        run(["sha512sum", "--tag", str(tarball)], stdout=f)

    new_checksum = sources_file.read_text().strip()
    logging.info(f"New checksum:\n{new_checksum}")

    if new_checksum == old_checksum:
        logging.info("Checksum didn't change. No need to upload tarball")
    else:
        logging.info("Uploading tarball to look-aside cache")
        run(
            [
                "centos-lookaside-upload-sig",
                "-f",
                str(tarball),
                "-n",
                "systemd",
            ],
            dry_run=args.dry_run,
        )


def update_spec_for_spec_autorelease_build(args: argparse.Namespace, systemd_spec: Path) -> None:
    # verify and potentially update release_override in systemd.spec

    systemd_version = rpmspec_query(args, systemd_spec, "%{name}-%{version}-%{release}")
    if not systemd_version:
        die("Failed to get systemd version from systemd.spec")

    logging.info(f"systemd version: {systemd_version}")

    build_tag = get_build_tag(args, "release")
    logging.info(f"Quering CBS for latest-build of {build_tag}")
    output = run(
        [
            "cbs",
            *(["--cert", args.cert] if args.cert else []),
            "latest-build",
            "--quiet",
            "--all",
            build_tag,
        ],
        stdout=subprocess.PIPE,
    ).stdout.strip()

    cbs_systemd_version = get_latest_build_systemd_version(output)
    cbs_systemd_version = cbs_systemd_version.removesuffix("." + get_rpm_suffix(args))  # remove .hs+fb.el10 for 257.3-1.5.hs+fb.el10
    if not cbs_systemd_version:
        die("Failed to get latest systemd build from CBS")

    logging.info(f"Latest systemd build: {cbs_systemd_version}")
    vercmp_result = run(["systemd-analyze", "compare-versions", systemd_version, "==", cbs_systemd_version], check=False)
    if vercmp_result.returncode != 0:
        logging.info(f"systemd version in systemd.spec '{systemd_version}' doesn't match one in CBS '{cbs_systemd_version}'")
        logging.info("Cannot do autoincrement of release_override! Continue as usual!")
        return

    logging.info("systemd version in systemd.spec matches one in CBS")

    systemd_release = rpmspec_query(args, systemd_spec, "%{release}")
    if not systemd_release:
        die("Failed to get systemd release from systemd.spec")

    parts = systemd_release.split(".")
    parts[-1] = int(parts[-1]) + 1  # increment last element by 1
    incremented_systemd_release = ".".join(map(str, parts))
    logging.info(f"New systemd release: {incremented_systemd_release}")

    logging.info("Verifing that new systemd_release is higher than old one")
    vercmp_result = run(["systemd-analyze", "compare-versions", incremented_systemd_release, ">", systemd_release], check=False)
    if vercmp_result.returncode != 0:
        die(f"Failed to confirm that: {incremented_systemd_release} > {systemd_release}")

    logging.info("Verification is correct!")
    logging.info(f"Modifing {systemd_spec} with release={incremented_systemd_release}")
    systemd_spec.write_text(
        systemd_spec.read_text().replace(
            "%{!?release_override:" + systemd_release + "}",
            "%{!?release_override:" + incremented_systemd_release + "}"
        )
    )


def get_latest_systemd_sha(branch):
    max_retries = 3
    retry_delay = 1  # seconds
    for attempt in range(max_retries + 1):
        try:
            logging.info(f"Requesting latest SHA for branch: {branch}")
            req = urllib.request.Request(
                f"https://api.github.com/repos/systemd/systemd/commits/{branch}",
                headers={"Accept": "application/vnd.github.VERSION.sha"}
            )

            with urllib.request.urlopen(req) as response:
                if response.getcode() != 200:
                    raise Exception(f"Failed to request latest SHA: {response.getcode()}")

                latest_sha = response.read().decode()
                logging.info(f"Latest SHA: {latest_sha}")
                return latest_sha
        except Exception as e:
            if attempt < max_retries:
                logging.warning(f"Retry {attempt + 1}/{max_retries} failed: {e}")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to request latest SHA after {max_retries} retries: {e}")
                raise e


def do_build(args: argparse.Namespace) -> None:
    logging.info(f"BUILD: repo={args.repo} release={args.release} source={args.source} scratch={args.scratch} autorelease={args.autorelease}")
    systemd_spec = args.git_dir / "systemd.spec"

    # Fetching of sha happens per child-pipeline which will likely cause inconsistency.
    # This is acceptable because it happens only for HEAD builds which MR or nighlty builds.
    # So, slight inconsistency is acceptable there.
    latest_sha = get_latest_systemd_sha("main") if args.source == "head" else ""

    logging.info("Downloading sources")
    run(
        [
            "spectool",
            "--sources",
            "--define",
            f"_sourcedir {args.git_dir}",
            "--get-files",
            f"{systemd_spec}",
            *(["--define", f"commit {latest_sha}"] if args.source == "head" else []),
            *(["--debug"] if need_verbose() else []),
        ]
    )

    if args.source == "head":
        systemd_spec = update_spec_for_head_build(args, systemd_spec, latest_sha)
    elif args.source == "spec":
        if args.scratch:
            systemd_spec = update_spec_for_spec_scratch_build(args, systemd_spec)
        elif args.autorelease:
            updated_sources_checksum_and_upload(args, systemd_spec)
            update_spec_for_spec_autorelease_build(args, systemd_spec)

    logging.info("Building systemd src.rpm")
    run(
        [
            "mock",
            "--root=" + get_build_root(args),
            f"--sources={args.git_dir}",
            f"--spec={systemd_spec}",
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
    logging.info(f"$ ./releng.py --repo={args.repo} --release={args.release} publish --task-id={task_id}")

    # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    if os.environ.get("GITLAB_CI"):
        artifacts_dir = args.git_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        task_id_file = artifacts_dir / f"{build_target}-{args.source}-task-id.txt"
        logging.info("")
        logging.info(f"Dumping task id to {task_id_file}")
        task_id_file.write_text(task_id)


def do_publish(args: argparse.Namespace) -> None:
    if not args.task_id:
        die("Can't publish rpms without CBS build id")

    logging.info(f"PUBLISH: repo={args.repo} release={args.release} task_id={args.task_id} publish_repo={args.publish_repo}")

    srcrpm = download_and_validate_src_rpm(args)
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
        artifacts_dir = args.git_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        git_tag = package.replace("~", "-")  # TODO need comes up with a standard
        tag_file = artifacts_dir / f"{git_tag}-tag.txt"
        logging.info("")
        logging.info(f"Dumping git_tag {git_tag} to {tag_file}")
        tag_file.write_text(git_tag)


def download_rpms(task_id: str, arch: str) -> None:
    run(["cbs", "download-task", "--noprogress", "--arch", arch, str(task_id)])


def download_and_validate_src_rpm(args: argparse.Namespace) -> Path:
    logging.info("Downloading source RPM")
    download_rpms(args.task_id, "src")

    # it's important to search using args.repo/args.release because
    # otherwise task can be from difference environment
    rpm_suffix = get_rpm_suffix(args)
    srcrpm_pattern = f"systemd-*-*.{rpm_suffix}.src.rpm"
    srcrpms = list(Path.cwd().glob(srcrpm_pattern))
    if len(srcrpms) != 1:
        die(f"Found no or more than one systemd source RPM ({srcrpm_pattern})")

    logging.info(f"Found source RPM {srcrpms[0]}")
    return srcrpms[0]


def rpm_query(rpm: Path, query: str) -> str:
    return run(
        [
            "rpm",
            "--query",
            "--queryformat",
            query,
            f"{rpm}",
        ],
        stdout=subprocess.PIPE,
    ).stdout.strip()


def do_unpack(args: argparse.Namespace) -> None:
    if not args.task_id:
        die("Can't publish rpms without CBS build id")

    logging.info(f"UNPACK: repo={args.repo} release={args.release} task_id={args.task_id}")

    srcrpm = download_and_validate_src_rpm(args)

    logging.info("Searching for patches")
    # here we query patches. They are ordered! Should be applied in reverse order though!
    patches = rpm_query(srcrpm, "[%{patch}\n]").splitlines()
    patches = list(reversed(patches))
    if len(patches) > 0:
        logging.info(f"Found {len(patches)} patches")

        logging.info(f"Unpacking {srcrpm}")
        with open(f"{srcrpm}.tar", "w") as rpmtar:
            # rpm2cpio rejects to create tar file itself when runs in a gitlab runner
            run(["rpm2cpio", f"{srcrpm}"], stdout=rpmtar)

        run(["cpio", "--extract", "--make-directories", "--file", f"{srcrpm}.tar", *(["--verbose"] if need_verbose() else [])])

        for i, patch in enumerate(patches):
            patch = patches[i] = Path.cwd() / patch
            logging.info(f"  - {patch.name}")
            if not patch.exists():
                die(f"Patch {patch} does not exist")
    else:
        logging.info("Found no patches. Still going to push to have clean tag in the unpacked repo")

    logging.info("Searching for source code version")
    output = rpm_query(srcrpm, "%{version}")
    if not output:
        die(f"Failed to query version from source RPM: {srcrpm}")

    if "~devel" in output:
        systemd_source_pattern = r"^systemd-[0-9a-f]+\.tar\.gz$"
        sources = rpm_query(srcrpm, "[%{source}\n]").splitlines()
        source = next((s for s in sources if re.match(systemd_source_pattern, s)), None)
        if not source:
            die(f"Failed to find file matching regexp '{systemd_source_pattern}' among spec sources")
        git_source_tag_or_commit = source.removeprefix("systemd-").removesuffix(".tar.gz")
    else:
        git_source_tag_or_commit = "v" + output

    logging.info(f"systemd source tag/commit to apply patches on top: {git_source_tag_or_commit}")

    git_unpacked_tag = rpm_query(srcrpm, "%{name}-%{version}-%{release}")
    git_unpacked_tag = git_unpacked_tag.replace("~", "-")
    git_unpacked_tag_upstream = f"{git_unpacked_tag}-upstream"
    logging.info(f"systemd unpack tags to push patches code to: {git_unpacked_tag} {git_unpacked_tag_upstream}")

    with tempfile.TemporaryDirectory(dir='.', prefix='systemd-source-', delete=args.cleanup) as repodir:
        run(["git", "clone", "https://github.com/systemd/systemd.git", str(repodir)])
        run(["git", "config", "--global", "user.email", "hyperscalebot@example.com"])
        run(["git", "config", "--global", "user.name", "hyperscalebot"])

        with chdir(Path(repodir)):
            run(["git", "checkout", git_source_tag_or_commit, *([] if need_verbose() else ["--quiet"])])
            run(["git", "tag", git_unpacked_tag_upstream])

            for patch in patches:
                run(["git", "am", str(patch)])
            run(["git", "tag", git_unpacked_tag])

            if os.environ.get("GITLAB_CI"):
                logging.info("Pushing to the unpacked repo")
                unpack_git_token = os.environ.get("GIT_PUSH_TOKEN_SYSTEMD_UNPACKED")
                if not unpack_git_token:
                    die("Can't push to unpack repo without GIT_PUSH_TOKEN_SYSTEMD_UNPACKED")

                # token is scrubbed by gitlab UI
                ci_server_host = os.environ.get("CI_SERVER_HOST")
                repo_url = f"https://hyperscalebot:{unpack_git_token}@{ci_server_host}/CentOS/Hyperscale/rpms-unpacked/systemd.git"
                run(["git", "remote", "add", "unpack", repo_url])
                run(["git", "push", "--force", "unpack", "tag", git_unpacked_tag, git_unpacked_tag_upstream], dry_run=args.dry_run)

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
        "--cert",
        help="Path to the CentOS certificate to use",
        metavar="PATH",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--git-dir",
        help="Path to Git repo, defaults to current dir",
        metavar="PATH",
        type=Path,
        default=Path.cwd(),
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

    repo_release_parser = argparse.ArgumentParser(add_help=False)
    repo_release_parser.add_argument(
        "--repo",
        help="Hyperscale repository to build against",
        choices=REPOS,
        default="main",
    )
    repo_release_parser.add_argument(
        "--release",
        help="CentOS Stream release to use (e.g 9)",
        metavar="RELEASE",
        choices=RELEASES,
        default=9,
        type=int,
    )

    subparsers = parser.add_subparsers(dest='verb')
    build_parser = subparsers.add_parser('build', help='Build command', parents=[repo_release_parser])
    build_parser.add_argument(
        "--source",
        choices=SOURCES,
        default="head",
        help="Do build using upstream HEAD or version from spec file",
    )
    build_parser.add_argument(
        "--scratch",
        help="Do scratch build",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    build_parser.add_argument(
        "--autorelease",
        help="Enables autorelease mode which can increment `release_override` in systemd.spec. " +
             "It also uploads source tarball to CBS and updates checksum. " +
             "Autorelease mode leaves changes in systemd.spec which should be commited to Git. " +
             "Noop if --scratch or --source=head.",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    build_parser.add_argument(
        "--rpm-extra-info",
        help="Extra information to include into RPM name. Useful to include short MR name/number. " +
             "This options works only with --scratch present.",
    )

    publish_parser = subparsers.add_parser('publish', help='Publish command', parents=[repo_release_parser])
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

    unpack_parser = subparsers.add_parser('unpack',
                                          help='Unpack systemd RPMs content and, optionally, push it to https://gitlab.com/CentOS/Hyperscale/rpms-unpacked/systemd',
                                          parents=[repo_release_parser])
    unpack_parser.add_argument(
        "--task-id",
        required=True,
        help="CBS's task ID to publish",
        type=int,  # koji: ValueError: invalid literal for int() with base 10
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    if args.cert:
        args.cert = args.cert.absolute()

    if not (args.git_dir / ".gitlab-ci.yml").exists():
        # testing-fram clones repo without .git
        die("The verb must be run from the rpm git repository")

    try:
        func = {
            "build": do_build,
            "publish": do_publish,
            "unpack": do_unpack,
        }[args.verb]

        with tempfile.TemporaryDirectory(dir='.', prefix='systemd-releng-', delete=args.cleanup) as workdir:
            logging.info(f"Created temporary directory {workdir}, will use it for all further work.")
            if not args.cleanup:
                logging.info("The temporary directory will not be removed at the end!")
            with chdir(Path(workdir)):
                return func(args)
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        logging.error("Interrupted")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
