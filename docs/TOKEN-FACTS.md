# NDB Token Facts and Evidence

Source record reviewed on 29 October 2026. These observations identify a contract; they do not constitute a security audit or market assessment.

| Attribute | Source-backed observation |
| --- | --- |
| Network | Polygon Mainnet, chain ID 137 |
| Address | `0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4` |
| Contract name | `NDB_Sovereign` |
| Compilation target | `NDB.sol:NDB_Sovereign` |
| Sourcify status | [Exact Match](https://repo.sourcify.dev/137/0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4) |
| Compiler | Solidity `0.8.31+commit.fd3a2265` |
| Verification record | 1 January 2026, 12:51:01 UTC |
| Deployment transaction | [`0x2da7ac67ebdec1900ce066b6038751c5df29c78c59f758a09cdaf5656a63bf06`](https://polygonscan.com/tx/0x2da7ac67ebdec1900ce066b6038751c5df29c78c59f758a09cdaf5656a63bf06) |
| Deployment block | `81076295` (as reported by Sourcify) |

## Requires separate verification

Current supply and decimals; balances and concentration; circulating supply; transfer rules and fees; administrative or upgrade capabilities; liquidity and market prices; exchange listings; independent security review; legal classification; and live integrations. Do not infer these from a source-match record. Publish dates, block numbers, methods and source links with any future claims.

## Read-only tool limitations

`ndb_verify` obtains values from one operator-selected RPC provider. It checks Polygon chain ID, contract bytecode presence and a consistent block hash before and after its calls, and uses a single numbered block tag for contract reads. This reduces accidental mixing of block heights but does not prove that a provider is honest or that the block is finalized, and cannot rule out every backend inconsistency or chain reorganization.

It does not independently compare bytecode with Sourcify, audit source code, confirm asset ownership, determine circulating supply, calculate token tax, assess liquidity, or sign or broadcast transactions. The Sourcify link in the output is a reference, not a live verification performed by the tool. For stronger evidence, independently cross-check trusted providers and record the finalized block hash and methodology.

Use an HTTPS endpoint you trust. Put the endpoint in the `NDB_RPC_URL` environment variable rather than in documentation, committed files or logs when it includes credentials. The program does not print the endpoint, but process environments and infrastructure may expose it to other authorized processes.
