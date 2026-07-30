# AoS Envelope Boundary

Ingress and egress use `aos.application.envelope.v1`. Validate version, identity, content hash, idempotency, provenance/security context, and payload. Emit an acknowledgement and a terminal success/rejection/failure receipt. Network/MCP/VPort/bus transports remain disabled scaffolds.
