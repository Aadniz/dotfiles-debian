;;; custom.el -*- lexical-binding: t; -*-
(load-file "~/.config/doom/faces.el")

;; Automatically sync org files when opening and saving them
(defvar sync-to-unison-directory (expand-file-name "~/Documents/org/")
  "Org files under this directory are synced with the org-files profile.")
(defvar sync-to-unison--running nil "Is a sync currently running?")
(defvar sync-to-unison--pending nil "Was another sync asked for while one ran?")

(defun sync-to-unison ()
  "Sync org file with unison in the background."
  (when (and (eq major-mode 'org-mode)
             buffer-file-name
             (string-prefix-p sync-to-unison-directory buffer-file-name)
             (file-exists-p (expand-file-name "~/.unison/org-files.prf")))
    (if sync-to-unison--running
        ;; E.g. saved while the sync from opening the file still runs: sync
        ;; again afterwards, or this change waits for the next save
        (setq sync-to-unison--pending t)
      (sync-to-unison--start))))

(defun sync-to-unison--start ()
  (setq sync-to-unison--running t)
  (message "Starting background sync with unison...")
  (make-process
   :name "unison-sync"
   :command '("unison" "org-files" "-ui" "text")
   :buffer "*unison-sync*"
   :sentinel #'sync-to-unison--finished))

(defun sync-to-unison--finished (process _event)
  (when (memq (process-status process) '(exit signal))
    (setq sync-to-unison--running nil)
    ;; Doom only reverts changed files when you switch buffers or refocus
    ;; Emacs, so show what the sync pulled in right away
    (let ((reverted (sync-to-unison--revert-buffers))
          ;; unison exits with 1 when it skipped conflicts, 2+ on failures
          (status (process-exit-status process)))
      (message "%s%s"
               (pcase status
                 (0 "Org files synced successfully")
                 (1 "Sync skipped conflicting files! Check *unison-sync* buffer for details")
                 (_ "Sync failed! Check *unison-sync* buffer for details"))
               (if reverted
                   (format " (reloaded %s)" (string-join reverted ", "))
                 "")))
    (when sync-to-unison--pending
      (setq sync-to-unison--pending nil)
      (sync-to-unison--start))))

(defun sync-to-unison--revert-buffers ()
  "Revert unmodified buffers whose synced files changed on disk.
Returns the names of the reverted buffers."
  (let (reverted)
    (dolist (buffer (buffer-list))
      (with-current-buffer buffer
        (when (and buffer-file-name
                   (string-prefix-p sync-to-unison-directory buffer-file-name)
                   (file-exists-p buffer-file-name)
                   (not (verify-visited-file-modtime buffer)))
          (if (buffer-modified-p)
              ;; Emacs asks before saving over the newer file
              (message "%s changed on disk, but has unsaved changes; not reloading"
                       (buffer-name))
            ;; preserve-modes: keeps org-mode and folding, and doesn't rerun
            ;; find-file-hook (which would sync again)
            (revert-buffer :ignore-auto :noconfirm :preserve-modes)
            (push (buffer-name) reverted)))))
    (nreverse reverted)))

(add-hook 'after-save-hook #'sync-to-unison)
(add-hook 'find-file-hook #'sync-to-unison)

;; Change window using CTRL + Shift + S
(global-set-key (kbd "C-S-s") 'other-window)

;; Duplicate cursor above and below
(define-key evil-normal-state-map (kbd "M-<up>")
            (lambda ()
              (interactive)
              (call-interactively '+multiple-cursors/evil-mc-toggle-cursor-here)
              (evil-previous-line 1)))
(define-key evil-normal-state-map (kbd "M-<down>")
            (lambda ()
              (interactive)
              (call-interactively '+multiple-cursors/evil-mc-toggle-cursor-here)
              (evil-next-line 1)))

;; Speed up TRAMP according to https://github.com/doomemacs/doomemacs/issues/3909#issuecomment-786596887
(after! tramp
  (setq tramp-inline-compress-start-size 1000)
  (setq tramp-copy-size-limit 10000)
  (setq vc-handled-backends '(Git))
  (setq tramp-verbose 1)
  (setq tramp-default-method "scp")
  (setq tramp-use-ssh-controlmaster-options nil)
  (setq projectile--mode-line "Projectile")
  (setq tramp-verbose 1))

