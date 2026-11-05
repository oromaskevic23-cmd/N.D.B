# NDB — Cross-Provider Read-Only Evidence

**2026-11-05 · Founder and founding architect: Alexander Nikolaevich Romaskevich (RomaskevicH)**

## Observed token identity, not market claims

NDB is a distinct Polygon PoS token (chain ID `137`) with canonical contract:
`0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4`.

`NDB` / `New Digital Bitcoin` is **not Bitcoin**, a Bitcoin-backed asset, or an official Bitcoin service. A Sourcify exact match identifies compiled source correspondence, not a security audit or proof of live listings, liquidity, token rights or adoption.

## What the new mode does

The `ndb_verify` observer can now optionally compare results from **two distinct, operator-supplied HTTPS JSON-RPC endpoints**:

1. Query the latest height from each endpoint and choose the smaller numbered block.
2. Verify each provider independently reports Polygon chain ID `137`, the requested block number and one stable block hash across its observation.
3. Read contract code, its SHA-256, standard ERC-20 metadata and raw supply using only read-only RPC methods, all pinned to the shared block number.
4. Compare exact block hash, contract address, bytecode hash and length, name, symbol, decimals and raw total supply. **Deny the cross-checked report on any mismatch.**
5. Print the status `TWO_RPC_REPORTS_AGREE_NOT_FINALITY_PROOF` only after matching observations. Never submit transactions, sign with a wallet or retrieve private keys.

Run with two **separately controlled** HTTPS endpoints, where possible:

```sh
export NDB_RPC_URL="https://YOUR-FIRST-POLYGON-RPC"
export NDB_SECOND_RPC_URL="https://YOUR-SECOND-POLYGON-RPC"
PYTHONPATH=src python3 -m ndb_verify
```

The existing one-provider mode remains available by leaving `NDB_SECOND_RPC_URL` unset. The second provider may also be passed explicitly as `--second-rpc-url`. For automated offline test coverage (no provider keys, no live network):

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
```

## What cross-checking DOES NOT prove

Two URLs might resolve to the same provider, might rely on the same upstream node, or could collude. Agreement does not prove canonical consensus, finality, on-chain source matching, admin privileges, circulating supply, token custody, third-party audits, consumer rights or market liquidity. A chain reorganization can change the selected block later. Record the block height, hash, observation timestamp, endpoint operators, limitations and actual evidence for public claims. Do not expose credential-bearing RPC URLs in screenshots or logs.

Before an exchange-readiness or token-linked service claim: obtain block-anchored contract administration and supply verification, distribution/concentration analysis, independent contract security review, applicable legal advice, consumer disclosures and a working independently QA-checked customer service. No artificial volume, misleading price targets, fabricated listings or investor-return promises.
