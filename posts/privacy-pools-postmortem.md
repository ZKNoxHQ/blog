[category]: <> (Security Research)
[date]: <> (2026/03/26)
[title]: <> (Privacy Pools: Anatomy of a 53-bit Entropy Collapse)

An independent analysis of the `bytesToNumber` vulnerability in Privacy Pools (0xbow), its real-world exploitation cost, and why the Ethereum Foundation's Kohaku wallet was never affected.

---

## Summary

A type coercion bug in the Privacy Pools SDK reduced the entropy of all cryptographic master keys from 256 bits to 53 bits (the mantissa width of a JavaScript IEEE 754 double-precision float). Every deposit made through the 0xbow SDK between the March 2025 mainnet launch and the fix in March 2026 is affected.

We independently built a complete brute-force proof of concept (Poseidon BN254 in C/x86-64 assembly), validated it end-to-end with 1000/1000 key recoveries, and measured the attack cost on real hardware. The vulnerability affects all six asset pools (ETH, wBTC, USDC, USDT, DAI, USDS). Approximately 2,711 ETH deposited, with ~1,044 ETH in residuals still at risk.

The Ethereum Foundation's Kohaku wallet, which also integrates Privacy Pools, uses a completely independent key derivation architecture and is **not affected**.

---

## 1. The Vulnerability

### 1.1 Root Cause

The bug is a single function call in `packages/sdk/src/crypto.ts`:

```typescript
import { bytesToNumber } from "viem/utils";

export function generateMasterKeys(mnemonic: string): MasterKeys {
    const key1 = bytesToNumber(                           // ← returns Number
      mnemonicToAccount(mnemonic, { accountIndex: 0 })
        .getHdKey().privateKey!,                          // ← 32 bytes (256 bits)
    );
    const key2 = bytesToNumber(                           // ← returns Number
      mnemonicToAccount(mnemonic, { accountIndex: 1 })
        .getHdKey().privateKey!,                          // ← 32 bytes (256 bits)
    );
    const masterNullifier = poseidon([BigInt(key1)]) as Secret;
    const masterSecret    = poseidon([BigInt(key2)]) as Secret;
    return { masterNullifier, masterSecret };
}
```

**Source (vulnerable, still on `main`):** [crypto.ts on main](https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/sdk/src/crypto.ts)

**Source (fixed, on `dev`):** [crypto.ts on dev](https://github.com/0xbow-io/privacy-pools-core/blob/dev/packages/sdk/src/crypto.ts)

`bytesToNumber` (from viem) converts a `Uint8Array` into a JavaScript `Number`. A `Number` is an IEEE 754 double-precision float with a 52-bit explicit mantissa (53 bits with the implicit leading 1). When a 256-bit private key is converted to `Number`, 203 bits of entropy are silently lost to rounding.

```
Private key (256 bits):  1 0 1 1 0 1 1 0 0 1 ... [256 bits total]
                         ├───── 53 bits ─────┤ ├── 203 bits rounded to zero ──┤
                              kept                      lost

Number:                  1.0110110010...₂ × 2²⁰³
BigInt(Number):          1011011001...000000000000000...0₂
                         ├───── 53 ─────┤├──── 203 zeros ────┤
```

The fix (commit [`00773cb`](https://github.com/0xbow-io/privacy-pools-core/commit/00773cb)) replaces `bytesToNumber` with `bytesToBigInt`, preserving all 256 bits.

### 1.2 How It Happened

The bug was introduced on February 26, 2025, five weeks before mainnet launch:

| Date | Commit | Description |
|------|--------|-------------|
| 21 Feb 2025 | [`fa0a985`](https://github.com/0xbow-io/privacy-pools-core/commit/fa0a985) | `generateMasterKeys(seed)` using `keccak256` + `BigInt`, **no bug** |
| 26 Feb 2025 | [`7e770b4`](https://github.com/0xbow-io/privacy-pools-core/commit/7e770b4) | Rewrite to use `mnemonicToAccount` + `bytesToNumber`, **bug introduced** |
| 31 Mar 2025 | | Mainnet launch with vulnerable code |
| 5 Mar 2026 | [`00773cb`](https://github.com/0xbow-io/privacy-pools-core/commit/00773cb) | Fix: `bytesToNumber` to `bytesToBigInt` |
| 16 Mar 2026 | [`13d53f0`](https://github.com/0xbow-io/privacy-pools-core/commit/13d53f0334b30d74cce32b09531d277a0de2a043) | Remove dead `keys.ts` (audit finding AW-L-01) |

The original implementation (`fa0a985`) used `keccak256(seed)` directly to `BigInt`: no type coercion, no precision loss. A PR review requested switching to BIP-44 mnemonic derivation, and the replacement code used `bytesToNumber` from viem without noticing it returns a JavaScript `Number` rather than a `BigInt`.

### 1.3 Affected Scope

The vulnerability affects **all pools, all assets, and both key derivation modes**.

The frontend supports two ways to generate a mnemonic:

**Mode 1: Manual mnemonic.** The user provides or generates a BIP-39 mnemonic directly.

**Mode 2: Wallet signature.** The frontend calls `signTypedData` on the user's wallet, extracts the `r` component (32 bytes) from the ECDSA signature, and derives a mnemonic via HKDF-SHA256:

```
signTypedData("Derive Account Seed", addressHash)
    │
    ▼ HKDF-Extract(IKM = sig.r, salt = address_bytes)
    │
    ▼ HKDF-Expand(info = "privacy-pools/wallet-seed:v1|v2")
    │
entropy (16 bytes v1 / 32 bytes v2)
    │
    ▼ mnemonicFromEntropy()
    │
mnemonic (12 words v1 / 24 words v2)
```

Regardless of the source, both modes feed the mnemonic into the same SDK path:

```
Mnemonic (manual or signature-derived)
    │
    ├── m/44'/60'/0'/0/0 → privateKey → bytesToNumber() → k0 (53 bits)
    └── m/44'/60'/1'/0/0 → privateKey → bytesToNumber() → k1 (53 bits)
                                              │
                                     Used for ALL pools
                                  (ETH, wBTC, USDC, USDT, DAI, USDS)
```

The v2 signature path is particularly ironic: HKDF produces 256 bits of entropy, the 24-word mnemonic encodes it faithfully, PBKDF2 produces a 512-bit seed, BIP-32 derives a 256-bit private key, and `bytesToNumber` crushes it to 53 bits at the final step.

On-chain data from ETH pools alone shows:

- 3,747 deposits totaling ~2,711 ETH
- 3,249 partial withdrawals totaling ~1,667 ETH
- ~1,044 ETH in residual commitments still in the pool
- 0 full withdrawals observed (all withdrawals are partial. This is user behavior, not a protocol limitation; the circuit, contract, and frontend all support full withdrawals)
- 2,160 unique depositors

---

## 2. Cryptographic Structure

### 2.1 Full Derivation Diagram

```
k0 (53 bits)                                         k1 (53 bits)
     │                                                    │
 Poseidon₁(k0)                                      Poseidon₁(k1)
     │                                                    │
 masterNullifier (mn)                              masterSecret (ms)
     │                                                    │
     ├──────────── DEPOSIT ──────────────────────────────┤
     │                                                    │
 P₃(mn, scope, index)                           P₃(ms, scope, index)
     │                                                    │
 deposit.nullifier                               deposit.secret
     │                                                    │
     │              ┌────────────────────────────────────┘
     │              │
     │        P₂(nullifier, secret)
     │              │
     │        precommitmentHash  ←── on-chain (Deposited event)
     │              │
     │        P₃(value, label, precommitmentHash)
     │              │
     │        commitment  ←── on-chain (Deposited event)
     │
 P₁(deposit.nullifier)
     │
 spentNullifier  ←── on-chain (Withdrawn event)
     │
     ├──────────── WITHDRAWAL (residual) ────────────────┤
     │                                                    │
 P₃(mn, label, wIndex)                          P₃(ms, label, wIndex)
     │                                                    │
 withdrawal.nullifier                            withdrawal.secret
     │                                                    │
     │              ┌────────────────────────────────────┘
     │              │
     │        P₂(w.nullifier, w.secret)
     │              │
     │        newPrecommitmentHash
     │              │
     │        P₃(residualValue, newLabel, newPrecommitmentHash)
     │              │
     │        newCommitment  ←── on-chain (Withdrawn event)
```

### 2.2 Attack Scenarios

Two attack scenarios exist depending on available on-chain data:

**Scenario A: Deanonymization only (k0 sufficient)**

If the deposit has been partially withdrawn, the `spentNullifier` is on-chain. Recovering k0 reveals the `masterNullifier`, which links deposit addresses to withdrawal addresses across all pools for that user.

```
For each k0 candidate (2^52 values per shift):
  mn = Poseidon₁(k0)
  nullifier = Poseidon₃(mn, scope, label)    ← public from Deposited event
  nh = Poseidon₁(nullifier)
  Compare nh to spentNullifier               ← public from Withdrawn event
```

**Scenario B: Full key recovery + theft (k0 + k1)**

Once k0 is known, k1 can be recovered via the precommitmentHash:

```
Passe 1: find k0 via spentNullifier:         2^52 candidates
Passe 2: find k1 via precommitmentHash:       2^52 candidates
                                              ─────
Total:                                         2^53 = 2 × 2^52
```

With both master keys, the attacker can forge withdrawal proofs and steal residual funds.

**Scenario C: Precommitment only (no withdrawal)**

For deposits that have never been withdrawn, only the `precommitmentHash` is on-chain. Recovery requires guessing both k0 and k1 simultaneously: 2^52 × 2^52 = **2^104, which is infeasible**.

### 2.3 Enumeration Space

IEEE 754 `Number()` produces a mantissa in [2^52, 2^53) for any normalized double. The shift depends on the original key's bit length:

| Shift | Bit-length | Probability | Search order |
|-------|-----------|-------------|--------------|
| 203 | 256 bits | 50.0% | 1st |
| 202 | 255 bits | 25.0% | 2nd |
| 204 | 257 bits (rounding overflow) | ~0.1% | 3rd |
| 201 | 254 bits | 12.5% | 4th |
| 200 | 253 bits | 6.25% | 5th |
| 199 | 252 bits | 3.12% | 6th |
| 198 | 251 bits | 1.56% | 7th |
| 205 | > 257 bits | negligible | 8th |

Total search space: 8 × 2^52 = **2^55 candidates** for exhaustive coverage, though shift 203 alone covers 50% of all keys.

The enumeration is uniform within each shift: no mantissa value is more probable than another. IEEE 754 round-to-nearest-even creates equal-sized bins of ~2^203 original keys per mantissa.

---

## 3. Real-World Attack Cost

### 3.1 Methodology

We built a complete brute-force pipeline implementing Poseidon BN254 (x^5 S-box, circomlibjs-compatible constants) with four progressively optimized versions:

| Implementation | fr_mul cycles | Chain throughput | Speedup |
|---|---|---|---|
| Schoolbook (C, `uint128`) | 479 cy | 3,968/s | 1.00× |
| CIOS (C, fused mul+reduce) | 168 cy | 7,117/s | 1.79× |
| ADX inline (`mulx` BMI2) | 126 cy | 8,432/s | 2.12× |
| ADX2 `.S` (`mulx`+`adcx`/`adox`) | 128 cy | 8,240/s | 2.08× |

*Measured on Intel i7 (ThinkPad P14s Gen4), 14 cores, 2.19 GHz.*

The ADX inline variant performs best on this microarchitecture. Intel Golden Cove's out-of-order execution reorders the inline `mulx`+`adc` better than the rigid `.S` assembly.

GPU comparison (RTX A500 Laptop, 15W TGP): **25,227 cand/s**, slower than the 14-core CPU at ~59,000 cand/s. Montgomery 256-bit arithmetic on GPU suffers from long dependency chains in 32-bit limb representation.

### 3.2 Validation

End-to-end validation: 1,000 vulnerable deposits generated in JavaScript (circomlibjs, same Poseidon as the SDK), brute-forced in C. Result: **1,000/1,000 keys recovered, 0 false negatives, 0 false positives.**

### 3.3 Cost Estimates

Based on measured throughput scaled to datacenter GPUs:

| GPU | Estimated rate | Spot price | Cost for 2^53 |
|---|---|---|---|
| **RTX 4090** | ~1.4M cand/s | $0.30/h | **~$540K** |
| A100 SXM 80GB | ~650K cand/s | $0.90/h | ~$3.4M |
| H100 SXM 80GB | ~1.1M cand/s | $1.80/h | ~$4.0M |

The RTX 4090 offers the best cost efficiency at $0.06 per billion candidates.

| Fleet size | Duration | Daily cost |
|---|---|---|
| 100 RTX 4090 | ~750 days | $720/day |
| 500 RTX 4090 | ~150 days | $3,600/day |
| 4,000 RTX 4090 | ~19 days | $28,800/day |

**Important caveat:** these estimates use our naive CUDA kernel. An optimized Poseidon GPU implementation (lazy reductions, lookup tables, high occupancy scheduling) could achieve 3-5× improvement, bringing the realistic attack cost down to **$100K–$180K**.

Even at the optimistic end, this cost exceeds nearly all individual deposits. The median deposit is 0.1 ETH (~$200), and only 48 deposits exceed 10 ETH. The largest depositors (whales with 50-100 ETH positions) have likely already migrated following the public disclosure. The attack remains economically viable only if targeting a large number of accounts simultaneously or if the attacker's goal is deanonymization rather than fund theft.

---

## 4. Additional Design Concerns

### 4.1 BIP-44 Path Reuse

Privacy Pools derives k0 and k1 from standard Ethereum BIP-44 paths:

```
k0 = privateKey of m/44'/60'/0'/0/0   ← standard Ethereum account #0
k1 = privateKey of m/44'/60'/1'/0/0   ← standard Ethereum account #1
```

These are the same keys MetaMask would derive. If a user shares a mnemonic between their Ethereum wallet and Privacy Pools, the key controlling their ETH is the same key used as a Poseidon input. The SDK documentation warns "this wallet should only be used for using Privacy Pools", which indicates that 0xbow is aware of this issue but chose a workaround over a proper fix.

### 4.2 Global Master Keys

The two master keys (`masterNullifier`, `masterSecret`) are derived once and reused for every deposit across all pools and chains. Compromising either key from a single deposit compromises all deposits for that user.

---

## 5. Kohaku: Not Affected

The Ethereum Foundation's [Kohaku wallet](https://github.com/ethereum/kohaku) integrates Privacy Pools through a completely independent implementation that was never vulnerable to this bug.

### 5.1 Key Derivation Comparison

| | 0xbow SDK | Kohaku |
|---|---|---|
| **Source** | [crypto.ts](https://github.com/0xbow-io/privacy-pools-core/blob/dev/packages/sdk/src/crypto.ts) | [keys.ts](https://github.com/ethereum/kohaku/blob/master/packages/privacy-pools/src/account/keys.ts) |
| BIP-32 path | `m/44'/60'/{accountIndex}'/0/0` | `m/28784'/1'/{account}'/{type}'/{deposit}'/{idx}'` |
| Purpose | 44 (standard ETH) | 28784 (`0x7070` = "pp") |
| Key scope | Global master keys (reused everywhere) | Per-deposit unique secrets |
| Conversion | `bytesToNumber` → `Number` (53 bits) ✗ | `deriveAt()` → `Hex` → `BigInt` (256 bits) ✓ |
| Domain separation | None (no chainId in derivation) | `Poseidon(chainId, entrypoint, secret)` |
| HW wallet ready | No (HD wallet in memory) | Yes (`Keystore.deriveAt()` abstraction) |

### 5.2 Architecture

Kohaku's implementation was written by Fat Solutions in commit [`dbeef1a`](https://github.com/ethereum/kohaku/commit/dbeef1add72054c262b27da966295ff5923ab9de) (March 11, 2026). It never imported or referenced `crypto.ts` from the 0xbow SDK. The shared circuits (`@fatsolutions/privacy-pools-core-circuits`) are compatible (same Poseidon, same circuit signals), but the derived values are completely different.

**Key design improvements in Kohaku:**

1. **Custom derivation path** (`m/28784'/1'/...`), avoiding collision with standard Ethereum keys.

2. **Per-deposit secrets**: each deposit derives fresh `nullifier` and `salt` from a unique HD path including `depositIndex` and `secretIndex`. Compromising one deposit does not reveal others.

3. **Keystore abstraction**: the `deriveAt(path: string): Hex` interface is explicitly designed for hardware wallet integration:

```typescript
/**
 * @todo Figure out how we can make this work for hardware wallets,
 * especially with railgun which should be capable of working natively.
 */
export type Keystore = {
    deriveAt(path: string): Hex;
};
```

4. **Domain separation**: secrets are hashed with `chainId` and `entrypointAddress`, preventing cross-chain replay attacks.

### 5.3 Incompatibility

Deposits made with the 0xbow SDK cannot be recovered with Kohaku, and vice versa. The two implementations produce entirely different nullifiers and commitments from the same mnemonic. Users who deposited via the 0xbow frontend must use the 0xbow SDK (with the `bytesToBigInt` fix) to recover their funds.

---

## 6. Mitigation

### 6.1 For Users

Users who deposited through the 0xbow frontend before the fix should **ragequit** their deposits proactively. The `ragequit()` function is permissioned: only the original depositor (`msg.sender`) can call it, giving legitimate users a structural advantage over any attacker.

### 6.2 For 0xbow

The `bytesToBigInt` fix addresses the immediate entropy loss, but the architectural issues (BIP-44 path reuse, global master keys) remain. A migration to per-deposit derivation similar to Kohaku's design would reduce the attack surface.

### 6.3 For the Ecosystem

This vulnerability class (implicit type coercion silently truncating cryptographic material) is endemic to dynamically typed languages. Embedded implementations (C, Rust, hardware wallets) do not have implicit `BigInt` to `Number` conversion, making this class of bugs impossible by construction.

---

## 7. Timeline

| Date | Event |
|---|---|
| 21 Feb 2025 | Safe implementation: `keccak256(seed)` → `BigInt` (commit `fa0a985`) |
| 26 Feb 2025 | Bug introduced: `bytesToNumber` replaces safe code (commit `7e770b4`) |
| 31 Mar 2025 | Privacy Pools mainnet launch |
| 4 Mar 2026 | Migration flow wired into frontend (branch `feat/entropy-upgrade`) |
| 5 Mar 2026 | Fix: `bytesToNumber` to `bytesToBigInt` (commit `00773cb`, `dev` branch only) |
| 6 Mar 2026 | First migrations on-chain via internal relayer `0x35c068...` |
| 9 Mar 2026 | Migration banner env var added to frontend |
| 11 Mar 2026 | Maintenance banner deployed; Kohaku V1 Plugin (commit `dbeef1a`) |
| 16 Mar 2026 | Dead code `keys.ts` removed from 0xbow SDK (commit `13d53f0`) |
| 19 Mar 2026 | PR #186 `feat/entropy-upgrade` merged into main |
| 23 Mar 2026 | Frontend v2.11.1 released with migration support |
| 26 Mar 2026 | 82 migrations completed out of 3,747 deposits (2.2%) |

---

## 8. Migration Analysis

### 8.1 Deployment Verification

Inspection of the JavaScript bundles served by privacypools.com (Vercel deployment `dpl_82oJ1if2qwzw5R6Qxub86wZneXk7`) confirms that both `bytesToNumber` (legacy account support) and `bytesToBigInt` (safe account) are present in the production code, along with `legacyAccount` migration logic. The fix is live.

Note that the published SDK on npm (`@0xbow/privacy-pools-core-sdk` v1.2.0) and the GitHub releases (v1.2.0, v1.2.1) do **not** contain the fix. The frontend deployment uses an unpublished build from the `dev` branch.

### 8.2 Migration Mechanism

The SDK now derives two accounts from the same mnemonic on every login: a **safe account** (`bytesToBigInt`, 256 bits) and a **legacy account** (`bytesToNumber`, 53 bits). The legacy account is used to discover existing deposits on-chain.

Migration is a withdrawal with `withdrawnValue = 0`: the legacy nullifier is spent, and a new commitment is created with safe keys. The residual value transfers from legacy to safe keys without moving any ETH. The contract sees a normal withdrawal; there is no on-chain distinction between a migration and a regular withdrawal.

Zero-value withdrawals did not exist before the fix. Scanning all `Withdrawn` events from the ETH pool deployment to March 26, 2026, in 25,000-block chunks (~3.5 days each):

```
Blocks 22167000-24567095  (Mar 2025 - Feb 2026):  0 migrations
Blocks 24567096-24592096  (early Mar):            0 migrations  / 25 events
Blocks 24592097-24617097  (~6 Mar):               1 migration   / 24 events
Blocks 24617098-24642098:                         2 migrations  / 42 events
Blocks 24642099-24667099:                         1 migration   / 38 events
Blocks 24667100-24692100:                         0 migrations  / 47 events
Blocks 24692101-24717101:                         7 migrations  / 44 events
Blocks 24717102-24742102  (~23-26 Mar):          71 migrations  / 113 events
                                                 ──
Total:                                           82 migrations  / 3,323 events
```

All 82 zero-value events appear after the fix commit (March 5). The burst of 71 in the last chunk coincides with the v2.11.1 frontend release on March 23.

### 8.3 On-Chain Data

Scanning all `Withdrawn` events on the ETH pool (`0xf241d5...`) from deployment to March 26, 2026:

```
Total withdrawals:      3,323
Migrations (value=0):      82  (2.5%)
Normal withdrawals:     3,241
Ragequits (all time):    ~200  (stable rate, no post-fix spike)
```

All 82 explicit migrations pass through a **dedicated relayer** (`0x35c068...`), distinct from the historical relayer (`0x6818809E...`). The first migration appeared on-chain on March 6, one day after the fix commit. 71 of the 82 occurred in the final 3 days (March 22-26), coinciding with the v2.11.1 frontend release on March 23.

### 8.4 Silent Migrations

Since v2.11.1, any withdrawal made through the updated UI automatically generates the `newCommitment` with safe keys. The user is not necessarily aware that a migration occurred. These silent migrations are indistinguishable on-chain from regular withdrawals: both have `withdrawnValue > 0` and pass through the standard relayer.

Comparing withdrawal traffic before and after the fix:

```
16 Feb - 6 Mar (before):  221 withdrawals / 18 days = 12.3/day
 6 Mar - 26 Mar (after):  287 withdrawals / 20 days = 14.4/day
                          287 - 82 migrations       = 10.3/day organic
```

Organic withdrawal traffic has slightly decreased post-fix. The apparent increase is entirely accounted for by the 82 explicit migrations. No evidence of significant silent migration activity through the standard relayer.

### 8.5 Migration Coverage

As of March 26, 2026:

```
Total deposits:             3,747
Explicit migrations:           82  (2.2%)
Possible silent migrations:    unknown (likely small)
Unprotected deposits:       ~3,600+ (97%+)
```

Deposits that have not had any withdrawal since March 23 remain entirely under 53-bit legacy keys. Migration only occurs when a user interacts with the updated frontend. Users who have not opened privacypools.com since the update are not protected.

### 8.6 Response Timeline

The bug was live in production for approximately 12 months (March 2025 to March 2026). Once identified, the technical response was thorough: dual-account scanning, legacy support, dedicated migration relayer, and a migration banner in the UI.

The internal team began migrating deposits 17 days before the public frontend release (March 6 vs March 23). During this window, new deposits continued to be created with vulnerable 53-bit keys on the public-facing UI. No public advisory was issued, and deposits were not paused. The migration code was developed, tested, and deployed in 18 days from fix to production, which included building the dual-account architecture, migration UI, and a dedicated relayer.

---

## 9. Conclusion

This vulnerability differs from the Trust Wallet incident (2023), where a PRNG seeded with 32 bits of entropy allowed a single brute-force pass to recover **all** affected wallets simultaneously. In Privacy Pools, the 2^53 search space must be exhausted **per user**. Each deposit has a unique `(scope, label)` pair, meaning the attacker must run a separate Poseidon chain for each target. There is no shortcut that amortizes the cost across victims.

This per-user cost structure, combined with the $100K–$540K compute requirement, makes large-scale exploitation economically impractical for all but the highest-value targets. The probability of this attack being deployed in practice remains low. That said, the deanonymization risk (k0 alone, single pass of 2^52) may be more attractive to state-level adversaries seeking to break privacy rather than steal funds. Problem is past transactions cannot be patched, you can't withdraw your privacy. A similar concern is rising considering harvest now, decrypt later with the PQ threat.

Cryptographic key material should never transit through dynamically typed representations. Whether the implementation language is JavaScript, Python, or any other language with implicit numeric coercion, the risk of silent precision loss is always present. Embedded implementations (C, Rust, hardware secure elements) enforce explicit type handling at every step, eliminating this class of vulnerability entirely.

We detected a similar type coercion flaw in a client's proof of concept before it was pushed to production. Because our embedded stack implements field arithmetic and protocol logic at the lowest level (C + assembly), with no external dependencies, every encoding must be explicitly understood and validated against reference test vectors. This double implementation acts as a free audit: if the embedded version does not match the reference, the bug surfaces immediately. Code, unlike audits, does not LGTM.

---

## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found typo, or want to improve the note ? Our blog is open to PRs.</small>
