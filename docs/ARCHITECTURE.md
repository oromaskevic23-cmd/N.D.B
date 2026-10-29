# NDB Architecture and Trust Boundaries

This document describes a development direction. No production payment system or autonomous economic activity is asserted.

## Roles

The Architect retains final architectural authority. HANTER is the AI Command Center and operates under the Architect. Multiple domain and functional orchestrators coordinate professional teams and dynamically assigned Nano Core Agents within separate runtime domains; there is no unrestricted global operational orchestrator. ORION is the collective-intelligence component where applicable.

## Required controls for proposed integrations

1. AI Passport identifies an agent; identity alone grants no authority.
2. Enterprise Skills describe bounded capabilities; capability does not imply approval.
3. Guardian Core and Zero Trust policies evaluate each requested operation.
4. Approval Gateway applies separately authorized human or bounded-policy decisions.
5. Audit Ledger and ProofGraph record evidence and reconciliation as designed.
6. Public/Private and CRYPTO IMPERIAL Ecosystem boundaries separate public information, sensitive operations, accounts and any digital assets.
7. Agents do not receive private keys, seed phrases or unrestricted spending authority. An Owner Kill Switch is an architectural control, not a claim that every deployment already enforces it.

Any settlement integration needs independently reviewed contract behavior, signing isolation, replay protection, explicit authorization, negative-path tests, incident response and a clear reconciliation policy before production use.

## Implemented in this repository

The Python observation tool uses read-only RPC calls to inspect the configured contract. Unit tests use simulated responses. It does not provide a wallet, signer, transaction executor, custody service, agent runtime or a production payment gateway.

## Related projects

- [IMPERIUM](https://github.com/oromaskevic23-cmd/IMPERIUM-) — long-term architectural digital currency envisioned for AI agents worldwide.
- [Nano Core Agents](https://github.com/oromaskevic23-cmd/Nano-Core-Agents-Public) — public professional-agent architecture.
- [CRYPTO IMPERIAL Ecosystem](https://github.com/oromaskevic23-cmd/CRYPTO-IMPERIAL-Ecosystem-Public) — separate crypto-development direction.
