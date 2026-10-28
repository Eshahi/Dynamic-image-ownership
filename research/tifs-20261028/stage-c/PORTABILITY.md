# Metadata byte identities across checkouts

The identifier draw ran on Windows after rule commit `fd0b682`, with text-only
metadata responses. Its original manifest and receipt hashes are preserved.
Git normalizes CRLF line endings in the rule and 24 generated receipt JSONs;
the HTTP response bodies and selection outcomes are unchanged.

`git-portability.json` records both original draw SHA256 and committed Git-blob
SHA256 for each available evidence file at `78a85a2`. Every difference was
verified to be CRLF-to-LF only, with no other content change. A Linux consumer
should normalize backslash path separators to `/` and verify `git_blob_sha256`.
Records outside that Git tree remain explicitly unavailable there; the original
exclusion snapshot retains their identifiers and the selector records missing
historical sources. This mapping does not claim those external bytes are present.

No source was selected again, no eligibility rule changed, and no image was
downloaded. Later raw/canonical image-hash checks remain required before any
authorized confirmatory use.
