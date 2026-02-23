;;; custom.el -*- lexical-binding: t; -*-

;; Automatically sync org files when saving
(defvar sync-to-unison--running nil "Is a sync currently running?")
(defun sync-to-unison ()
  "Sync org file with unison in the background."
  (when (and (eq major-mode 'org-mode)
             (string-prefix-p (expand-file-name "~/Documents/org") buffer-file-name)
             (file-exists-p (expand-file-name "~/.unison/org-files.prf"))
    (unless sync-to-unison--running
      (setq sync-to-unison--running t)
      (message "Starting background sync with unison...")
      (make-process
       :name "unison-sync"
       :command '("unison" "org-files" "-ui" "text")
       :buffer "*unison-sync*"
       :sentinel
       (lambda (process event)
         (setq sync-to-unison--running nil)
         (if (string-prefix-p "finished" event)
             (message "Org files synced successfully")
           (message "Sync failed! Check *unison-sync* buffer for details"))))))))

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
