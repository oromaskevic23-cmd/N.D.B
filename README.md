# NDB — New Digital Bitcoin

**Project founder and founding architect:** Alexander Nikolaevich Romaskevich (RomaskevicH). [Authorship and contribution provenance](AUTHORS.md).

<p align="center">
  <img src="assets/ndb-hero-20261029.jpg" alt="NDB digital emblem" width="420">
</p>

<p align="center"><strong>A digital asset initiative within the CRYPTO IMPERIAL Ecosystem.</strong></p>

**Founder and Architect:** Alexander Romaskevich · **Signature:** RomaskevicH  
**Network:** Polygon PoS Mainnet · **Contract:** `0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4`

**Explore the two-project overview:** [NDB & IMPERIUM in the CRYPTO IMPERIAL Ecosystem →](https://github.com/oromaskevic23-cmd/CRYPTO-IMPERIAL-Ecosystem-Public#imperium--ndb)

## Project status

NDB is a Polygon token project. Its contract is listed as an **Exact Match** on [Sourcify](https://repo.sourcify.dev/137/0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4), which identifies the contract as `NDB_Sovereign`. Source matching does not establish an independent security audit, market liquidity, exchange listing, commercial adoption or production agent payments.

The name New Digital Bitcoin is the project name; NDB is a distinct Polygon token and is not Bitcoin or an official Bitcoin project.

## Purpose and direction

NDB aims to support a transparent digital-asset ecosystem with independently verifiable contract information and, subject to further engineering and approvals, useful services for AI-driven workflows. Potential integrations are proposals and must be tested and authorized before any use involving funds.

The related project [IMPERIUM](https://github.com/oromaskevic23-cmd/IMPERIUM-) is a **long-term architectural digital currency envisioned for AI agents worldwide**, not a claim of existing global adoption. Both projects remain within the [CRYPTO IMPERIAL Ecosystem](https://github.com/oromaskevic23-cmd/CRYPTO-IMPERIAL-Ecosystem-Public) boundary.

## Contract identity

| Item | Observation |
| --- | --- |
| Chain | Polygon Mainnet, chain ID `137` |
| Contract address | [`0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4`](https://repo.sourcify.dev/137/0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4) |
| Verified source name | `NDB_Sovereign` |
| Source verification | Sourcify **Exact Match**; verification record dated 1 January 2026 UTC |
| Deployment transaction | [`0x2da7ac67ebdec1900ce066b6038751c5df29c78c59f758a09cdaf5656a63bf06`](https://polygonscan.com/tx/0x2da7ac67ebdec1900ce066b6038751c5df29c78c59f758a09cdaf5656a63bf06) |

See [Token facts](docs/TOKEN-FACTS.md) for the evidence scope and outstanding checks. Current supply, distribution, transfer conditions, liquidity and market data require separate current, block-anchored evidence. Network fees depend on the chain and transaction conditions.

## Read-only token observation

This repository includes a Python standard-library tool that reads the configured NDB contract from an operator-supplied HTTPS Polygon JSON-RPC endpoint. It checks the chain ID and code presence, reads name, symbol, decimals and total supply at one numbered block, and checks the block hash again before returning a JSON report. It uses an explicit read-only RPC method allowlist and has no signing or transaction submission functionality.

```bash
# Set NDB_RPC_URL to your own HTTPS Polygon Mainnet RPC endpoint.
PYTHONPATH=src python3 -m ndb_verify

# Offline unit tests; no RPC endpoint is needed.
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Python 3.9+ is required. A provider can report incorrect data; the tool does not verify source matching, block finality, contract ownership, liquidity, fees or security. The latest block can reorganize. Review the [tool limitations](docs/TOKEN-FACTS.md#read-only-tool-limitations) before interpreting results. Never put credentials, private keys or seed phrases into the repository.

## Architecture and next steps

- [Architecture and trust boundaries](docs/ARCHITECTURE.md)
- [Token facts and evidence](docs/TOKEN-FACTS.md)
- [Evidence-gated roadmap](docs/ROADMAP.md)
- [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md)
- [Nano Core Agents](https://github.com/oromaskevic23-cmd/Nano-Core-Agents-Public) · [IMPERIAL Core](https://github.com/oromaskevic23-cmd/Capital--Core-Public)

**Architecture → Implementation → Evidence**
