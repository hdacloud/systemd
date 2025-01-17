# systemd

This repo contains the rpm spec for the Hyperscale systemd package and various tools and utilites used for
testing and releasing it.

# CI

On merge requests, CI pipelines run without specifying --publish to releng.py. On the main branch, CI
pipelines run with the --publish argument specified to releng.py so that results are only published on the
main branch but pipelines can still run in dry-run mode on merge requests. To make this work every script
that is used in a pipeline should run in dry-run mode by default and accept a --publish option to disable the
dry-run. Use the $PUBLISH variable in the pipeline configuration which will expand to an empty string on
merge requests and to --publish when the job is run as part of the daily scheduled pipeline in gitlab.
