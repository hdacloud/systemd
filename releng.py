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
def restore(path: Path) -> Iterator[None]:
    old = path.read_text()
    try:
        yield
    finally:
        path.write_text(old)


def do_cd(args: argparse.Namespace) -> None:
    if not Path(".git").exists():
        die("The cd verb must be run from the rpm git repository")

    logging.info("Downloading sources")
    run(
        [
            "spectool",
            "--define",
            f"_sourcedir {Path.cwd()}",
            "--define",
            "branch main",
            "--get-files",
            "systemd.spec",
        ],
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

    with restore(Path("systemd.spec")):
        Path("systemd.spec").write_text(
            textwrap.dedent(
                f"""\
                %bcond upstream 1
                %define version_override {version}
                %define release_override {rpmrelease}
                %define branch main
                """
            )
            + Path("systemd.spec").read_text()
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
                "--sources=.",
                "--spec=systemd.spec",
                "--enable-network",
                "--define",
                "%_disable_source_fetch 0",
                "--buildsrpm",
                "--resultdir=.",
            ],
        )

    srcrpm = next(Path.cwd().glob("*.src.rpm"))
    logging.info(f"Wrote: {srcrpm}")

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


class Verb(enum.Enum):
    cd = "cd"

    def __str__(self) -> str:
        return self.value

    def run(self, args: argparse.Namespace) -> None:
        {Verb.cd: do_cd}[self](args)


def main() -> None:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(LogFormatter())
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel("INFO")

    parser = argparse.ArgumentParser()

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
        "verb",
        type=Verb,
        choices=list(Verb),
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

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
