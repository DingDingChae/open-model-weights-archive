# Model storage

## Design

The Git repository stores immutable source revisions and artifact coordinates.
Full snapshots are published as OCI artifacts in public GHCR. This follows
Desktop Material CheapLFS's registry strategy without consuming Git LFS
storage or download bandwidth.

## Integrity

Hugging Face snapshots are pinned to commit SHA. OCI manifests are
content-addressed. The archive script refuses a snapshot smaller than the
locked upstream measurement.

## Failure modes

- Interrupted downloads resume through the Hugging Face cache.
- Missing ORAS or registry authentication stops before publication.
- A partial upload never moves the `latest` tag.
- Upstream licenses remain attached to the copied snapshot.

## Security

No model token is required for these public, ungated snapshots. GitHub
credentials are supplied by the local credential helper to ORAS and are never
written into this repository.
