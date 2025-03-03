# systemd

This repo contains the rpm spec for the Hyperscale systemd package and various tools and utilites used for
testing and releasing it.

# CI

CI has three distinct workflows:

## Merge Request

On merge requests, CI pipelines trigger multiple children pipelines, one per
combination of `REPO` (main, facebook), `RELEASE` (9, 10), and `SOURCE` (head,
spec).  The latter is the way to test both the upstream HEAD version and the
version defined in the spec file. To make it simple: when a patch is applied,
you want to make sure that this patch works cleanly with systemd version in
systemd.spec (ex: v257.2), and to the HEAD of systemd upstream
(https://github.com/systemd/systemd).

Each child pipeline performs a scratch build (using CBS) and runs upstream
tests (using testing-farm).

## Schedule (nighly builds)

Scheduled pipeline execution happens at the configured schedule (Build ->
Pipeline schedules). The pipeline builds only HEAD versions of the systemd: one
per `REPO`, `RELEASE` (ex: systemd-258~devel-20250303020517.hs.el10). It
doesn't perform tests. It publishes RPM using the 'testing' tag, ex,
hyperscale10s-packages-main-testing.

## Manual Run (release workflow)

Manual runs primarily aim to release the official Hyperscale systemd version.

To trigger it, go to `Build -> Pipelines -> New Pipeline`. Select appropriate
values for the available variables:
- `SOURCE`: choose "spec" to build systemd version defined in systemd.spec.
- `PUBLISH`: choose "release" if you want to publish official release. Do
   'testing' or 'false' for any other testing purposes.

The pipeline kicks in with multiple child pipelines. Each does:
1. Build
2. Test
3. Publish RPM with chosen tag
4. Tag repo if $PUBLISH == 'release' for tracking
