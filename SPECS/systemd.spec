# PIE is broken on s390 (#868839, #872148)
%ifnarch s390 s390x
%global _hardened_build 1
%endif

# We ship a .pc file but don't want to have a dep on pkg-config. We
# strip the automatically generated dep here and instead co-own the
# directory.
%global __requires_exclude pkg-config

Name:           systemd
Url:            http://www.freedesktop.org/wiki/Software/systemd
Version:        208
Release:        12.atomic.4%{?dist}
# For a breakdown of the licensing, see README
License:        LGPLv2+ and MIT and GPLv2+
Summary:        A System and Service Manager

Source0:        http://www.freedesktop.org/software/systemd/%{name}-%{version}.tar.xz
# RHEL7 default preset policy
Source1:        99-default-disable.preset
# SysV convert script.
Source2:        systemd-sysv-convert
# Stop-gap, just to ensure things work fine with rsyslog without having to change the package right-away
Source3:        listen.conf
# Prevent accidental removal of the systemd package
Source4:        yum-protect-systemd.conf
# ship /etc/rc.d/rc.local https://bugzilla.redhat.com/show_bug.cgi?id=968401
Source5:        rc.local
#https://bugzilla.redhat.com/show_bug.cgi?id=1032711
Source6:        60-alias-kmsg.rules

# RHEL-specific:
Patch0001: 0001-units-add-Install-section-to-tmp.mount.patch
Patch0002: 0002-man-explain-NAME-in-systemctl-man-page.patch
Patch0003: 0003-fix-lingering-references-to-var-lib-backlight-random.patch
Patch0004: 0004-cryptsetup-fix-OOM-handling-when-parsing-mount-optio.patch
Patch0005: 0005-journald-add-missing-error-check.patch
Patch0006: 0006-bus-fix-potentially-uninitialized-memory-access.patch
Patch0007: 0007-dbus-fix-return-value-of-dispatch_rqueue.patch
Patch0008: 0008-modules-load-fix-error-handling.patch
Patch0009: 0009-efi-never-call-qsort-on-potentially-NULL-arrays.patch
Patch0010: 0010-strv-don-t-access-potentially-NULL-string-arrays.patch
Patch0011: 0011-mkdir-pass-a-proper-function-pointer-to-mkdir_safe_i.patch
Patch0012: 0012-tmpfiles.d-include-setgid-perms-for-run-log-journal.patch
Patch0013: 0013-gpt-auto-generator-exit-immediately-if-in-container.patch
Patch0014: 0014-systemd-order-remote-mounts-from-mountinfo-before-re.patch
Patch0015: 0015-manager-when-verifying-whether-clients-may-change-en.patch
Patch0016: 0016-mount-check-for-NULL-before-reading-pm-what.patch
Patch0017: 0017-core-do-not-add-what-to-RequiresMountsFor-for-networ.patch
Patch0018: 0018-systemd-serialize-deserialize-forbid_restart-value.patch
Patch0019: 0019-core-unify-the-way-we-denote-serialization-attribute.patch
Patch0020: 0020-journald-fix-minor-memory-leak.patch
Patch0021: 0021-journald-remove-rotated-file-from-hashmap-when-rotat.patch
Patch0022: 0022-udevadm.xml-document-resolve-names-option-for-test.patch
Patch0023: 0023-dbus-common-avoid-leak-in-error-path.patch
Patch0024: 0024-drop-ins-check-return-value.patch
Patch0025: 0025-shared-util-Fix-glob_extend-argument.patch
Patch0026: 0026-Fix-for-SIGSEGV-in-systemd-bootchart-on-short-living.patch
Patch0027: 0027-man-document-the-b-special-boot-option.patch
Patch0028: 0028-tmpfiles-log-unaccessible-FUSE-mount-points-only-as-.patch
Patch0029: 0029-shared-util-fix-off-by-one-error-in-tag_to_udev_node.patch
Patch0030: 0030-Configurable-Timeouts-Restarts-default-values.patch
Patch0031: 0031-manager-configurable-StartLimit-default-values.patch
Patch0032: 0032-sysctl-bring-back-etc-sysctl.conf.patch
Patch0033: 0033-systemd-treat-reload-failure-as-failure.patch
Patch0034: 0034-journal-when-appending-to-journal-file-allocate-larg.patch
Patch0035: 0035-journal-optimize-bisection-logic-a-bit-by-caching-th.patch
Patch0036: 0036-journal-fix-iteration-when-we-go-backwards-from-the-.patch
Patch0037: 0037-journal-allow-journal_file_copy_entry-to-work-on-non.patch
Patch0038: 0038-journal-simplify-pre-allocation-logic.patch
Patch0039: 0039-journald-mention-how-long-we-needed-to-flush-to-var-.patch
Patch0040: 0040-Never-call-qsort-on-potentially-NULL-arrays.patch
Patch0041: 0041-localed-match-converted-keymaps-before-legacy.patch
Patch0042: 0042-core-socket-fix-SO_REUSEPORT.patch
Patch0043: 0043-activate-fix-crash-when-s-is-passed.patch
Patch0044: 0044-systemd-python-fix-booted-and-add-two-functions-to-d.patch
Patch0045: 0045-util.c-check-if-return-value-from-ttyname_r-is-0-ins.patch
Patch0046: 0046-activate-mention-E-in-the-help-text.patch
Patch0047: 0047-docs-remove-unneeded-the-s-in-gudev-docs.patch
Patch0048: 0048-man-explicitly-say-when-multiple-units-can-be-specif.patch
Patch0049: 0049-util-fix-handling-of-trailing-whitespace-in-split_qu.patch
Patch0050: 0050-man-Improve-the-description-of-parameter-X-in-tmpfil.patch
Patch0051: 0051-coredumpctl-in-case-of-error-free-pattern-after-prin.patch
Patch0052: 0052-udev-net_id-Introduce-predictable-network-names-for-.patch
Patch0053: 0053-tmpfiles-don-t-allow-label_fix-to-print-ENOENT-when-.patch
Patch0054: 0054-delta-ensure-that-d_type-will-be-set-on-every-fs.patch
Patch0055: 0055-shell-completion-dump-has-moved-to-systemd-analyze.patch
Patch0056: 0056-shell-completion-remove-load-from-systemctl.patch
Patch0057: 0057-Fix-SELinux-check-for-transient-units.-1008864.patch
Patch0058: 0058-acpi-fptd-fix-memory-leak-in-acpi_get_boot_usec.patch
Patch0059: 0059-acpi-make-sure-we-never-free-an-uninitialized-pointe.patch
Patch0060: 0060-systemctl-fix-name-mangling-for-sysv-units.patch
Patch0061: 0061-execute-more-debugging-messages.patch
Patch0062: 0062-logind-fix-bus-introspection-data-for-TakeControl.patch
Patch0063: 0063-utf8-fix-utf8_is_printable.patch
Patch0064: 0064-keymap-Fix-Samsung-900X-34-C.patch
Patch0065: 0065-do-not-accept-garbage-from-acpi-firmware-performance.patch
Patch0066: 0066-login-fix-invalid-free-in-sd_session_get_vt.patch
Patch0067: 0067-login-make-sd_session_get_vt-actually-work.patch
Patch0068: 0068-Make-sure-that-we-don-t-dereference-NULL.patch
Patch0069: 0069-gitignore-ignore-clang-analyze-output.patch
Patch0070: 0070-man-add-more-markup-to-udevadm-8.patch
Patch0071: 0071-Fix-bad-assert-in-show_pid_array.patch
Patch0072: 0072-Never-call-qsort-on-potentially-NULL-arrays.patch
Patch0073: 0073-rules-expose-loop-block-devices-to-systemd.patch
Patch0074: 0074-rules-don-t-limit-some-of-the-rules-to-the-add-actio.patch
Patch0075: 0075-hwdb-update.patch
Patch0076: 0076-rules-remove-pointless-MODE-settings.patch
Patch0077: 0077-catalog-remove-links-to-non-existent-wiki-pages.patch
Patch0078: 0078-udev-builtin-path_id-add-support-for-bcma-bus.patch
Patch0079: 0079-libudev-default-log_priority-to-INFO.patch
Patch0080: 0080-nspawn-only-pass-in-slice-setting-if-it-is-set.patch
Patch0081: 0081-zsh-completion-add-systemd-run.patch
Patch0082: 0082-systemctl-fix-typo-in-help-text.patch
Patch0083: 0083-detect_virtualization-returns-NULL-pass-empty-string.patch
Patch0084: 0084-udev-builtin-keyboard-Fix-large-scan-codes-on-32-bit.patch
Patch0085: 0085-nspawn-log-out-of-memory-errors.patch
Patch0086: 0086-man-fix-typo.patch
Patch0087: 0087-man-do-not-use-term-in-para.patch
Patch0088: 0088-shutdown-trim-the-cgroup-tree-on-loop-iteration.patch
Patch0089: 0089-run-support-system-to-match-other-commands-even-if-r.patch
Patch0090: 0090-acpi-fpdt-break-on-zero-or-negative-length-read.patch
Patch0091: 0091-man-add-rationale-into-systemd-halt-8.patch
Patch0092: 0092-systemd-python-convert-keyword-value-to-string.patch
Patch0093: 0093-Make-hibernation-test-work-for-swap-files.patch
Patch0094: 0094-man-add-docs-for-sd_is_special-and-some-man-page-sym.patch
Patch0095: 0095-systemctl-return-r-instead-of-always-returning-0.patch
Patch0096: 0096-journal-fix-minor-memory-leak.patch
Patch0097: 0097-man-units-fix-installation-of-systemd-nspawn-.servic.patch
Patch0098: 0098-systemd-fix-memory-leak-in-cgroup-code.patch
Patch0099: 0099-button-don-t-exit-if-we-cannot-handle-a-button-press.patch
Patch0100: 0100-timer-properly-format-relative-timestamps-in-the-fut.patch
Patch0101: 0101-timer-consider-usec_t-1-an-invalid-timestamp.patch
Patch0102: 0102-Resolve-dev-console-to-the-active-tty-instead-of-jus.patch
Patch0103: 0103-Only-disable-output-on-console-during-boot-if-needed.patch
Patch0104: 0104-Fix-possible-lack-of-status-messages-on-shutdown-reb.patch
Patch0105: 0105-random-seed-improve-debugging-messages-a-bit.patch
Patch0106: 0106-Fix-RemainAfterExit-services-keeping-a-hold-on-conso.patch
Patch0107: 0107-keymap-Add-Toshiba-Satellite-U940.patch
Patch0108: 0108-calendar-support-yearly-and-annually-names-the-same-.patch
Patch0109: 0109-hashmap-be-a-bit-more-conservative-with-pre-allocati.patch
Patch0110: 0110-manager-don-t-do-plymouth-in-a-container.patch
Patch0111: 0111-hwdb-Update-database-of-Bluetooth-company-identifier.patch
Patch0112: 0112-automount-log-info-about-triggering-process.patch
Patch0113: 0113-hwdb-Update-database-of-Bluetooth-company-identifier.patch
Patch0114: 0114-journal-fail-silently-in-sd_j_sendv-if-journal-is-un.patch
Patch0115: 0115-Fix-memory-leak-in-stdout-journal-streams.patch
Patch0116: 0116-man-document-is-enabled-output.patch
Patch0117: 0117-hostnamed-avoid-using-NULL-in-error-path.patch
Patch0118: 0118-core-do-not-segfault-if-swap-activity-happens-when-p.patch
Patch0119: 0119-kernel-install-add-h-help.patch
Patch0120: 0120-kernel-install-fix-help-output.patch
Patch0121: 0121-man-improve-wording-and-comma-usage-in-systemd.journ.patch
Patch0122: 0122-drop-several-entries-from-kbd-model-map-whose-kbd-la.patch
Patch0123: 0123-correct-name-of-Tajik-kbd-layout-in-kbd-model-map.patch
Patch0124: 0124-hwdb-Update-database-of-Bluetooth-company-identifier.patch
Patch0125: 0125-Ensure-unit-is-journaled-for-short-lived-or-oneshot-.patch
Patch0126: 0126-core-manager-remove-infinite-loop.patch
Patch0127: 0127-util-check-for-overflow-in-greedy_realloc.patch
Patch0128: 0128-journald-use-a-bit-more-cleanup-magic.patch
Patch0129: 0129-activate-clean-up-inherited-descriptors.patch
Patch0130: 0130-man-explain-in-more-detail-how-SYSTEMD_READY-influen.patch
Patch0131: 0131-units-don-t-run-readahead-done-timers-in-containers.patch
Patch0132: 0132-nspawn-complain-and-continue-if-machine-has-same-id.patch
Patch0133: 0133-man-beef-up-ExecStart-description.patch
Patch0134: 0134-man-remove-advice-to-avoid-setting-the-same-var-more.patch
Patch0135: 0135-systemctl-add-the-plain-option-to-the-help-message.patch
Patch0136: 0136-Fix-a-few-resource-leaks-in-error-paths.patch
Patch0137: 0137-Fix-a-few-signed-unsigned-format-string-issues.patch
Patch0138: 0138-journal-file-protect-against-alloca-0.patch
Patch0139: 0139-man-describe-journalctl-show-cursor.patch
Patch0140: 0140-journal-fix-against-theoretical-undefined-behavior.patch
Patch0141: 0141-journald-downgrade-warning-message-when-dev-kmsg-doe.patch
Patch0142: 0142-journal-file.c-remove-redundant-assignment-of-variab.patch
Patch0143: 0143-login-Don-t-stop-a-running-user-manager-from-garbage.patch
Patch0144: 0144-log-when-we-log-to-dev-console-and-got-disconnected-.patch
Patch0145: 0145-loginctl-when-showing-device-tree-of-seats-with-no-d.patch
Patch0146: 0146-man-be-more-explicit-about-option-arguments-that-tak.patch
Patch0147: 0147-man-add-DOI-for-refereed-article-on-Forward-Secure-S.patch
Patch0148: 0148-keymap-Refactor-Acer-tables.patch
Patch0149: 0149-logind-remove-dead-variable.patch
Patch0150: 0150-hwdb-update.patch
Patch0151: 0151-delta-replace-readdir_r-with-readdir.patch
Patch0152: 0152-delta-fix-delta-for-drop-ins.patch
Patch0153: 0153-delta-if-prefix-is-specified-only-show-overrides-the.patch
Patch0154: 0154-man-units-tmpfiles.d-5-cleanup.patch
Patch0155: 0155-tmpfiles-introduce-the-concept-of-unsafe-operations.patch
Patch0156: 0156-sleep-config-fix-useless-check-for-swapfile-type.patch
Patch0157: 0157-man-resolve-word-omissions.patch
Patch0158: 0158-man-improvements-to-comma-placement.patch
Patch0159: 0159-man-grammar-and-wording-improvements.patch
Patch0160: 0160-man-document-fail-nofail-auto-noauto.patch
Patch0161: 0161-man-fix-description-of-is-enabled-returned-value.patch
Patch0162: 0162-man-fix-Type-reference.patch
Patch0163: 0163-man-fix-Type-reference-v2.patch
Patch0164: 0164-hwdb-Update-database-of-Bluetooth-company-identifier.patch
Patch0165: 0165-man-add-a-note-about-propagating-signals.patch
Patch0166: 0166-man-include-autoconf-snippet-in-daemon-7.patch
Patch0167: 0167-systemd-python-fix-setting-of-exception-codes.patch
Patch0168: 0168-systemd-python-fix-listen_fds-under-Python-2.patch
Patch0169: 0169-man-expand-on-some-more-subtle-points-in-systemd.soc.patch
Patch0170: 0170-tmpfiles-rename-unsafe-to-boot.patch
Patch0171: 0171-sleep-config-Dereference-pointer-before-check-for-NU.patch
Patch0172: 0172-sleep-config-fix-double-free.patch
Patch0173: 0173-core-service-check-if-mainpid-matches-only-if-it-is-.patch
Patch0174: 0174-man-typo-fix.patch
Patch0175: 0175-swap-remove-if-else-with-the-same-data-path.patch
Patch0176: 0176-hwdb-update.patch
Patch0177: 0177-journal-Add-missing-byte-order-conversions.patch
Patch0178: 0178-hwdb-change-key-mappings-for-Samsung-90X3A.patch
Patch0179: 0179-hwdb-add-Samsung-700G.patch
Patch0180: 0180-hwdb-remove-duplicate-entry-for-Samsung-700Z.patch
Patch0181: 0181-hwdb-fix-match-for-Thinkpad-X201-tablet.patch
Patch0182: 0182-keymap-Recognize-different-Toshiba-Satellite-capital.patch
Patch0183: 0183-sleep.c-fix-typo.patch
Patch0184: 0184-man-mention-which-variables-will-be-expanded-in-Exec.patch
Patch0185: 0185-hwdb-Add-support-for-Toshiba-Satellite-P75-A7200-key.patch
Patch0186: 0186-journal-fix-access-to-munmapped-memory-in-sd_journal.patch
Patch0187: 0187-gpt-auto-generator-skip-nonexistent-devices.patch
Patch0188: 0188-gpt-auto-generator-use-EBADSLT-code-when-unable-to-d.patch
Patch0189: 0189-nspawn-explicitly-terminate-machines-when-we-exit-ns.patch
Patch0190: 0190-bash-completion-journalctl-file.patch
Patch0191: 0191-journalctl-zsh-completion-fix-several-issues-in-help.patch
Patch0192: 0192-cgroup-run-PID-1-in-the-root-cgroup.patch
Patch0193: 0193-pam-retrieve-value-of-debug-param-first.patch
Patch0194: 0194-utils-silence-the-compiler-warning.patch
Patch0195: 0195-s390-getty-generator-initialize-essential-system-ter.patch
Patch0196: 0196-pam-use-correct-log-level.patch
Patch0197: 0197-pam-do-not-set-XDG_RUNTIME_DIR-unconditionally.patch
Patch0198: 0198-selinux-Don-t-attempt-to-load-policy-in-initramfs-if.patch
Patch0199: 0199-kernel-install-add-fedora-specific-callouts-to-new-k.patch
Patch0200: 0200-remove-user-.service.patch
Patch0201: 0201-Fix-bad-assert-in-show_pid_array.patch
Patch0202: 0202-mount-don-t-send-out-PropertiesChanged-message-if-ac.patch
Patch0203: 0203-udev-rules-setup-tty-permissions-and-group-for-sclp_.patch
Patch0204: 0204-cdrom_id-use-the-old-MMC-fallback.patch
Patch0205: 0205-core-introduce-new-stop-protocol-for-unit-scopes.patch
Patch0206: 0206-core-watch-SIGCHLD-more-closely-to-track-processes-o.patch
Patch0207: 0207-logind-rework-session-shutdown-logic.patch
Patch0208: 0208-logind-order-all-scopes-after-both-systemd-logind.se.patch
Patch0209: 0209-logind-given-that-we-can-now-relatively-safely-shutd.patch
Patch0210: 0210-utmp-make-sure-we-don-t-write-the-utmp-reboot-record.patch
Patch0211: 0211-rules-mark-loop-device-as-SYSTEMD_READY-0-if-no-file.patch
Patch0212: 0212-logind-fix-reference-to-systemd-user-sessions.servic.patch
Patch0213: 0213-logind-add-forgotten-call-to-user_send_changed.patch
Patch0214: 0214-logind-save-session-after-setting-the-stopping-flag.patch
Patch0215: 0215-logind-save-user-state-after-stopping-the-session.patch
Patch0216: 0216-logind-initialize-timer_fd.patch
Patch0217: 0217-service-don-t-create-extra-cgroup-for-control-proces.patch
Patch0218: 0218-logind-pass-pointer-to-User-object-to-user_save.patch
Patch0219: 0219-fstab-generator-When-parsing-the-root-cmdline-option.patch
Patch0220: 0220-gpt-auto-generator-Generate-explicit-dependencies-on.patch
Patch0221: 0221-fstab-generator-Generate-explicit-dependencies-on-sy.patch
Patch0222: 0222-fsck-root-only-run-when-requested-in-fstab.patch
Patch0223: 0223-core-allow-PIDs-to-be-watched-by-two-units-at-the-sa.patch
Patch0224: 0224-core-correctly-unregister-PIDs-from-PID-hashtables.patch
Patch0225: 0225-logind-uninitialized-timer_fd-is-set-to-1.patch
Patch0226: 0226-logind-add-forgotten-return-statement.patch
Patch0227: 0227-core-remove-extra-semicolon-and-make-gcc-shut-up.patch
Patch0228: 0228-core-fix-detection-of-dead-processes.patch
Patch0229: 0229-Fix-prototype-of-get_process_state.patch
Patch0230: 0230-core-check-for-return-value-from-get_process_state.patch
Patch0231: 0231-unit-add-waiting-jobs-to-run-queue-in-unit_coldplug.patch
Patch0232: 0232-logind-session-save-stopping-flag.patch
Patch0233: 0233-units-serial-getty-.service-add-Install-section.patch
Patch0234: 0234-units-order-network-online.target-after-network.targ.patch
Patch0235: 0235-util-consider-both-fuse.glusterfs-and-glusterfs-netw.patch
Patch0236: 0236-core-make-StopWhenUnneeded-work-in-conjunction-with-.patch
Patch0237: 0237-cgroups-agent-down-grade-log-level.patch
Patch0238: 0238-random-seed-raise-POOL_SIZE_MIN-constant-to-1024.patch
Patch0239: 0239-delta-do-not-use-unicode-chars-in-C-locale.patch
Patch0240: 0240-core-print-debug-instead-of-error-message.patch
Patch0241: 0241-journald-always-add-syslog-facility-for-messages-com.patch
Patch0242: 0242-Introduce-_cleanup_endmntent_.patch
Patch0243: 0243-Introduce-_cleanup_fdset_free_.patch
Patch0244: 0244-Introduce-udev-object-cleanup-functions.patch
Patch0245: 0245-fsck-modernization.patch
Patch0246: 0246-fsck-fstab-generator-be-lenient-about-missing-fsck.-.patch
Patch0247: 0247-rules-60-persistent-storage-add-nvme-pcie-ssd-scsi_i.patch
Patch0248: 0248-cgls-fix-running-with-M-option.patch
Patch0249: 0249-units-when-spawning-a-getty-configure-TERM-explicitl.patch
Patch0250: 0250-getty-Start-getty-on-3270-terminals-available-on-Lin.patch
Patch0251: 0251-core-Added-support-for-ERRNO-NOTIFY_SOCKET-message-p.patch
Patch0252: 0252-service-don-t-accept-negative-ERRNO-notification-mes.patch
Patch0253: 0253-socket-add-SocketUser-and-SocketGroup-for-chown-ing-.patch
Patch0254: 0254-selinux-Check-access-vector-for-enable-and-disable-p.patch
Patch0255: 0255-systemctl-show-StatusErrno-value-in-systemctl-status.patch
Patch0256: 0256-service-flush-status-text-and-errno-values-each-time.patch
Patch0257: 0257-service-don-t-free-status_text-twice.patch
Patch0258: 0258-util-add-files_same-helper-function.patch
Patch0259: 0259-systemctl-for-switch-root-check-if-we-switch-to-a-sy.patch
Patch0260: 0260-shared-include-root-when-canonicalizing-conf-paths.patch
Patch0261: 0261-shared-add-root-argument-to-search_and_fopen.patch
Patch0262: 0262-machine-id-add-root-option-to-operate-on-an-alternat.patch
Patch0263: 0263-conf-files-fix-when-for-root-logic.patch
Patch0264: 0264-Make-systemctl-root-look-for-files-in-the-proper-pla.patch
Patch0265: 0265-tmpfiles-fix-memory-leak-of-exclude_prefixes.patch
Patch0266: 0266-tmpfiles-add-root-option-to-operate-on-an-alternate-.patch
Patch0267: 0267-conf-files-include-root-in-returned-file-paths.patch
Patch0268: 0268-install-make-sure-that-root-mode-doesn-t-make-us-con.patch
Patch0269: 0269-shared-install-do-not-prefix-created-symlink-with-ro.patch
Patch0270: 0270-systemctl-fail-in-the-case-that-no-unit-files-were-f.patch
Patch0271: 0271-units-make-ExecStopPost-action-part-of-ExecStart.patch
Patch0272: 0272-systemctl-fix-broken-list-unit-files-with-root.patch
Patch0273: 0273-machine-id-only-look-into-KVM-uuid-when-we-are-not-r.patch
Patch0274: 0274-util-reset-signals-when-we-fork-off-agents.patch
Patch0275: 0275-util-fix-minimal-race-where-we-might-miss-SIGTERMs-w.patch
Patch0276: 0276-udev-do-not-skip-the-execution-of-RUN-when-renaming-.patch
Patch0277: 0277-man-mention-System-Administrator-s-Guide-in-systemct.patch
Patch0278: 0278-vconsole-also-copy-character-maps-not-just-fonts-fro.patch
Patch0279: 0279-vconsole-setup-run-setfont-before-loadkeys.patch
Patch0280: 0280-vconsole-setup-fix-inverted-error-messages.patch
Patch0281: 0281-systemd-detect-virt-detect-s390-virtualization.patch
Patch0282: 0001-systemctl-unbreak-switchroot.patch
Patch0283: 0001-systemd-detect-virt-fix-detect-s390-virtualization.patch
Patch0284: 0001-core-make-sure-to-serialize-jobs-for-all-units.patch


%global num_patches %{lua: c=0; for i,p in ipairs(patches) do c=c+1; end; print(c);}

BuildRequires:  libcap-devel
BuildRequires:  tcp_wrappers-devel
BuildRequires:  pam-devel
BuildRequires:  libselinux-devel
BuildRequires:  audit-libs-devel
BuildRequires:  cryptsetup-devel
BuildRequires:  dbus-devel
BuildRequires:  libacl-devel
BuildRequires:  pciutils-devel
BuildRequires:  glib2-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  libblkid-devel
BuildRequires:  xz-devel
BuildRequires:  kmod-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  qrencode-devel
BuildRequires:  libmicrohttpd-devel
BuildRequires:  libxslt
BuildRequires:  docbook-style-xsl
BuildRequires:  pkgconfig
BuildRequires:  intltool
BuildRequires:  gperf
BuildRequires:  gtk-doc
BuildRequires:  python2-devel
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  git

Requires(post): coreutils
Requires(post): gawk
Requires(post): sed
Requires(post): acl
Requires(pre):  coreutils
Requires(pre):  /usr/bin/getent
Requires(pre):  /usr/sbin/groupadd
Requires:       dbus
Requires:       nss-myhostname
Requires:       %{name}-libs = %{version}-%{release}
Requires:       kmod >= 14
Requires:       redhat-release >= 7.0

Provides:       /bin/systemctl
Provides:       /sbin/shutdown
Provides:       syslog
Provides:       systemd-units = %{version}-%{release}
# part of system since f18, drop at f20
Provides:       udev = %{version}
Obsoletes:      udev < 183
Conflicts:      dracut < 027
# f18 version, drop at f20
Conflicts:      plymouth < 0.8.5.1
# For the journal-gateway split in F20, drop at F22
Obsoletes:      systemd < 204-10
# Ensures correct multilib updates added F18, drop at F20
Conflicts:      systemd < 185-4
# added F18, drop at F20
Obsoletes:      system-setup-keyboard < 0.9
Provides:       system-setup-keyboard = 0.9
# nss-myhostname got integrated in F19, drop at F21
Obsoletes:      nss-myhostname < 0.4
Provides:       nss-myhostname = 0.4
# systemd-analyze got merged in F19, drop at F21
Obsoletes:      systemd-analyze < 198
Provides:       systemd-analyze = 198
Obsoletes:      upstart < 1.2-3
Obsoletes:      upstart-sysvinit < 1.2-3
Conflicts:      upstart-sysvinit
Obsoletes:      hal
Obsoletes:      ConsoleKit

%description
systemd is a system and service manager for Linux, compatible with
SysV and LSB init scripts. systemd provides aggressive parallelization
capabilities, uses socket and D-Bus activation for starting services,
offers on-demand starting of daemons, keeps track of processes using
Linux cgroups, supports snapshotting and restoring of the system
state, maintains mount and automount points and implements an
elaborate transactional dependency-based service control logic. It can
work as a drop-in replacement for sysvinit.

%package libs
Summary:        systemd libraries
License:        LGPLv2+ and MIT
Obsoletes:      libudev < 183
Obsoletes:      systemd < 185-4
Conflicts:      systemd < 185-4

%description libs
Libraries for systemd and udev, as well as the systemd PAM module.

%package devel
Summary:        Development headers for systemd
License:        LGPLv2+ and MIT
Requires:       %{name} = %{version}-%{release}
Provides:       libudev-devel = %{version}
Obsoletes:      libudev-devel < 183

%description devel
Development headers and auxiliary files for developing applications for systemd.

%package sysv
Summary:        SysV tools for systemd
License:        LGPLv2+
Requires:       %{name} = %{version}-%{release}

%description sysv
SysV compatibility tools for systemd

%package python
Summary:        Python Bindings for systemd
License:        LGPLv2+
Requires:       %{name} = %{version}-%{release}

%description python
This package contains python binds for systemd APIs

%package -n libgudev1
Summary:        Libraries for adding libudev support to applications that use glib
Conflicts:      filesystem < 3
License:        LGPLv2+
Requires:       %{name} = %{version}-%{release}

%description -n libgudev1
This package contains the libraries that make it easier to use libudev
functionality from applications that use glib.

%package -n libgudev1-devel
Summary:        Header files for adding libudev support to applications that use glib
Requires:       libgudev1 = %{version}-%{release}
License:        LGPLv2+

%description -n libgudev1-devel
This package contains the header and pkg-config files for developing
glib-based applications using libudev functionality.

%package journal-gateway
Summary:        Gateway for serving journal events over the network using HTTP
Requires:       %{name} = %{version}-%{release}
License:        LGPLv2+
Requires(pre):    /usr/bin/getent
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
# For the journal-gateway split in F20, drop at F22
Obsoletes:      systemd < 204-10

%description journal-gateway
systemd-journal-gatewayd serves journal events over the network using HTTP.

%prep
%setup -q

git init
git config user.email "systemd-maint@redhat.com"
git config user.name "Fedora systemd team"
git add .
git commit -a -q -m "%{version} baseline."

# Apply all the patches.
git am \
    --exclude .gitignore \
    --exclude docs/.gitignore \
    --exclude docs/gudev/.gitignore \
    --exclude docs/libudev/.gitignore \
    --exclude docs/sysvinit/.gitignore \
    --exclude docs/var-log/.gitignore \
    --exclude hwdb/.gitignore \
    --exclude m4/.gitignore \
    --exclude man/.gitignore \
    --exclude po/.gitignore \
    --exclude rules/.gitignore \
    --exclude src/.gitignore \
    --exclude src/analyze/.gitignore \
    --exclude src/core/.gitignore \
    --exclude src/gudev/.gitignore \
    --exclude src/hostname/.gitignore \
    --exclude src/journal/.gitignore \
    --exclude src/libsystemd-daemon/.gitignore \
    --exclude src/libsystemd-id128/.gitignore \
    --exclude src/libudev/.gitignore \
    --exclude src/locale/.gitignore \
    --exclude src/login/.gitignore \
    --exclude src/python-systemd/.gitignore \
    --exclude src/python-systemd/docs/* \
    --exclude src/timedate/.gitignore \
    --exclude src/udev/.gitignore \
    --exclude src/udev/scsi_id/.gitignore \
    --exclude sysctl.d/.gitignore \
    --exclude test/.gitignore \
    --exclude units/.gitignore \
    --exclude units/user/.gitignore \
    %{patches}


%build
autoreconf

%configure \
        --libexecdir=%{_prefix}/lib \
        --enable-gtk-doc \
        --disable-static \
        --with-sysvinit-path=/etc/rc.d/init.d \
        --with-rc-local-script-path-start=/etc/rc.d/rc.local
make %{?_smp_mflags} V=1

%install
%make_install
find %{buildroot} \( -name '*.a' -o -name '*.la' \) -delete

# udev links
mkdir -p %{buildroot}/%{_sbindir}
ln -sf ../bin/udevadm %{buildroot}%{_sbindir}/udevadm

# Create SysV compatibility symlinks. systemctl/systemd are smart
# enough to detect in which way they are called.
ln -s ../lib/systemd/systemd %{buildroot}%{_sbindir}/init
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/reboot
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/halt
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/poweroff
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/shutdown
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/telinit
ln -s ../bin/systemctl %{buildroot}%{_sbindir}/runlevel

# legacy links
ln -s loginctl %{buildroot}%{_bindir}/systemd-loginctl

# We create all wants links manually at installation time to make sure
# they are not owned and hence overriden by rpm after the used deleted
# them.
rm -r %{buildroot}%{_sysconfdir}/systemd/system/*.target.wants

# Make sure the ghost-ing below works
touch %{buildroot}%{_sysconfdir}/systemd/system/runlevel2.target
touch %{buildroot}%{_sysconfdir}/systemd/system/runlevel3.target
touch %{buildroot}%{_sysconfdir}/systemd/system/runlevel4.target
touch %{buildroot}%{_sysconfdir}/systemd/system/runlevel5.target

# Make sure these directories are properly owned
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/basic.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/default.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/dbus.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/syslog.target.wants

# Make sure the user generators dir exists too
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-generators
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user-generators

# Create new-style configuration files so that we can ghost-own them
touch %{buildroot}%{_sysconfdir}/hostname
touch %{buildroot}%{_sysconfdir}/vconsole.conf
touch %{buildroot}%{_sysconfdir}/locale.conf
touch %{buildroot}%{_sysconfdir}/machine-id
touch %{buildroot}%{_sysconfdir}/machine-info
touch %{buildroot}%{_sysconfdir}/localtime
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/00-keyboard.conf

# Install default preset policy
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user-preset/
install -m 0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/systemd/system-preset/

# Make sure the shutdown/sleep drop-in dirs exist
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-shutdown/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-sleep/

# Make sure the NTP units dir exists
mkdir -p %{buildroot}%{_prefix}/lib/systemd/ntp-units.d/

# Make sure directories in /var exist
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/coredump
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/catalog
touch %{buildroot}%{_localstatedir}/lib/systemd/catalog/database
touch %{buildroot}%{_sysconfdir}/udev/hwdb.bin

# Install SysV conversion tool for systemd
install -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/

# Install rsyslog fragment
mkdir -p %{buildroot}%{_sysconfdir}/rsyslog.d/
install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/rsyslog.d/

# Install yum protection fragment
mkdir -p %{buildroot}%{_sysconfdir}/yum/protected.d/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/yum/protected.d/systemd.conf

# Install rc.local
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/rc.d/rc.local
ln -s rc.d/rc.local %{buildroot}%{_sysconfdir}/rc.local

# To avoid making life hard for Rawhide-using developers, don't package the
# kernel.core_pattern setting until systemd-coredump is a part of an actual
# systemd release and it's made clear how to get the core dumps out of the
# journal.
rm -f %{buildroot}%{_prefix}/lib/sysctl.d/50-coredump.conf

# For now remove /var/log/README since we are not enabling persistant
# logging yet.
rm -f %{buildroot}%{_localstatedir}/log/README

# No tmp-on-tmpfs by default in RHEL7. bz#876122
rm -f %{buildroot}%{_prefix}/lib/systemd/system/local-fs.target.wants/tmp.mount

# No gpt-auto-generator in RHEL7
rm -f %{buildroot}%{_prefix}/lib/systemd/system-generators/systemd-gpt-auto-generator

install -m 0644 %{SOURCE6} $RPM_BUILD_ROOT/%{_udevrulesdir}/

%pre
getent group cdrom >/dev/null 2>&1 || groupadd -r -g 11 cdrom >/dev/null 2>&1 || :
getent group tape >/dev/null 2>&1 || groupadd -r -g 33 tape >/dev/null 2>&1 || :
getent group dialout >/dev/null 2>&1 || groupadd -r -g 18 dialout >/dev/null 2>&1 || :
getent group floppy >/dev/null 2>&1 || groupadd -r -g 19 floppy >/dev/null 2>&1 || :
getent group systemd-journal >/dev/null 2>&1 || groupadd -r -g 190 systemd-journal 2>&1 || :

systemctl stop systemd-udevd-control.socket systemd-udevd-kernel.socket systemd-udevd.service >/dev/null 2>&1 || :

# Rename configuration files that changed their names
mv -n %{_sysconfdir}/systemd/systemd-logind.conf %{_sysconfdir}/systemd/logind.conf >/dev/null 2>&1 || :
mv -n %{_sysconfdir}/systemd/systemd-journald.conf %{_sysconfdir}/systemd/journald.conf >/dev/null 2>&1 || :

%pretrans -p <lua>
--# Migrate away from systemd-timedated-ntp.target.
--# Take note which ntp services, if any, were pulled in by it.
--# We'll enable them the usual way in %%post.
--# Remove this after upgrades from F17 are no longer supported.
function migrate_ntp()
    --# Are we upgrading from a version that had systemd-timedated-ntp.target?
    t = posix.stat("/usr/lib/systemd/system/systemd-timedated-ntp.target", "type")
    if t ~= "regular" then return end

    --# Was the target enabled?
    t = posix.stat("/etc/systemd/system/multi-user.target.wants/systemd-timedated-ntp.target", "type")
    if t ~= "link" then return end

    --# filesystem provides /var/lib/rpm-state since F17 GA
    r,msg,errno = posix.mkdir("/var/lib/rpm-state/systemd")
    if r == nil and errno ~= 17 then return end  --# EEXIST is fine.

    --# Save the list of ntp services pulled by the target.
    f = io.open("/var/lib/rpm-state/systemd/ntp-units", "w")
    if f == nil then return end

    files = posix.dir("/usr/lib/systemd/system/systemd-timedated-ntp.target.wants")
    for i,name in ipairs(files) do
        if name ~= "." and name ~= ".." then
            s = string.format("%s\n", name)
            f:write(s)
        end
    end

    f:close()
end

migrate_ntp()
return 0

%post
systemd-machine-id-setup >/dev/null 2>&1 || :
/usr/lib/systemd/systemd-random-seed save >/dev/null 2>&1 || :
systemctl daemon-reexec >/dev/null 2>&1 || :
systemctl start systemd-udevd.service >/dev/null 2>&1 || :
udevadm hwdb --update >/dev/null 2>&1 || :
journalctl --update-catalog >/dev/null 2>&1 || :
systemd-tmpfiles --create >/dev/null 2>&1 || :

if [ $1 -eq 1 ] ; then
        # Try to read default runlevel from the old inittab if it exists
        runlevel=$(awk -F ':' '$3 == "initdefault" && $1 !~ "^#" { print $2 }' /etc/inittab 2> /dev/null)
        if [ -z "$runlevel" ] ; then
                target="/usr/lib/systemd/system/graphical.target"
        else
                target="/usr/lib/systemd/system/runlevel$runlevel.target"
        fi

        # And symlink what we found to the new-style default.target
        ln -sf "$target" /etc/systemd/system/default.target >/dev/null 2>&1 || :

        # Services we install by default, and which are controlled by presets.
        systemctl preset \
                getty@tty1.service \
                remote-fs.target \
                systemd-readahead-replay.service \
                systemd-readahead-collect.service >/dev/null 2>&1 || :
else
        # This systemd service does not exist anymore, we now do it
        # internally in PID 1
        rm -f /etc/systemd/system/sysinit.target.wants/hwclock-load.service >/dev/null 2>&1 || :

        # This systemd target does not exist anymore. It's been replaced
        # by ntp-units.d.
        rm -f /etc/systemd/system/multi-user.target.wants/systemd-timedated-ntp.target >/dev/null 2>&1 || :

        # Enable the units recorded by %%pretrans
        if [ -e /var/lib/rpm-state/systemd/ntp-units ] ; then
                while read service; do
                        systemctl enable "$service" >/dev/null 2>&1 || :
                done < /var/lib/rpm-state/systemd/ntp-units
                rm -r /var/lib/rpm-state/systemd/ntp-units >/dev/null 2>&1 || :
        fi
fi

# Migrate /etc/sysconfig/clock
if [ ! -L /etc/localtime -a -e /etc/sysconfig/clock ] ; then
       . /etc/sysconfig/clock >/dev/null 2>&1 || :
       if [ -n "$ZONE" -a -e "/usr/share/zoneinfo/$ZONE" ] ; then
              ln -sf "../usr/share/zoneinfo/$ZONE" /etc/localtime >/dev/null 2>&1 || :
       fi
fi
rm -f /etc/sysconfig/clock >/dev/null 2>&1 || :

# Migrate /etc/sysconfig/i18n
if [ -e /etc/sysconfig/i18n -a ! -e /etc/locale.conf ]; then
        unset LANG
        unset LC_CTYPE
        unset LC_NUMERIC
        unset LC_TIME
        unset LC_COLLATE
        unset LC_MONETARY
        unset LC_MESSAGES
        unset LC_PAPER
        unset LC_NAME
        unset LC_ADDRESS
        unset LC_TELEPHONE
        unset LC_MEASUREMENT
        unset LC_IDENTIFICATION
        . /etc/sysconfig/i18n >/dev/null 2>&1 || :
        [ -n "$LANG" ] && echo LANG=$LANG > /etc/locale.conf 2>&1 || :
        [ -n "$LC_CTYPE" ] && echo LC_CTYPE=$LC_CTYPE >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_NUMERIC" ] && echo LC_NUMERIC=$LC_NUMERIC >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_TIME" ] && echo LC_TIME=$LC_TIME >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_COLLATE" ] && echo LC_COLLATE=$LC_COLLATE >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_MONETARY" ] && echo LC_MONETARY=$LC_MONETARY >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_MESSAGES" ] && echo LC_MESSAGES=$LC_MESSAGES >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_PAPER" ] && echo LC_PAPER=$LC_PAPER >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_NAME" ] && echo LC_NAME=$LC_NAME >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_ADDRESS" ] && echo LC_ADDRESS=$LC_ADDRESS >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_TELEPHONE" ] && echo LC_TELEPHONE=$LC_TELEPHONE >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_MEASUREMENT" ] && echo LC_MEASUREMENT=$LC_MEASUREMENT >> /etc/locale.conf 2>&1 || :
        [ -n "$LC_IDENTIFICATION" ] && echo LC_IDENTIFICATION=$LC_IDENTIFICATION >> /etc/locale.conf 2>&1 || :
fi

# Migrate /etc/sysconfig/keyboard
if [ -e /etc/sysconfig/keyboard -a ! -e /etc/vconsole.conf ]; then
        unset SYSFONT
        unset SYSFONTACM
        unset UNIMAP
        unset KEYMAP
        [ -e /etc/sysconfig/i18n ] && . /etc/sysconfig/i18n >/dev/null 2>&1 || :
        . /etc/sysconfig/keyboard >/dev/null 2>&1 || :
        [ -n "$SYSFONT" ] && echo FONT=$SYSFONT > /etc/vconsole.conf 2>&1 || :
        [ -n "$SYSFONTACM" ] && echo FONT_MAP=$SYSFONTACM >> /etc/vconsole.conf 2>&1 || :
        [ -n "$UNIMAP" ] && echo FONT_UNIMAP=$UNIMAP >> /etc/vconsole.conf 2>&1 || :
        [ -n "$KEYTABLE" ] && echo KEYMAP=$KEYTABLE >> /etc/vconsole.conf 2>&1 || :
fi
rm -f /etc/sysconfig/i18n >/dev/null 2>&1 || :
rm -f /etc/sysconfig/keyboard >/dev/null 2>&1 || :

# Migrate HOSTNAME= from /etc/sysconfig/network
if [ -e /etc/sysconfig/network -a ! -e /etc/hostname ]; then
        unset HOSTNAME
        . /etc/sysconfig/network >/dev/null 2>&1 || :
        [ -n "$HOSTNAME" ] && echo $HOSTNAME > /etc/hostname 2>&1 || :
fi
sed -i '/^HOSTNAME=/d' /etc/sysconfig/network >/dev/null 2>&1 || :

# Migrate the old systemd-setup-keyboard X11 configuration fragment
if [ ! -e /etc/X11/xorg.conf.d/00-keyboard.conf ] ; then
        mv /etc/X11/xorg.conf.d/00-system-setup-keyboard.conf /etc/X11/xorg.conf.d/00-keyboard.conf >/dev/null 2>&1 || :
else
        rm -f /etc/X11/xorg.conf.d/00-system-setup-keyboard.conf >/dev/null 2>&1 || :
fi

# sed-fu to add myhostname to the hosts line of /etc/nsswitch.conf
if [ -f /etc/nsswitch.conf ] ; then
        sed -i.bak -e '
                /^hosts:/ !b
                /\<myhostname\>/ b
                s/[[:blank:]]*$/ myhostname/
                ' /etc/nsswitch.conf >/dev/null 2>&1 || :
fi

%posttrans
# Convert old /etc/sysconfig/desktop settings
preferred=
if [ -f /etc/sysconfig/desktop ]; then
        . /etc/sysconfig/desktop
        if [ "$DISPLAYMANAGER" = GNOME ]; then
                preferred=gdm
        elif [ "$DISPLAYMANAGER" = KDE ]; then
                preferred=kdm
        elif [ "$DISPLAYMANAGER" = WDM ]; then
                preferred=wdm
        elif [ "$DISPLAYMANAGER" = XDM ]; then
                preferred=xdm
        elif [ -n "$DISPLAYMANAGER" ]; then
                preferred=${DISPLAYMANAGER##*/}
        fi
fi
if [ -z "$preferred" ]; then
        if [ -x /usr/sbin/gdm ]; then
                preferred=gdm
        elif [ -x /usr/bin/kdm ]; then
                preferred=kdm
        fi
fi
if [ -n "$preferred" -a -r "/usr/lib/systemd/system/$preferred.service" ]; then
        # This is supposed to fail when the symlink already exists
        ln -s "/usr/lib/systemd/system/$preferred.service" /etc/systemd/system/display-manager.service >/dev/null 2>&1 || :
fi

%postun
if [ $1 -ge 1 ] ; then
        systemctl daemon-reload > /dev/null 2>&1 || :
        systemctl try-restart systemd-logind.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
        systemctl disable \
                getty@.service \
                remote-fs.target \
                systemd-readahead-replay.service \
                systemd-readahead-collect.service >/dev/null 2>&1 || :

        rm -f /etc/systemd/system/default.target >/dev/null 2>&1 || :

        if [ -f /etc/nsswitch.conf ] ; then
                sed -i.bak -e '
                        /^hosts:/ !b
                        s/[[:blank:]]\+myhostname\>//
                        ' /etc/nsswitch.conf >/dev/null 2>&1 || :
        fi
fi

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%post -n libgudev1 -p /sbin/ldconfig
%postun -n libgudev1 -p /sbin/ldconfig

%pre journal-gateway
getent group systemd-journal-gateway >/dev/null 2>&1 || groupadd -r -g 191 systemd-journal-gateway 2>&1 || :
getent passwd systemd-journal-gateway >/dev/null 2>&1 || useradd -r -l -u 191 -g systemd-journal-gateway -d %{_prefix}/lib/systemd -s /sbin/nologin -c "Journal Gateway" systemd-journal-gateway >/dev/null 2>&1 || :

%post journal-gateway
%systemd_post systemd-journal-gatewayd.socket systemd-journal-gatewayd.service

%preun journal-gateway
%systemd_preun systemd-journal-gatewayd.socket systemd-journal-gatewayd.service

%postun journal-gateway
%systemd_postun_with_restart systemd-journal-gatewayd.service

%files
%doc %{_docdir}/systemd
%dir %{_sysconfdir}/systemd
%dir %{_sysconfdir}/systemd/system
%dir %{_sysconfdir}/systemd/user
%dir %{_sysconfdir}/tmpfiles.d
%dir %{_sysconfdir}/sysctl.d
%dir %{_sysconfdir}/modules-load.d
%dir %{_sysconfdir}/binfmt.d
%dir %{_sysconfdir}/udev
%dir %{_sysconfdir}/udev/rules.d
%dir %{_prefix}/lib/systemd
%dir %{_prefix}/lib/systemd/system-generators
%dir %{_prefix}/lib/systemd/user-generators
%dir %{_prefix}/lib/systemd/system-preset
%dir %{_prefix}/lib/systemd/user-preset
%dir %{_prefix}/lib/systemd/system-shutdown
%dir %{_prefix}/lib/systemd/system-sleep
%dir %{_prefix}/lib/systemd/catalog
%dir %{_prefix}/lib/systemd/ntp-units.d
%dir %{_prefix}/lib/tmpfiles.d
%dir %{_prefix}/lib/sysctl.d
%dir %{_prefix}/lib/modules-load.d
%dir %{_prefix}/lib/binfmt.d
%dir %{_datadir}/systemd
%dir %{_datadir}/pkgconfig
%dir %{_localstatedir}/lib/systemd
%dir %{_localstatedir}/lib/systemd/catalog
%dir %{_localstatedir}/lib/systemd/coredump
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.locale1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.timedate1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.machine1.conf
%config(noreplace) %{_sysconfdir}/systemd/system.conf
%config(noreplace) %{_sysconfdir}/systemd/user.conf
%config(noreplace) %{_sysconfdir}/systemd/logind.conf
%config(noreplace) %{_sysconfdir}/systemd/journald.conf
%config(noreplace) %{_sysconfdir}/systemd/bootchart.conf
%config(noreplace) %{_sysconfdir}/udev/udev.conf
%config(noreplace) %{_sysconfdir}/rsyslog.d/listen.conf
%config(noreplace) %{_sysconfdir}/yum/protected.d/systemd.conf
%config(noreplace) %{_sysconfdir}/pam.d/systemd-user
%ghost %{_sysconfdir}/udev/hwdb.bin
%{_rpmconfigdir}/macros.d/macros.systemd
%{_sysconfdir}/xdg/systemd
%{_sysconfdir}/rc.d/init.d/README
%ghost %config(noreplace) %{_sysconfdir}/hostname
%ghost %config(noreplace) %{_sysconfdir}/localtime
%ghost %config(noreplace) %{_sysconfdir}/vconsole.conf
%ghost %config(noreplace) %{_sysconfdir}/locale.conf
%ghost %config(noreplace) %{_sysconfdir}/machine-id
%ghost %config(noreplace) %{_sysconfdir}/machine-info
%ghost %config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/00-keyboard.conf
%ghost %config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/00-system-setup-keyboard.conf
%ghost %{_localstatedir}/lib/systemd/catalog/database
%{_bindir}/systemctl
%{_bindir}/systemd-notify
%{_bindir}/systemd-analyze
%{_bindir}/systemd-ask-password
%{_bindir}/systemd-tty-ask-password-agent
%{_bindir}/systemd-machine-id-setup
%{_bindir}/loginctl
%{_bindir}/systemd-loginctl
%{_bindir}/journalctl
%{_bindir}/machinectl
%{_bindir}/systemd-tmpfiles
%{_bindir}/systemd-nspawn
%{_bindir}/systemd-stdio-bridge
%{_bindir}/systemd-cat
%{_bindir}/systemd-cgls
%{_bindir}/systemd-cgtop
%{_bindir}/systemd-delta
%{_bindir}/systemd-run
%caps(cap_dac_override,cap_sys_ptrace=pe) %{_bindir}/systemd-detect-virt
%{_bindir}/systemd-inhibit
%{_bindir}/hostnamectl
%{_bindir}/localectl
%{_bindir}/timedatectl
%{_bindir}/bootctl
%{_bindir}/systemd-coredumpctl
%{_bindir}/udevadm
%{_bindir}/kernel-install
%{_prefix}/lib/systemd/systemd
%exclude %{_prefix}/lib/systemd/system/systemd-journal-gatewayd.*
%{_prefix}/lib/systemd/system
%{_prefix}/lib/systemd/user
%exclude %{_prefix}/lib/systemd/systemd-journal-gatewayd
%{_prefix}/lib/systemd/systemd-*
%{_prefix}/lib/udev
%{_prefix}/lib/systemd/system-generators/systemd-cryptsetup-generator
%{_prefix}/lib/systemd/system-generators/systemd-getty-generator
%{_prefix}/lib/systemd/system-generators/systemd-rc-local-generator
%{_prefix}/lib/systemd/system-generators/systemd-fstab-generator
%{_prefix}/lib/systemd/system-generators/systemd-system-update-generator
%{_prefix}/lib/systemd/system-generators/systemd-efi-boot-generator
%{_prefix}/lib/tmpfiles.d/systemd.conf
%{_prefix}/lib/tmpfiles.d/x11.conf
%{_prefix}/lib/tmpfiles.d/legacy.conf
%{_prefix}/lib/tmpfiles.d/tmp.conf
%{_prefix}/lib/tmpfiles.d/systemd-nologin.conf
%{_prefix}/lib/sysctl.d/50-default.conf
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset
%{_prefix}/lib/systemd/catalog/systemd.catalog
%{_prefix}/lib/kernel/install.d/50-depmod.install
%{_prefix}/lib/kernel/install.d/90-loaderentry.install
%{_sbindir}/init
%{_sbindir}/reboot
%{_sbindir}/halt
%{_sbindir}/poweroff
%{_sbindir}/shutdown
%{_sbindir}/telinit
%{_sbindir}/runlevel
%{_sbindir}/udevadm
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man7/*
%exclude %{_mandir}/man8/systemd-journal-gatewayd.*
%{_mandir}/man8/*
%{_datadir}/systemd/kbd-model-map
%{_datadir}/dbus-1/services/org.freedesktop.systemd1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.systemd1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.locale1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.timedate1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.machine1.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.systemd1.*.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.hostname1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.locale1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.timedate1.xml
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.locale1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.timedate1.policy
%{_datadir}/pkgconfig/systemd.pc
%{_datadir}/pkgconfig/udev.pc
%{_datadir}/bash-completion/completions/hostnamectl
%{_datadir}/bash-completion/completions/journalctl
%{_datadir}/bash-completion/completions/localectl
%{_datadir}/bash-completion/completions/loginctl
%{_datadir}/bash-completion/completions/systemctl
%{_datadir}/bash-completion/completions/systemd-coredumpctl
%{_datadir}/bash-completion/completions/timedatectl
%{_datadir}/bash-completion/completions/udevadm
%{_datadir}/bash-completion/completions/systemd-analyze
%{_datadir}/bash-completion/completions/kernel-install
%{_datadir}/bash-completion/completions/systemd-run
%{_datadir}/zsh/site-functions/*
%ghost %{_localstatedir}/lib/random-seed
%ghost %dir %{_localstatedir}/var/lib/systemd/
%ghost %dir %{_localstatedir}/var/lib/systemd/coredump
%ghost %dir %{_localstatedir}/var/lib/systemd/catalog
%ghost %{_localstatedir}/var/lib/systemd/catalog/database
%ghost %dir %{_localstatedir}/var/lib/backlight/
%config(noreplace) %{_sysconfdir}/rc.d/rc.local
%{_sysconfdir}/rc.local

# Make sure we don't remove runlevel targets from F14 alpha installs,
# but make sure we don't create then anew.
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel2.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel3.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel4.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel5.target

%files libs
%{_libdir}/security/pam_systemd.so
%{_libdir}/libnss_myhostname.so.2
%{_libdir}/libsystemd-daemon.so.*
%{_libdir}/libsystemd-login.so.*
%{_libdir}/libsystemd-journal.so.*
%{_libdir}/libsystemd-id128.so.*
%{_libdir}/libudev.so.*

%files devel
%dir %{_includedir}/systemd
%{_libdir}/libsystemd-daemon.so
%{_libdir}/libsystemd-login.so
%{_libdir}/libsystemd-journal.so
%{_libdir}/libsystemd-id128.so
%{_libdir}/libudev.so
%{_includedir}/systemd/sd-daemon.h
%{_includedir}/systemd/sd-login.h
%{_includedir}/systemd/sd-journal.h
%{_includedir}/systemd/sd-id128.h
%{_includedir}/systemd/sd-messages.h
%{_includedir}/systemd/sd-shutdown.h
%{_includedir}/libudev.h
%{_libdir}/pkgconfig/libsystemd-daemon.pc
%{_libdir}/pkgconfig/libsystemd-login.pc
%{_libdir}/pkgconfig/libsystemd-journal.pc
%{_libdir}/pkgconfig/libsystemd-id128.pc
%{_libdir}/pkgconfig/libudev.pc
%{_mandir}/man3/*
%dir %{_datadir}/gtk-doc/html/libudev
%{_datadir}/gtk-doc/html/libudev/*

%files sysv
%{_bindir}/systemd-sysv-convert

%files python
%{python_sitearch}/systemd/__init__.py
%{python_sitearch}/systemd/__init__.pyc
%{python_sitearch}/systemd/__init__.pyo
%{python_sitearch}/systemd/_journal.so
%{python_sitearch}/systemd/_reader.so
%{python_sitearch}/systemd/_daemon.so
%{python_sitearch}/systemd/id128.so
%{python_sitearch}/systemd/login.so
%{python_sitearch}/systemd/journal.py
%{python_sitearch}/systemd/journal.pyc
%{python_sitearch}/systemd/journal.pyo
%{python_sitearch}/systemd/daemon.py
%{python_sitearch}/systemd/daemon.pyc
%{python_sitearch}/systemd/daemon.pyo

%files -n libgudev1
%{_libdir}/libgudev-1.0.so.*
%{_libdir}/girepository-1.0/GUdev-1.0.typelib

%files -n libgudev1-devel
%{_libdir}/libgudev-1.0.so
%dir %{_includedir}/gudev-1.0
%dir %{_includedir}/gudev-1.0/gudev
%{_includedir}/gudev-1.0/gudev/*.h
%{_datadir}/gir-1.0/GUdev-1.0.gir
%dir %{_datadir}/gtk-doc/html/gudev
%{_datadir}/gtk-doc/html/gudev/*
%{_libdir}/pkgconfig/gudev-1.0*

%files journal-gateway
%{_prefix}/lib/systemd/system/systemd-journal-gatewayd.*
%{_prefix}/lib/systemd/systemd-journal-gatewayd
%{_mandir}/man8/systemd-journal-gatewayd.*
%{_datadir}/systemd/gatewayd

%changelog
* Fri Sep 12 2014 Lukas Nykryn <lnykryn@redhat.com> - 208-11.1.5
- units/serial-getty@.service: add [Install] section (#1083936)
- units: order network-online.target after network.target (#1072431)
- util: consider both fuse.glusterfs and glusterfs network file systems (#1080229)
- core: make StopWhenUnneeded work in conjunction with units that fail during their start job (#986949)
- cgroups-agent: down-grade log level (#1044386)
- random-seed: raise POOL_SIZE_MIN constant to 1024 (#1066517)
- delta: do not use unicode chars in C locale (#1088419)
- core: print debug instead of error message (#1105608)
- journald: always add syslog facility for messages coming from kmsg (#1113215)
- fsck,fstab-generator: be lenient about missing fsck.<type> (#1098310)
- rules/60-persistent-storage: add nvme pcie ssd scsi_id ENV (#1042990)
- cgls: fix running with -M option (#1085455)
- getty: Start getty on 3270 terminals available on Linux on System z (#1075729)
- core: Added support for ERRNO NOTIFY_SOCKET  message parsing (#1106457)
- socket: add SocketUser= and SocketGroup= for chown()ing sockets in the file system (#1111761)
- tmpfiles: add --root option to operate on an alternate fs tree (#1111199)
- units: make ExecStopPost action part of ExecStart (#1036276)
- machine-id: only look into KVM uuid when we are not running in a container (#1123452)
- util: reset signals when we fork off agents (#1134818)
- udev: do not skip the execution of RUN when renaming a network device fails (#1102135)
- man: mention System Administrator's Guide in systemctl manpage (#978948)
- vconsole: also copy character maps (not just fonts) from vt1 to vt2, vt3, ... (#1002450)
- systemd-detect-virt: detect s390 virtualization (#1139149)

* Wed Apr 02 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-11
- logind-session: save stopping flag (#1082692)
- unit: add waiting jobs to run queue in unit_coldplug (#1083159)

* Fri Mar 28 2014 Harald Hoyer <harald@redhat.com> 208-10
- require redhat-release >= 7.0
Resolves: rhbz#1070114

* Fri Mar 14 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-9
- fixes crashes in logind and systemd (#1073994)
- run fsck before mouting root in initramfs (#1056661)

* Thu Mar 06 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-8
- rules: mark loop device as SYSTEMD_READY=0 if no file is attached (#1067422)
- utmp: make sure we don't write the utmp reboot record twice on each boot (#1053600)
- rework session shutdown logic (#1047614)
- introduce new stop protocol for unit scopes (#1064976)

* Wed Mar 05 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-7
- setup tty permissions and group for /dev/sclp_line0 (#1070310)
- cdrom_id: use the old MMC fallback (#1038015)
- mount: don't send out PropertiesChanged message if actually nothing got changed (#1069718)

* Wed Feb 26 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-6
- fix boot if SELINUX=permissive in configuration file and trying to boot in enforcing=1 (#907841)

* Tue Feb 25 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-5
- reintroduce 60-alias-kmsg.rules (#1032711)

* Mon Feb 17 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-4
- fstab-generator: revert wrongly applied patch

* Fri Feb 14 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 208-3
- dbus-manager: fix selinux check for enable/disable

* Wed Feb 12 2014 Michal Sekletar <msekleta@redhat.com> - 208-2
- require redhat-release package
- call systemd-tmpfiles after package installation (#1059345)
- move preset policy out of systemd package (#903690)

* Tue Feb 11 2014 Michal Sekletar <msekleta@redhat.com> - 208-1
- rebase to systemd-208 (#1063332)
- do not create symlink /etc/systemd/system/syslog.service (#1055421)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 207-14
- Mass rebuild 2014-01-24

* Thu Jan 16 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 207-13
- fix SELinux check for transient units (#1008864)

* Wed Jan 15 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 207-12
- shell-completion: remove load and dump from systemctl (#1048066)
- delta: ensure that d_type will be set on every fs (#1050795)
- tmpfiles: don't allow label_fix to print ENOENT when we want to ignore it (#1044871)
- udev/net_id: Introduce predictable network names for Linux on System z (#870859)
- coredumpctl: in case of error free pattern after print (#1052786)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 207-11
- Mass rebuild 2013-12-27

* Thu Dec 19 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-10
- cgroup_show: don't call show_pid_array on empty arrays

* Wed Dec 18 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-9
- treat reload failure as failure (#1036848)
- improve journal performance (#1029604)
- backport bugfixes (#1043525)
- fix handling of trailing whitespace in split_quoted (#984832)
- localed: match converted keymaps before legacy (#903776)
- improve the description of parameter X in tmpfiles.d page (#1029604)
- obsolete ConsoleKit (#1039761)
- make rc.local more backward comaptible (#1039465)

* Tue Nov 19 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-8
- tmpfiles: introduce m (#1030961)

* Tue Nov 12 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-7
- introduce DefaultStartLimit (#821723)

* Mon Nov 11 2013 Harald Hoyer <harald@redhat.com> 207-6
- changed systemd-journal-gateway login shell to /sbin/nologin
- backported a lot of bugfixes
- udev: path_id - fix by-path link generation for scm devices
Resolves: rhbz#888707

* Tue Nov 05 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-5
- create /etc/rc.d/rc.local (#968401)
- cgroup: always enable memory.use_hierarchy= for all cgroups (#1011575)
- remove user@.service (#1019738)
- drop some out-of-date references to cgroup settings (#1000004)
- explain NAME in systemctl man page (#978954)

* Tue Oct 15 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-4
- core: whenever a new PID is passed to us, make sure we watch it

* Tue Oct 01 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-3
- presets: add tuned.service

* Thu Sep 19 2013 Lukas Nykryn <lnykryn@redhat.com> - 207-2
- Advertise hibernation only if there's enough free swap
- swap: create .wants symlink to 'auto' swap devices
- Verify validity of session name when received from outside
- polkit: Avoid race condition in scraping /proc
Resolves: rhbz#1005142

* Fri Sep 13 2013 Harald Hoyer <harald@redhat.com> 207-1
- version 207

* Fri Sep 06 2013 Harald Hoyer <harald@redhat.com> 206-8
- support "debug" kernel command line parameter
- journald: fix fd leak in journal_file_empty
- journald: fix vacuuming of archived journals
- libudev: enumerate - do not try to match against an empty subsystem
- cgtop: fixup the online help
- libudev: fix memleak when enumerating childs

* Wed Aug 28 2013 Harald Hoyer <harald@redhat.com> 206-7
- fixed cgroup hashmap corruption
Resolves: rhbz#997742 rhbz#995197

* Fri Aug 23 2013 Harald Hoyer <harald@redhat.com> 206-6
- cgroup.c: check return value of unit_realize_cgroup_now()
Resolves: rhbz#997742 rhbz#995197

* Thu Aug 22 2013 Harald Hoyer <harald@redhat.com> 206-5
- obsolete upstart
Resolves: rhbz#978014
- obsolete hal
Resolves: rhbz#975589
- service: always unwatch PIDs before forgetting old ones
Resolves: rhbz#995197
- units: disable kmod-static-nodes.service in containers
- use CAP_MKNOD ConditionCapability
- fstab-generator: read rd.fstab=on/off switch correctly
- backlight: add minimal tool to save/restore screen brightness
- backlight: instead of syspath use sysname for identifying
- sysctl: allow overwriting of values specified in "later"
- systemd-python: fix initialization of _Reader objects
- udevd: simplify sigterm check
- libudev: fix hwdb validation to look for the *new* file
- units: make fsck units remain after exit
- udev: replace CAP_MKNOD by writable /sys condition
- libudev-enumerate.c:udev_enumerate_get_list_entry() fixed
- journal: fix parsing of facility in syslog messages

* Fri Aug 09 2013 Harald Hoyer <harald@redhat.com> 206-4
- journal: handle multiline syslog messages
- man: Fix copy&paste error
- core: synchronously block when logging
- journal: immediately sync to disk as soon as we receieve an EMERG/ALERT/CRIT message
- initctl: use irreversible jobs when switching runlevels
- udev: log error if chmod/chown of static dev nodes fails
- udev: static_node - don't touch permissions uneccessarily
- tmpfiles: support passing --prefix multiple times
- tmpfiles: introduce --exclude-prefix
- tmpfiles-setup: exclude /dev prefixes files
- logind: update state file after generating the session fifo, not before
- journalctl: use _COMM= match for scripts
- man: systemd.unit: fix volatile path
- man: link up scope+slice units from systemd.unit(5)
- man: there is no session mode, only user mode
- journal: fix hashmap leak in mmap-cache
- systemd-delta: Only print colors when on a tty
- systemd: fix segv in snapshot creation
- udev: hwdb - try reading modalias for usb before falling back to the composed one
- udevd: respect the log-level set in /etc/udev/udev.conf
- fstab-generator: respect noauto/nofail when adding sysroot mount

* Fri Aug 02 2013 Lukáš Nykrýn <lnykryn@redhat.com> - 206-3
- add dependency on kmod >= 14
- remove /var/log/journal to make journal non-persistant (#989750)
- add hypervkvpd.service to presets (#924321)

* Thu Aug 01 2013 Lukáš Nykrýn <lnykryn@redhat.com> - 206-2
- 80-net-name-slot.rules: only rename network interfaces on ACTION==add

* Tue Jul 23 2013 Kay Sievers <kay@redhat.com> - 206-1
- New upstream release
  Resolves (#984152)

* Wed Jul  3 2013 Lennart Poettering <lpoetter@redhat.com> - 205-1
- New upstream release

* Wed Jun 26 2013 Michal Schmidt <mschmidt@redhat.com> 204-10
- Split systemd-journal-gateway subpackage (#908081).

* Mon Jun 24 2013 Michal Schmidt <mschmidt@redhat.com> 204-9
- Rename nm_dispatcher to NetworkManager-dispatcher in default preset (#977433)

* Fri Jun 14 2013 Harald Hoyer <harald@redhat.com> 204-8
- fix, which helps to sucessfully browse journals with
  duplicated seqnums

* Fri Jun 14 2013 Harald Hoyer <harald@redhat.com> 204-7
- fix duplicate message ID bug
Resolves: rhbz#974132

* Thu Jun 06 2013 Harald Hoyer <harald@redhat.com> 204-6
- introduce 99-default-disable.preset

* Thu Jun  6 2013 Lennart Poettering <lpoetter@redhat.com> - 204-5
- Rename 90-display-manager.preset to 85-display-manager.preset so that it actually takes precedence over 90-default.preset's "disable *" line (#903690)

* Tue May 28 2013 Harald Hoyer <harald@redhat.com> 204-4
- Fix kernel-install (#965897)

* Wed May 22 2013 Kay Sievers <kay@redhat.com> - 204-3
- Fix kernel-install (#965897)

* Thu May  9 2013 Lennart Poettering <lpoetter@redhat.com> - 204-2
- New upstream release
- disable isdn by default (#959793)

* Tue May 07 2013 Harald Hoyer <harald@redhat.com> 203-2
- forward port kernel-install-grubby.patch

* Tue May  7 2013 Lennart Poettering <lpoetter@redhat.com> - 203-1
- New upstream release

* Wed Apr 24 2013 Harald Hoyer <harald@redhat.com> 202-3
- fix ENOENT for getaddrinfo
- Resolves: rhbz#954012 rhbz#956035
- crypt-setup-generator: correctly check return of strdup
- logind-dbus: initialize result variable
- prevent library underlinking

* Fri Apr 19 2013 Harald Hoyer <harald@redhat.com> 202-2
- nspawn create empty /etc/resolv.conf if necessary
- python wrapper: add sd_journal_add_conjunction()
- fix s390 booting
- Resolves: rhbz#953217

* Thu Apr 18 2013 Lennart Poettering <lpoetter@redhat.com> - 202-1
- New upstream release

* Tue Apr 09 2013 Michal Schmidt <mschmidt@redhat.com> - 201-2
- Automatically discover whether to run autoreconf and add autotools and git
  BuildRequires based on the presence of patches to be applied.
- Use find -delete.

* Mon Apr  8 2013 Lennart Poettering <lpoetter@redhat.com> - 201-1
- New upstream release

* Mon Apr  8 2013 Lennart Poettering <lpoetter@redhat.com> - 200-4
- Update preset file

* Fri Mar 29 2013 Lennart Poettering <lpoetter@redhat.com> - 200-3
- Remove NetworkManager-wait-online.service from presets file again, it should default to off

* Fri Mar 29 2013 Lennart Poettering <lpoetter@redhat.com> - 200-2
- New upstream release

* Tue Mar 26 2013 Lennart Poettering <lpoetter@redhat.com> - 199-2
- Add NetworkManager-wait-online.service to the presets file

* Tue Mar 26 2013 Lennart Poettering <lpoetter@redhat.com> - 199-1
- New upstream release

* Mon Mar 18 2013 Michal Schmidt <mschmidt@redhat.com> 198-7
- Drop /usr/s?bin/ prefixes.

* Fri Mar 15 2013 Harald Hoyer <harald@redhat.com> 198-6
- run autogen to pickup all changes

* Fri Mar 15 2013 Harald Hoyer <harald@redhat.com> 198-5
- do not mount anything, when not running as pid 1
- add initrd.target for systemd in the initrd

* Wed Mar 13 2013 Harald Hoyer <harald@redhat.com> 198-4
- fix switch-root and local-fs.target problem
- patch kernel-install to use grubby, if available

* Fri Mar 08 2013 Harald Hoyer <harald@redhat.com> 198-3
- add Conflict with dracut < 026 because of the new switch-root isolate

* Thu Mar  7 2013 Lennart Poettering <lpoetter@redhat.com> - 198-2
- Create required users

* Thu Mar 7 2013 Lennart Poettering <lpoetter@redhat.com> - 198-1
- New release
- Enable journal persistancy by default

* Sun Feb 10 2013 Peter Robinson <pbrobinson@fedoraproject.org> 197-3
- Bump for ARM

* Fri Jan 18 2013 Michal Schmidt <mschmidt@redhat.com> - 197-2
- Added qemu-guest-agent.service to presets (Lennart, #885406).
- Add missing pygobject3-base to systemd-analyze deps (Lennart).
- Do not require hwdata, it is all in the hwdb now (Kay).
- Drop dependency on dbus-python.

* Tue Jan  8 2013 Lennart Poettering <lpoetter@redhat.com> - 197-1
- New upstream release

* Mon Dec 10 2012 Michal Schmidt <mschmidt@redhat.com> - 196-4
- Enable rngd.service by default (#857765).

* Mon Dec 10 2012 Michal Schmidt <mschmidt@redhat.com> - 196-3
- Disable hardening on s390(x) because PIE is broken there and produces
  text relocations with __thread (#868839).

* Wed Dec 05 2012 Michal Schmidt <mschmidt@redhat.com> - 196-2
- added spice-vdagentd.service to presets (Lennart, #876237)
- BR cryptsetup-devel instead of the legacy cryptsetup-luks-devel provide name
  (requested by Milan Brož).
- verbose make to see the actual build flags

* Wed Nov 21 2012 Lennart Poettering <lpoetter@redhat.com> - 196-1
- New upstream release

* Tue Nov 20 2012 Lennart Poettering <lpoetter@redhat.com> - 195-8
- https://bugzilla.redhat.com/show_bug.cgi?id=873459
- https://bugzilla.redhat.com/show_bug.cgi?id=878093

* Thu Nov 15 2012 Michal Schmidt <mschmidt@redhat.com> - 195-7
- Revert udev killing cgroup patch for F18 Beta.
- https://bugzilla.redhat.com/show_bug.cgi?id=873576

* Fri Nov 09 2012 Michal Schmidt <mschmidt@redhat.com> - 195-6
- Fix cyclical dep between systemd and systemd-libs.
- Avoid broken build of test-journal-syslog.
- https://bugzilla.redhat.com/show_bug.cgi?id=873387
- https://bugzilla.redhat.com/show_bug.cgi?id=872638

* Thu Oct 25 2012 Kay Sievers <kay@redhat.com> - 195-5
- require 'sed', limit HOSTNAME= match

* Wed Oct 24 2012 Michal Schmidt <mschmidt@redhat.com> - 195-4
- add dmraid-activation.service to the default preset
- add yum protected.d fragment
- https://bugzilla.redhat.com/show_bug.cgi?id=869619
- https://bugzilla.redhat.com/show_bug.cgi?id=869717

* Wed Oct 24 2012 Kay Sievers <kay@redhat.com> - 195-3
- Migrate /etc/sysconfig/ i18n, keyboard, network files/variables to
  systemd native files

* Tue Oct 23 2012 Lennart Poettering <lpoetter@redhat.com> - 195-2
- Provide syslog because the journal is fine as a syslog implementation

* Tue Oct 23 2012 Lennart Poettering <lpoetter@redhat.com> - 195-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=831665
- https://bugzilla.redhat.com/show_bug.cgi?id=847720
- https://bugzilla.redhat.com/show_bug.cgi?id=858693
- https://bugzilla.redhat.com/show_bug.cgi?id=863481
- https://bugzilla.redhat.com/show_bug.cgi?id=864629
- https://bugzilla.redhat.com/show_bug.cgi?id=864672
- https://bugzilla.redhat.com/show_bug.cgi?id=864674
- https://bugzilla.redhat.com/show_bug.cgi?id=865128
- https://bugzilla.redhat.com/show_bug.cgi?id=866346
- https://bugzilla.redhat.com/show_bug.cgi?id=867407
- https://bugzilla.redhat.com/show_bug.cgi?id=868603

* Wed Oct 10 2012 Michal Schmidt <mschmidt@redhat.com> - 194-2
- Add scriptlets for migration away from systemd-timedated-ntp.target

* Wed Oct  3 2012 Lennart Poettering <lpoetter@redhat.com> - 194-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=859614
- https://bugzilla.redhat.com/show_bug.cgi?id=859655

* Fri Sep 28 2012 Lennart Poettering <lpoetter@redhat.com> - 193-1
- New upstream release

* Tue Sep 25 2012 Lennart Poettering <lpoetter@redhat.com> - 192-1
- New upstream release

* Fri Sep 21 2012 Lennart Poettering <lpoetter@redhat.com> - 191-2
- Fix journal mmap header prototype definition to fix compilation on 32bit

* Fri Sep 21 2012 Lennart Poettering <lpoetter@redhat.com> - 191-1
- New upstream release
- Enable all display managers by default, as discussed with Adam Williamson

* Thu Sep 20 2012 Lennart Poettering <lpoetter@redhat.com> - 190-1
- New upstream release
- Take possession of /etc/localtime, and remove /etc/sysconfig/clock
- https://bugzilla.redhat.com/show_bug.cgi?id=858780
- https://bugzilla.redhat.com/show_bug.cgi?id=858787
- https://bugzilla.redhat.com/show_bug.cgi?id=858771
- https://bugzilla.redhat.com/show_bug.cgi?id=858754
- https://bugzilla.redhat.com/show_bug.cgi?id=858746
- https://bugzilla.redhat.com/show_bug.cgi?id=858266
- https://bugzilla.redhat.com/show_bug.cgi?id=858224
- https://bugzilla.redhat.com/show_bug.cgi?id=857670
- https://bugzilla.redhat.com/show_bug.cgi?id=856975
- https://bugzilla.redhat.com/show_bug.cgi?id=855863
- https://bugzilla.redhat.com/show_bug.cgi?id=851970
- https://bugzilla.redhat.com/show_bug.cgi?id=851275
- https://bugzilla.redhat.com/show_bug.cgi?id=851131
- https://bugzilla.redhat.com/show_bug.cgi?id=847472
- https://bugzilla.redhat.com/show_bug.cgi?id=847207
- https://bugzilla.redhat.com/show_bug.cgi?id=846483
- https://bugzilla.redhat.com/show_bug.cgi?id=846085
- https://bugzilla.redhat.com/show_bug.cgi?id=845973
- https://bugzilla.redhat.com/show_bug.cgi?id=845194
- https://bugzilla.redhat.com/show_bug.cgi?id=845028
- https://bugzilla.redhat.com/show_bug.cgi?id=844630
- https://bugzilla.redhat.com/show_bug.cgi?id=839736
- https://bugzilla.redhat.com/show_bug.cgi?id=835848
- https://bugzilla.redhat.com/show_bug.cgi?id=831740
- https://bugzilla.redhat.com/show_bug.cgi?id=823485
- https://bugzilla.redhat.com/show_bug.cgi?id=821813
- https://bugzilla.redhat.com/show_bug.cgi?id=807886
- https://bugzilla.redhat.com/show_bug.cgi?id=802198
- https://bugzilla.redhat.com/show_bug.cgi?id=767795
- https://bugzilla.redhat.com/show_bug.cgi?id=767561
- https://bugzilla.redhat.com/show_bug.cgi?id=752774
- https://bugzilla.redhat.com/show_bug.cgi?id=732874
- https://bugzilla.redhat.com/show_bug.cgi?id=858735

* Thu Sep 13 2012 Lennart Poettering <lpoetter@redhat.com> - 189-4
- Don't pull in pkg-config as dep
- https://bugzilla.redhat.com/show_bug.cgi?id=852828

* Wed Sep 12 2012 Lennart Poettering <lpoetter@redhat.com> - 189-3
- Update preset policy
- Rename preset policy file from 99-default.preset to 90-default.preset so that people can order their own stuff after the Fedora default policy if they wish

* Thu Aug 23 2012 Lennart Poettering <lpoetter@redhat.com> - 189-2
- Update preset policy
- https://bugzilla.redhat.com/show_bug.cgi?id=850814

* Thu Aug 23 2012 Lennart Poettering <lpoetter@redhat.com> - 189-1
- New upstream release

* Thu Aug 16 2012 Ray Strode <rstrode@redhat.com> 188-4
- more scriptlet fixes
  (move dm migration logic to %posttrans so the service
   files it's looking for are available at the time
   the logic is run)

* Sat Aug 11 2012 Lennart Poettering <lpoetter@redhat.com> - 188-3
- Remount file systems MS_PRIVATE before switching roots
- https://bugzilla.redhat.com/show_bug.cgi?id=847418

* Wed Aug 08 2012 Rex Dieter <rdieter@fedoraproject.org> - 188-2
- fix scriptlets

* Wed Aug  8 2012 Lennart Poettering <lpoetter@redhat.com> - 188-1
- New upstream release
- Enable gdm and avahi by default via the preset file
- Convert /etc/sysconfig/desktop to display-manager.service symlink
- Enable hardened build

* Mon Jul 30 2012 Kay Sievers <kay@redhat.com> - 187-3
- Obsolete: system-setup-keyboard

* Wed Jul 25 2012 Kalev Lember <kalevlember@gmail.com> - 187-2
- Run ldconfig for the new -libs subpackage

* Thu Jul 19 2012 Lennart Poettering <lpoetter@redhat.com> - 187-1
- New upstream release

* Mon Jul 09 2012 Harald Hoyer <harald@redhat.com> 186-2
- fixed dracut conflict version

* Tue Jul  3 2012 Lennart Poettering <lpoetter@redhat.com> - 186-1
- New upstream release

* Fri Jun 22 2012 Nils Philippsen <nils@redhat.com> - 185-7.gite7aee75
- add obsoletes/conflicts so multilib systemd -> systemd-libs updates work

* Thu Jun 14 2012 Michal Schmidt <mschmidt@redhat.com> - 185-6.gite7aee75
- Update to current git

* Wed Jun 06 2012 Kay Sievers - 185-5.gita2368a3
- disable plymouth in configure, to drop the .wants/ symlinks

* Wed Jun 06 2012 Michal Schmidt <mschmidt@redhat.com> - 185-4.gita2368a3
- Update to current git snapshot
  - Add systemd-readahead-analyze
  - Drop upstream patch
- Split systemd-libs
- Drop duplicate doc files
- Fixed License headers of subpackages

* Wed Jun 06 2012 Ray Strode <rstrode@redhat.com> - 185-3
- Drop plymouth files
- Conflict with old plymouth

* Tue Jun 05 2012 Kay Sievers - 185-2
- selinux udev labeling fix
- conflict with older dracut versions for new udev file names

* Mon Jun 04 2012 Kay Sievers - 185-1
- New upstream release
  - udev selinux labeling fixes
  - new man pages
  - systemctl help <unit name>

* Thu May 31 2012 Lennart Poettering <lpoetter@redhat.com> - 184-1
- New upstream release

* Thu May 24 2012 Kay Sievers <kay@redhat.com> - 183-1
- New upstream release including udev merge.

* Wed Mar 28 2012 Michal Schmidt <mschmidt@redhat.com> - 44-4
- Add triggers from Bill Nottingham to correct the damage done by
  the obsoleted systemd-units's preun scriptlet (#807457).

* Mon Mar 26 2012 Dennis Gilmore <dennis@ausil.us> - 44-3
- apply patch from upstream so we can build systemd on arm and ppc
- and likely the rest of the secondary arches

* Tue Mar 20 2012 Michal Schmidt <mschmidt@redhat.com> - 44-2
- Don't build the gtk parts anymore. They're moving into systemd-ui.
- Remove a dead patch file.

* Fri Mar 16 2012 Lennart Poettering <lpoetter@redhat.com> - 44-1
- New upstream release
- Closes #798760, #784921, #783134, #768523, #781735

* Mon Feb 27 2012 Dennis Gilmore <dennis@ausil.us> - 43-2
- don't conflict with fedora-release systemd never actually provided
- /etc/os-release so there is no actual conflict

* Wed Feb 15 2012 Lennart Poettering <lpoetter@redhat.com> - 43-1
- New upstream release
- Closes #789758, #790260, #790522

* Sat Feb 11 2012 Lennart Poettering <lpoetter@redhat.com> - 42-1
- New upstream release
- Save a bit of entropy during system installation (#789407)
- Don't own /etc/os-release anymore, leave that to fedora-release

* Thu Feb  9 2012 Adam Williamson <awilliam@redhat.com> - 41-2
- rebuild for fixed binutils

* Thu Feb  9 2012 Lennart Poettering <lpoetter@redhat.com> - 41-1
- New upstream release

* Tue Feb  7 2012 Lennart Poettering <lpoetter@redhat.com> - 40-1
- New upstream release

* Thu Jan 26 2012 Kay Sievers <kay@redhat.com> - 39-3
- provide /sbin/shutdown

* Wed Jan 25 2012 Harald Hoyer <harald@redhat.com> 39-2
- increment release

* Wed Jan 25 2012 Kay Sievers <kay@redhat.com> - 39-1.1
- install everything in /usr
  https://fedoraproject.org/wiki/Features/UsrMove

* Wed Jan 25 2012 Lennart Poettering <lpoetter@redhat.com> - 39-1
- New upstream release

* Sun Jan 22 2012 Michal Schmidt <mschmidt@redhat.com> - 38-6.git9fa2f41
- Update to a current git snapshot.
- Resolves: #781657

* Sun Jan 22 2012 Michal Schmidt <mschmidt@redhat.com> - 38-5
- Build against libgee06. Reenable gtk tools.
- Delete unused patches.
- Add easy building of git snapshots.
- Remove legacy spec file elements.
- Don't mention implicit BuildRequires.
- Configure with --disable-static.
- Merge -units into the main package.
- Move section 3 manpages to -devel.
- Fix unowned directory.
- Run ldconfig in scriptlets.
- Split systemd-analyze to a subpackage.

* Sat Jan 21 2012 Dan Horák <dan[at]danny.cz> - 38-4
- fix build on big-endians

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-3
- Disable building of gtk tools for now

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-2
- Fix a few (build) dependencies

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-1
- New upstream release

* Tue Nov 15 2011 Michal Schmidt <mschmidt@redhat.com> - 37-4
- Run authconfig if /etc/pam.d/system-auth is not a symlink.
- Resolves: #753160

* Wed Nov 02 2011 Michal Schmidt <mschmidt@redhat.com> - 37-3
- Fix remote-fs-pre.target and its ordering.
- Resolves: #749940

* Wed Oct 19 2011 Michal Schmidt <mschmidt@redhat.com> - 37-2
- A couple of fixes from upstream:
- Fix a regression in bash-completion reported in Bodhi.
- Fix a crash in isolating.
- Resolves: #717325

* Tue Oct 11 2011 Lennart Poettering <lpoetter@redhat.com> - 37-1
- New upstream release
- Resolves: #744726, #718464, #713567, #713707, #736756

* Thu Sep 29 2011 Michal Schmidt <mschmidt@redhat.com> - 36-5
- Undo the workaround. Kay says it does not belong in systemd.
- Unresolves: #741655

* Thu Sep 29 2011 Michal Schmidt <mschmidt@redhat.com> - 36-4
- Workaround for the crypto-on-lvm-on-crypto disk layout
- Resolves: #741655

* Sun Sep 25 2011 Michal Schmidt <mschmidt@redhat.com> - 36-3
- Revert an upstream patch that caused ordering cycles
- Resolves: #741078

* Fri Sep 23 2011 Lennart Poettering <lpoetter@redhat.com> - 36-2
- Add /etc/timezone to ghosted files

* Fri Sep 23 2011 Lennart Poettering <lpoetter@redhat.com> - 36-1
- New upstream release
- Resolves: #735013, #736360, #737047, #737509, #710487, #713384

* Thu Sep  1 2011 Lennart Poettering <lpoetter@redhat.com> - 35-1
- New upstream release
- Update post scripts
- Resolves: #726683, #713384, #698198, #722803, #727315, #729997, #733706, #734611

* Thu Aug 25 2011 Lennart Poettering <lpoetter@redhat.com> - 34-1
- New upstream release

* Fri Aug 19 2011 Harald Hoyer <harald@redhat.com> 33-2
- fix ABRT on service file reloading
- Resolves: rhbz#732020

* Wed Aug  3 2011 Lennart Poettering <lpoetter@redhat.com> - 33-1
- New upstream release

* Fri Jul 29 2011 Lennart Poettering <lpoetter@redhat.com> - 32-1
- New upstream release

* Wed Jul 27 2011 Lennart Poettering <lpoetter@redhat.com> - 31-2
- Fix access mode of modprobe file, restart logind after upgrade

* Wed Jul 27 2011 Lennart Poettering <lpoetter@redhat.com> - 31-1
- New upstream release

* Wed Jul 13 2011 Lennart Poettering <lpoetter@redhat.com> - 30-1
- New upstream release

* Thu Jun 16 2011 Lennart Poettering <lpoetter@redhat.com> - 29-1
- New upstream release

* Mon Jun 13 2011 Michal Schmidt <mschmidt@redhat.com> - 28-4
- Apply patches from current upstream.
- Fixes memory size detection on 32-bit with >4GB RAM (BZ712341)

* Wed Jun 08 2011 Michal Schmidt <mschmidt@redhat.com> - 28-3
- Apply patches from current upstream
- https://bugzilla.redhat.com/show_bug.cgi?id=709909
- https://bugzilla.redhat.com/show_bug.cgi?id=710839
- https://bugzilla.redhat.com/show_bug.cgi?id=711015

* Sat May 28 2011 Lennart Poettering <lpoetter@redhat.com> - 28-2
- Pull in nss-myhostname

* Thu May 26 2011 Lennart Poettering <lpoetter@redhat.com> - 28-1
- New upstream release

* Wed May 25 2011 Lennart Poettering <lpoetter@redhat.com> - 26-2
- Bugfix release
- https://bugzilla.redhat.com/show_bug.cgi?id=707507
- https://bugzilla.redhat.com/show_bug.cgi?id=707483
- https://bugzilla.redhat.com/show_bug.cgi?id=705427
- https://bugzilla.redhat.com/show_bug.cgi?id=707577

* Sat Apr 30 2011 Lennart Poettering <lpoetter@redhat.com> - 26-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=699394
- https://bugzilla.redhat.com/show_bug.cgi?id=698198
- https://bugzilla.redhat.com/show_bug.cgi?id=698674
- https://bugzilla.redhat.com/show_bug.cgi?id=699114
- https://bugzilla.redhat.com/show_bug.cgi?id=699128

* Thu Apr 21 2011 Lennart Poettering <lpoetter@redhat.com> - 25-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=694788
- https://bugzilla.redhat.com/show_bug.cgi?id=694321
- https://bugzilla.redhat.com/show_bug.cgi?id=690253
- https://bugzilla.redhat.com/show_bug.cgi?id=688661
- https://bugzilla.redhat.com/show_bug.cgi?id=682662
- https://bugzilla.redhat.com/show_bug.cgi?id=678555
- https://bugzilla.redhat.com/show_bug.cgi?id=628004

* Wed Apr  6 2011 Lennart Poettering <lpoetter@redhat.com> - 24-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=694079
- https://bugzilla.redhat.com/show_bug.cgi?id=693289
- https://bugzilla.redhat.com/show_bug.cgi?id=693274
- https://bugzilla.redhat.com/show_bug.cgi?id=693161

* Tue Apr  5 2011 Lennart Poettering <lpoetter@redhat.com> - 23-1
- New upstream release
- Include systemd-sysv-convert

* Fri Apr  1 2011 Lennart Poettering <lpoetter@redhat.com> - 22-1
- New upstream release

* Wed Mar 30 2011 Lennart Poettering <lpoetter@redhat.com> - 21-2
- The quota services are now pulled in by mount points, hence no need to enable them explicitly

* Tue Mar 29 2011 Lennart Poettering <lpoetter@redhat.com> - 21-1
- New upstream release

* Mon Mar 28 2011 Matthias Clasen <mclasen@redhat.com> - 20-2
- Apply upstream patch to not send untranslated messages to plymouth

* Tue Mar  8 2011 Lennart Poettering <lpoetter@redhat.com> - 20-1
- New upstream release

* Tue Mar  1 2011 Lennart Poettering <lpoetter@redhat.com> - 19-1
- New upstream release

* Wed Feb 16 2011 Lennart Poettering <lpoetter@redhat.com> - 18-1
- New upstream release

* Mon Feb 14 2011 Bill Nottingham <notting@redhat.com> - 17-6
- bump upstart obsoletes (#676815)

* Wed Feb  9 2011 Tom Callaway <spot@fedoraproject.org> - 17-5
- add macros.systemd file for %%{_unitdir}

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb  9 2011 Lennart Poettering <lpoetter@redhat.com> - 17-3
- Fix popen() of systemctl, #674916

* Mon Feb  7 2011 Bill Nottingham <notting@redhat.com> - 17-2
- add epoch to readahead obsolete

* Sat Jan 22 2011 Lennart Poettering <lpoetter@redhat.com> - 17-1
- New upstream release

* Tue Jan 18 2011 Lennart Poettering <lpoetter@redhat.com> - 16-2
- Drop console.conf again, since it is not shipped in pamtmp.conf

* Sat Jan  8 2011 Lennart Poettering <lpoetter@redhat.com> - 16-1
- New upstream release

* Thu Nov 25 2010 Lennart Poettering <lpoetter@redhat.com> - 15-1
- New upstream release

* Thu Nov 25 2010 Lennart Poettering <lpoetter@redhat.com> - 14-1
- Upstream update
- Enable hwclock-load by default
- Obsolete readahead
- Enable /var/run and /var/lock on tmpfs

* Fri Nov 19 2010 Lennart Poettering <lpoetter@redhat.com> - 13-1
- new upstream release

* Wed Nov 17 2010 Bill Nottingham <notting@redhat.com> 12-3
- Fix clash

* Wed Nov 17 2010 Lennart Poettering <lpoetter@redhat.com> - 12-2
- Don't clash with initscripts for now, so that we don't break the builders

* Wed Nov 17 2010 Lennart Poettering <lpoetter@redhat.com> - 12-1
- New upstream release

* Fri Nov 12 2010 Matthias Clasen <mclasen@redhat.com> - 11-2
- Rebuild with newer vala, libnotify

* Thu Oct  7 2010 Lennart Poettering <lpoetter@redhat.com> - 11-1
- New upstream release

* Wed Sep 29 2010 Jesse Keating <jkeating@redhat.com> - 10-6
- Rebuilt for gcc bug 634757

* Thu Sep 23 2010 Bill Nottingham <notting@redhat.com> - 10-5
- merge -sysvinit into main package

* Mon Sep 20 2010 Bill Nottingham <notting@redhat.com> - 10-4
- obsolete upstart-sysvinit too

* Fri Sep 17 2010 Bill Nottingham <notting@redhat.com> - 10-3
- Drop upstart requires

* Tue Sep 14 2010 Lennart Poettering <lpoetter@redhat.com> - 10-2
- Enable audit
- https://bugzilla.redhat.com/show_bug.cgi?id=633771

* Tue Sep 14 2010 Lennart Poettering <lpoetter@redhat.com> - 10-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=630401
- https://bugzilla.redhat.com/show_bug.cgi?id=630225
- https://bugzilla.redhat.com/show_bug.cgi?id=626966
- https://bugzilla.redhat.com/show_bug.cgi?id=623456

* Fri Sep  3 2010 Bill Nottingham <notting@redhat.com> - 9-3
- move fedora-specific units to initscripts; require newer version thereof

* Fri Sep  3 2010 Lennart Poettering <lpoetter@redhat.com> - 9-2
- Add missing tarball

* Fri Sep  3 2010 Lennart Poettering <lpoetter@redhat.com> - 9-1
- New upstream version
- Closes 501720, 614619, 621290, 626443, 626477, 627014, 627785, 628913

* Fri Aug 27 2010 Lennart Poettering <lpoetter@redhat.com> - 8-3
- Reexecute after installation, take ownership of /var/run/user
- https://bugzilla.redhat.com/show_bug.cgi?id=627457
- https://bugzilla.redhat.com/show_bug.cgi?id=627634

* Thu Aug 26 2010 Lennart Poettering <lpoetter@redhat.com> - 8-2
- Properly create default.target link

* Wed Aug 25 2010 Lennart Poettering <lpoetter@redhat.com> - 8-1
- New upstream release

* Thu Aug 12 2010 Lennart Poettering <lpoetter@redhat.com> - 7-3
- Fix https://bugzilla.redhat.com/show_bug.cgi?id=623561

* Thu Aug 12 2010 Lennart Poettering <lpoetter@redhat.com> - 7-2
- Fix https://bugzilla.redhat.com/show_bug.cgi?id=623430

* Tue Aug 10 2010 Lennart Poettering <lpoetter@redhat.com> - 7-1
- New upstream release

* Fri Aug  6 2010 Lennart Poettering <lpoetter@redhat.com> - 6-2
- properly hide output on package installation
- pull in coreutils during package installtion

* Fri Aug  6 2010 Lennart Poettering <lpoetter@redhat.com> - 6-1
- New upstream release
- Fixes #621200

* Wed Aug  4 2010 Lennart Poettering <lpoetter@redhat.com> - 5-2
- Add tarball

* Wed Aug  4 2010 Lennart Poettering <lpoetter@redhat.com> - 5-1
- Prepare release 5

* Tue Jul 27 2010 Bill Nottingham <notting@redhat.com> - 4-4
- Add 'sysvinit-userspace' provide to -sysvinit package to fix upgrade/install (#618537)

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-3
- Add libselinux to build dependencies

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-2
- Use the right tarball

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-1
- New upstream release, and make default

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-3
- Used wrong tarball

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-2
- Own /cgroup jointly with libcgroup, since we don't dpend on it anymore

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-1
- New upstream release

* Fri Jul 9 2010 Lennart Poettering <lpoetter@redhat.com> - 2-0
- New upstream release

* Wed Jul 7 2010 Lennart Poettering <lpoetter@redhat.com> - 1-0
- First upstream release

* Tue Jun 29 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.7.20100629git4176e5
- New snapshot
- Split off -units package where other packages can depend on without pulling in the whole of systemd

* Tue Jun 22 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.6.20100622gita3723b
- Add missing libtool dependency.

* Tue Jun 22 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.5.20100622gita3723b
- Update snapshot

* Mon Jun 14 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.4.20100614git393024
- Pull the latest snapshot that fixes a segfault. Resolves rhbz#603231

* Fri Jun 11 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.3.20100610git2f198e
- More minor fixes as per review

* Thu Jun 10 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.2.20100610git2f198e
- Spec improvements from David Hollis

* Wed Jun 09 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.1.20090609git2f198e
- Address review comments

* Tue Jun 01 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.0.git2010-06-02
- Initial spec (adopted from Kay Sievers)
