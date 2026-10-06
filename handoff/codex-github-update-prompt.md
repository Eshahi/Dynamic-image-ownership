Post the GitHub issue updates that the repository owner approved on 2026-10-06. The repository is Eshahi/Dynamic-image-ownership. Use the GitHub CLI (`gh`) or the GitHub connector you already use for this repository.

Source of truth: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/thesis-runs/d916749c/github-issue-updates-20261006.md`. The owner approved it exactly as written ("Approve all as planned").

Do exactly this and nothing else:

1. **Comment text.** For each issue under "Close as completed", "Close as not planned" and "Keep open, with a status comment":
   - post the quoted block as one comment, without the leading `> `;
   - replace every `B/` with `https://github.com/Eshahi/Dynamic-image-ownership/blob/e26bd4b/`;
   - add no footer and no mention of Claude or Codex. The owner wants these comments to appear as their own (decision of 2026-10-06).
2. **Closing.**
   - Close #18, #19, #20, #21, #23, #24 and #25 with reason **completed**.
   - Close #27 with reason **not planned**.
   - Do not close #22, #26, #28, #29, #30, #31, #32 or #33. They get the comment only. #26, #28 and #29 share one text, and so do #31, #32 and #33.
3. **Draft PRs.**
   - On #67, #68 and #69, comment: `Superseded by the method amendments: the frozen candidate is F5 r2 (see research/m1b-package.md at e26bd4b). Closing without merge.`
   - Then close each PR without merging. Do not delete their branches.
4. **No change** to #13, #34, #35, #36, #37, #38 or PR #59. Do not edit labels, titles, milestones or any other issue.
5. **Report.** Write `thesis-runs/d916749c/github-update-report.md` listing each issue or PR number, the action taken and the comment URL. Stop if any call fails, and record the failure in that report.
