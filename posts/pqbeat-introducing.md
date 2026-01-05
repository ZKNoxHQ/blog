[category]: <> (General)
[date]: <> (2026/01/05)
[title]: <> (Introducing PQbeat: A Post-Quantum Readiness Tracker for Ethereum)


The quantum threat to blockchain cryptography is no longer a theoretical exercise. With NIST finalizing post-quantum standards in 2024 and major technology companies announcing quantum computing milestones, the question has shifted from "if" to "when." For the Ethereum ecosystem — securing hundreds of billions in value through ECDSA signatures — this transition requires coordination, transparency, and measurable progress. 
Today we introduce <a href="https://pqbeat.zknox.com" style="color: #6D28D9">PQbeat</a>, a public tracker that evaluates the post-quantum preparedness of L1/L2 chains, wallets, and protocols across the Ethereum ecosystem.

<p align="center">
<a href="https://pqbeat.xyz">
<img src="../../../../../images/pqbeat.png" alt="drawing" class="center" width="700"/>
</a>
</p>



## <span style="color: #6D28D9;">The Problem: No Visibility Into Readiness</span>

The Ethereum community has no standardized way to assess post-quantum preparedness. Roadmaps are published, research papers are written, but there is no objective measurement of what has actually been deployed and tested in production.

This creates multiple risks. Users cannot evaluate whether their assets are protected. Developers cannot identify which infrastructure components are ready for integration. And the ecosystem cannot coordinate an orderly transition because there is no shared understanding of current capabilities.

PQbeat addresses this gap by tracking only deployed capabilities — not announcements, not roadmaps, not promises.

## <span style="color: #6D28D9;">Methodology: Stages of Readiness</span>

PQbeat evaluates entities across five stages (0-4) based on verifiable, deployed functionality. The staging system differs by entity type.

### <span style="color: #6D28D9;">L1/L2 Chains</span>

| Stage | Criteria | Technical Requirements |
|-------|----------|------------------------|
| <span style="color: #6D28D9;">**Stage 0**</span> | No PQ capability deployed | ECDSA only |
| <span style="color: #6D28D9;">**Stage 1**</span> | PQ accounts usable in production | ERC-4337 / EIP-7702 + PQ signature verification via smart contract |
| <span style="color: #6D28D9;">**Stage 2**</span> | Native PQ accounts in production | EIP-7701 + precompiles (ML-DSA, Falcon, or equivalent) |
| <span style="color: #6D28D9;">**Stage 3**</span> | Migration path operational | ZK-recovery mechanism + governance-enabled freeze |
| <span style="color: #6D28D9;">**Stage 4**</span> | Post-Quantum Consensus Layer | BLS12-381 replaced by aggregatable PQ signatures |

The progression is intentionally strict. A chain reaches Stage 1 only when users can create and operate post-quantum smart accounts in production — not on testnets, not in audits, but deployed and functional.


**The consensus layer is the easy part.** When the time comes, a coordinated hard fork will migrate all validators at once — a single, synchronized upgrade.

**The execution layer is the real challenge.** There is no hard fork for user accounts, smart contracts, or protocol governance. Each wallet must adopt PQ signatures. Each protocol must accept smart accounts. Each user must migrate their assets. This fragmented landscape — millions of independent actors with no forced upgrade path — will take years of advocacy, tooling, and incremental adoption.

### <span style="color: #6D28D9;">Stage Progression</span>

```
Stage 0 → 1 : Deploy PQ signature verifier as smart contract (high gas cost, but functional)
Stage 1 → 2 : Implement precompiles (EIP-8051/8052) + EIP-7701 native account abstraction
Stage 2 → 3 : Deploy ZK-recovery circuits + governance-enabled freeze mechanism
Stage 3 → 4 : Migrate consensus layer (BLS12-381 → aggregatable PQ signatures via STARK/WHIR)
```

Each transition represents a significant engineering effort. Stage 1 can be achieved relatively quickly with existing infrastructure. Stage 4 requires fundamental changes to the consensus mechanism.

### <span style="color: #6D28D9;">Wallets</span>

Wallets inherit the stage of the highest-stage chain they support with full PQ smart account functionality.

| Stage | Criteria |
|-------|----------|
| <span style="color: #6D28D9;">**Stage 0**</span> | No PQ support |
| <span style="color: #6D28D9;">**Stage N**</span> | PQ smart account supported on a Stage N chain |

A wallet reaches Stage N when it can:
1. Create and manage PQ smart accounts
2. Sign transactions using post-quantum signature schemes
3. Operate on a chain that has achieved Stage N

This inheritance model reflects reality: a wallet's PQ capabilities are limited by the chains it supports.

### <span style="color: #6D28D9;">Protocols</span>

Protocols follow a simplified staging based on smart wallet compatibility and governance security.

| Stage | Criteria |
|-------|----------|
| <span style="color: #6D28D9;">**Stage 0**</span> | No PQ support — EOA-gated or ECDSA multisig only |
| <span style="color: #6D28D9;">**Stage 1**</span> | Accepts ERC-4337 / EIP-7702 smart accounts as signers |
| <span style="color: #6D28D9;">**Stage 2**</span> | Stage 1 + governance secured by PQ signatures |

A protocol that uses ERC-1271 for signature validation and accepts arbitrary smart contract accounts (without `tx.origin == msg.sender` checks) can reach Stage 1 on any Stage 1+ chain. Stage 2 requires that the protocol's own governance — typically a multisig or DAO — also uses post-quantum signatures.

Immutable protocols present an interesting case: if the contract logic is frozen but accepts smart accounts, it achieves Stage 1 permanently. The governance component of Stage 2 is marked as not applicable.

## <span style="color: #6D28D9;">What PQbeat Tracks</span>

### <span style="color: #6D28D9;">Chains</span>

For each L1 and L2, PQbeat evaluates:

- <span style="color: #6D28D9;">**PQ Signature Verifier**</span>: Is there a deployed contract or precompile that can verify ML-DSA, Falcon, or other NIST-approved PQ signatures?
- <span style="color: #6D28D9;">**Account Abstraction Support**</span>: Is ERC-4337, EIP-7702, or EIP-7701 available in production?
- <span style="color: #6D28D9;">**Precompile Status**</span>: Are gas-efficient precompiles for PQ verification deployed or in active development?
- <span style="color: #6D28D9;">**Recovery Infrastructure**</span>: Is a ZK-recovery mechanism deployed that would allow emergency migration?
- <span style="color: #6D28D9;">**Consensus PQ Readiness**</span>: What is the status of replacing BLS signatures in the consensus layer?

### <span style="color: #6D28D9;">Wallets</span>

For hardware and software wallets:

- <span style="color: #6D28D9;">**PQ Algorithm Support**</span>: Which post-quantum signature schemes are implemented?
- <span style="color: #6D28D9;">**Smart Account Compatibility**</span>: Can the wallet create and manage ERC-4337/7702 accounts?
- <span style="color: #6D28D9;">**Chain Coverage**</span>: On which Stage 1+ chains does the wallet operate?
- <span style="color: #6D28D9;">**Key Derivation**</span>: Does the wallet support PQ-compatible derivation paths while preserving seed phrase compatibility?

### <span style="color: #6D28D9;">Protocols</span>

For DeFi protocols and applications:

- <span style="color: #6D28D9;">**Smart Account Acceptance**</span>: Can users interact via ERC-4337 accounts?
- <span style="color: #6D28D9;">**ERC-1271 Support**</span>: Does the protocol properly validate smart contract signatures?
- <span style="color: #6D28D9;">**Governance Security**</span>: Is the protocol's governance mechanism PQ-secured?
- <span style="color: #6D28D9;">**TVL Exposure**</span>: What value is at risk if the protocol remains at Stage 0?

## <span style="color: #6D28D9;">Tracked Entities</span>

PQbeat tracks three categories of entities across the Ethereum ecosystem.

### <span style="color: #6D28D9;">L1/L2 Chains</span>

| Chain | Stage | Precompiles | EIP-7701 | ZK-Recovery | Notes |
|-------|-------|-------------|----------|-------------|-------|
| Ethereum | 0 → 1 | ❌ | ❌ | ❌ | ZKNOX contracts pending deployment |
| Arbitrum | 0 → 1 | ❌ | ❌ | ❌ | Inherits L1 contracts |
| Base | 0 → 1 | ❌ | ❌ | ❌ | Inherits L1 contracts |
| Optimism | 0 → 1 | ❌ | ❌ | ❌ | Inherits L1 contracts |
| Starknet | 0 | ❌ | ❌ | ❌ | STARK-native, no PQ sig verifier deployed |

Ethereum L1 will transition to Stage 1 once post-quantum signature verification contracts are deployed in production. L2s that inherit L1 contract availability (Arbitrum, Base, Optimism) will transition simultaneously.

### <span style="color: #6D28D9;">Wallets</span>

| Wallet | Stage | PQ Smart Account | Type | Notes |
|--------|-------|------------------|------|-------|
| ZKNOX Kohaku | 1 | ML-DSA, Falcon | Software | ERC-4337 smart accounts |
| Ledger | 0 | ❌ | Hardware | No PQ support |
| Trezor | 0 | ❌ | Hardware | No PQ support |
| MetaMask | 0 | ❌ | Software | No PQ support |
| Safe | 0 | ❌ | Software | ECDSA signers only |
| Rabby | 0 | ❌ | Software | No PQ support |

Hardware wallets represent a critical dependency. Until vendors like Ledger and Trezor implement PQ signature generation, users must choose between hardware security and post-quantum protection.

### <span style="color: #6D28D9;">Protocols</span>

| Protocol | Stage | 4337/7702 Support | Governance PQ | Notes |
|----------|-------|-------------------|---------------|-------|
| Uniswap V3 Core | 2 | ✅ Permissionless | N/A (immutable) | No admin keys |
| Uniswap Governance | 1 | ✅ | ❌ ECDSA DAO | UNI token voting |
| Aave V3 | 1 | ✅ Permissionless + ERC-1271 | ❌ ECDSA multisig | |
| Compound V3 | 1 | ✅ Permissionless | ❌ ECDSA multisig | |
| MakerDAO | 1 | ✅ Permissionless | ❌ ECDSA multisig | |
| Lido | 1 | ✅ Permissionless | ❌ ECDSA multisig | Large TVL exposure |
| CoW Protocol | 1 | ✅ ERC-1271 | ❌ ECDSA | Intent-based, smart wallet compatible |
| 1inch Fusion | 1 | ✅ ERC-1271 | ❌ ECDSA | Order signing via smart wallets |
| UniswapX | 1 | ✅ ERC-1271 | ❌ ECDSA | Dutch auction with smart wallet support |
| Safe Multisig | 0 | ⚠️ ERC-1271 signers | ❌ ECDSA signers | Signers must use ECDSA |
| ENS | 1 | ✅ Permissionless | ❌ ECDSA DAO | |

Most major DeFi protocols are permissionless and accept any `msg.sender`, making them compatible with ERC-4337/EIP-7702 smart wallets by default. The primary vulnerability lies in governance mechanisms, which remain secured by ECDSA multisigs or DAOs.

Immutable protocols (like Uniswap V3 Core) achieve Stage 2 automatically — there is no governance to compromise.

---

## <span style="color: #6D28D9;">Roadmap: Current Initiatives</span>

### <span style="color: #6D28D9;">Ethereum Protocol Efforts</span>

| Initiative | Status | Description |
|------------|--------|-------------|
| <span style="color: #6D28D9;">**EIP-8051**</span> | Draft | Precompile for ML-DSA (FIPS-204) signature verification |
| <span style="color: #6D28D9;">**EIP-8052**</span> | Draft | Precompile for Falcon signature verification |
| <span style="color: #6D28D9;">**EIP-7701**</span> | Draft | Native account abstraction for efficient smart accounts |
| <span style="color: #6D28D9;">**PQ Consensus Layer**</span> | Research | Replacing BLS12-381 with aggregatable PQ signatures |
| <span style="color: #6D28D9;">**ZK Recovery Mechanism**</span> | Research | Circuits for seed-based account recovery post-freeze |

### <span style="color: #6D28D9;">Stage Progression Dependencies</span>

```
Stage 0 → 1 : Deploy PQ signature verifier (smart contract)
              └─ ZKNOX: Dilithium/Falcon verifiers ready for deployment

Stage 1 → 2 : EIP-8051/8052 precompiles + EIP-7701 implementation
              └─ Reduces verification cost from ~5M gas to ~50k gas

Stage 2 → 3 : ZK-recovery circuits + governance freeze mechanism
              └─ Requires ecosystem coordination for emergency procedures

Stage 3 → 4 : Consensus layer migration
              └─ BLS12-381 → PQ aggregatable signatures (STARK/WHIR)
              └─ ~1GB per epoch without aggregation; requires ZK compression
```

### <span style="color: #6D28D9;">Identified PQ Projects</span>

| Project | Focus | Status |
|---------|-------|--------|
| <span style="color: #6D28D9;">**ZKNOX**</span> | Smart accounts, signature verifiers, EIPs | Active development |
| <span style="color: #6D28D9;">**Ethereum Foundation PQ Research**</span> | Protocol-level migration planning | Active research |
| <span style="color: #6D28D9;">**NIST PQC Standards**</span> | ML-DSA (FIPS-204), Falcon, SPHINCS+ | Finalized (2024) |
| <span style="color: #6D28D9;">**Tetration Lab**</span> | Emergency hard fork mechanisms | Research |

---

## <span style="color: #6D28D9;">Current State Summary</span>

As of December 2025, the Ethereum ecosystem is predominantly at Stage 0. Most chains have no deployed PQ verification capability. Most wallets cannot sign with post-quantum algorithms. Most protocol governance relies entirely on ECDSA.

This is expected. The transition is early. But it underscores the importance of tracking progress systematically.

The path to Stage 1 is imminent — ZKNOX contracts for ML-DSA and Falcon verification are pending deployment. Once live, any ERC-4337 or EIP-7702 wallet can create post-quantum secured accounts on Ethereum mainnet.

The path to Stage 2 depends on EIP-8051 and EIP-8052 precompile adoption, which would reduce signature verification costs by two orders of magnitude.

The path to Stage 3 and 4 requires significant protocol-level coordination that has not yet begun in earnest.

## <span style="color: #6D28D9;">Why This Matters</span>

The post-quantum transition is not a single event but a multi-year process. Assets secured by ECDSA today will remain vulnerable until they are migrated to PQ-secured accounts. The longer this takes, the greater the exposure window.

PQbeat provides three functions:

1. <span style="color: #6D28D9;">**Transparency**</span>: Users can evaluate the security posture of chains, wallets, and protocols they rely on
2. <span style="color: #6D28D9;">**Coordination**</span>: Developers can identify bottlenecks and prioritize integration work
3. <span style="color: #6D28D9;">**Accountability**</span>: The ecosystem can measure progress against stated goals

The tracker is designed to be objective and verifiable. Claims are evaluated against deployed code, not roadmaps.

## <span style="color: #6D28D9;">Contributing</span>

PQbeat is maintained by ZKNOX as a public resource. The data model is designed for community contribution:

- Chain, wallet, and protocol entries are stored as structured data
- Stage assessments follow documented criteria
- Pull requests with evidence of deployed capabilities are welcome

If your project has achieved a higher stage than currently listed, submit evidence of deployed functionality. If you identify errors in our assessments, open an issue.

## <span style="color: #6D28D9;">Conclusion</span>

The quantum threat to Ethereum is real but manageable — if the ecosystem transitions in an orderly manner. PQbeat exists to make that transition visible.

Stage 3 readiness — with ZK-recovery deployed and freeze mechanisms available — represents the minimum insurance policy against an accelerated quantum timeline. Even if we are fortunate enough to reach Stage 4 gracefully, having Stage 3 infrastructure ready is prudent risk management.

Track the ecosystem's progress at [pqbeat.zknox.com](https://pqbeat.zknox.com).

---

## <span style="color: #6D28D9;">References</span>

- [Post-Quantum Readiness in EdDSA Chains](https://eprint.iacr.org/2025/1368.pdf)
- [How to hard-fork to save most users' funds in a quantum emergency](https://ethresear.ch/t/how-to-hard-fork-to-save-most-users-funds-in-a-quantum-emergency/18901)
- [EIP-8051: ML-DSA Signature Verification Precompile](https://eips.ethereum.org/EIPS/eip-8051)
- [EIP-8052: Falcon Signature Verification Precompile](https://eips.ethereum.org/EIPS/eip-8052)

---

## <span style="color: #6D28D9;">Reach Us</span>

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact](mailto:gm@zknox.com)

<small>Found a typo or want to improve this post? Our blog is open to PRs.</small>

*ZKNOX — Post-Quantum Cryptography for Ethereum*
