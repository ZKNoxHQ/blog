[category]: <> (General)
[date]: <> (2026/03/13)
[title]: <> (Unlimited public computation in constrained hardware using ZK proofs — Application to ZK clear signing)

<p align="center">
<img src="../../../../../images/nanozkp.png" alt="zk clear signing" class="center"/>
</p>

## Introduction

Today we are releasing three things simultaneously: the first complete BLS12-381 pairing implementation running natively inside a hardware wallet secure element, a full Groth16 verifier running in that same device, and a complete ZK clear signing circuit for Aave v3 with working end-to-end examples. Together, they form something we believe has never been done before: end-to-end ZK proof verification entirely within a hardware wallet secure element, applied to a real production protocol.

All three components are functional and released before ETHCC: the verifier, the Circom circuit covering 13 Aave v3 actions, and the test vectors proving the full pipeline from raw calldata to verified proof.

This post describes the general principle behind delegating arbitrary public computations to constrained verifiers, then applies it to clear signing, and finally proposes a trust model that eliminates the need for any metadata signing server by anchoring the verification key directly in the protocol's smart contract.


## The general principle: delegating computation without trust

Consider a program `f(x) = y`. A constrained verifier — a smart contract, a microcontroller, a hardware wallet — holds `y` and wants to be certain that someone correctly computed `f` on a valid input `x`. Without zero-knowledge proofs, the only option is to rerun the computation, which requires the resources to do so and trust that the input wasn't altered.

With a succinct proving system like Groth16, the prover executes `f`, generates a constant-size proof `π` (~200 bytes), and the verifier checks `π` in *O(1)* time — regardless of the complexity of `f`. Verification reduces to a pairing equation on an elliptic curve:

```
e(π.A, π.B) · e(-α, β) · e(-vk_x, γ) · e(-π.C, δ) == 1 ∈ Fp12
```

where `vk_x = IC[0] + Σ (pub_i · IC[i+1])` is a linear combination of the public signals, computed via scalar multiplication and point addition on G1.

The critical property: the verifier needs only the verification key `vk` — a small, static artifact baked in at circuit compilation time. It does not need to understand `f`, reexecute it, or trust the prover. The proof is either valid or it isn't.

This paradigm is powerful precisely because the verifier can be *constrained*. An Ethereum contract. A Cortex-M4 running at 64 MHz. A secure element with 512 KB of flash.

## The blind signing problem and EIP-7730

Hardware wallets sign raw bytes. When a user approves a transaction on a Ledger Nano, the device receives a serialized calldata blob — something like `0xa415bcad000000...` — and is expected to display a meaningful summary of what the user is about to sign.

This is the clear signing problem. In practice, most hardware wallets either display a truncated hex string, or rely on external metadata to decode the calldata into a human-readable string like "Borrow 0.5 WETH (variable) on Aave v3".

[EIP-7730](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7730.md) standardizes these metadata descriptors — a JSON document describing how to parse a contract's ABI into displayable fields. Ledger's clear signing initiative builds on this. The metadata is signed by a trusted server, and the wallet verifies the signature before trusting the display.

This is a good step. But it introduces a dependency: the metadata signing server. If that server is compromised, an attacker can serve fraudulent metadata that causes the wallet to display "Transfer 0.001 ETH to charity" while the user signs a drain of their entire portfolio.

The question becomes: can we eliminate this trust dependency entirely?

## The ZK approach: proving that readable faithfully represents tx

The prover — the dapp, the protocol, or any relayer — supplies both `tx` (contract address, selector, calldata) and `readable` (the human-readable string to display). Neither is secret in the cryptographic sense; "witness" simply means not transmitted to the verifier. The circuit attests that `h(tx)` and `h(readable)` are the correct hashes of their respective inputs, and that `readable` is the canonical ABI representation of `tx` according to the protocol's decoding rules.

The wallet receives `tx`, `readable`, and `π`. It recomputes `h(tx)` from the raw transaction bytes and `h(readable)` from the string, verifies `π` against those two public values, and if the proof holds, displays `readable` — with cryptographic certainty that it faithfully represents `tx`, without interpreting a single ABI byte itself.

```
                    tx, readable, π
  ┌──────────┐ ──────────────────────────────────────► ┌──────────────────┐
  │  Prover  │                                         │  Hardware Wallet │
  │  (dapp / │                                         │  secure element  │
  │ relayer) │                                         └────────┬─────────┘
  └────┬─────┘                                                  │
       │ tx, readable (witness)                       ③ receives tx, readable
       ▼                                                        │
  ┌────────────────────┐                              ④ recomputes locally
  │    ZK Circuit      │                                h(tx)  from raw bytes
  │  Groth16 BLS12-381 │                                h(readable)  from string
  │                    │                                        │
  │  h(tx) = hash(tx)  │                              ⑤ verifies π against
  │  h(rbl) = hash(rbl)│ ──► public signals ──────────  h(tx) and h(readable)
  │  readable = ABI(tx)│         h(tx)                          │
  │                    │         h(readable)           valid  → display readable
  └────────────────────┘                               invalid → reject
       │
       └──► proof π (π.A 96B | π.B 192B | π.C 96B)
```

The circuit enforces three constraints:

* `h(tx) = hash(tx)` — the public hash matches the witness transaction
* `h(readable) = hash(readable)` — the public hash matches the witness string
* `readable` is the canonical ABI representation of `tx` — selector, parameters, token registry, amount formatting all verified

The proof `π` attests that there exist inputs satisfying all three simultaneously. No metadata server. No signature from a trusted third party. The prover can be anyone.

## Anchoring the verification key in the contract

A new trust question arises: how does the wallet know the verification key `vk` is legitimate? A substituted `vk` would let an attacker forge valid proofs for arbitrary strings.

EIP-7730 solves this with a server signature. We can do better: anchor the hash of `vk` directly in the protocol's smart contract.

```solidity
// In the Aave v3 contract, or an associated registry
bytes32 public clearSigningVKHash;

function setClearSigningVK(bytes32 vkHash) external onlyGovernance {
    clearSigningVKHash = vkHash;
}
```

The wallet, on first interaction with a contract, fetches `clearSigningVKHash` from the chain and compares it to the hash of the `vk` it holds. If they match, the `vk` is authenticated by the protocol's own governance — not by a third-party server.

This has several useful properties:

* **No metadata server** — the source of truth is the contract. When the protocol updates its interface, it deploys a new circuit, updates `clearSigningVKHash` via governance, and all wallets follow automatically
* **Same trust model as the protocol itself** — trusting the `vk` is equivalent to trusting the protocol's governance parameters, which is already the implicit trust assumption when interacting with the contract
* **Fully auditable** — anyone can compile the circuit, derive the `vk`, and verify that its hash matches what's on-chain


Anchoring the verification key in the contract removes the metadata server and ties clear signing to the protocol itself. But one question remains: how do we know the circuit behind that key actually matches what the contract developer intended?

Today the circuit is written separately from the contract. Even if the key is authenticated on-chain, users still rely on the developer to ensure the circuit correctly represents the contract's semantics.

A natural solution is to derive the circuit directly from the contract specification. This is a direction currently being explored in [Verity](https://github.com/lfglabs-dev/verity) — formally verified smart contracts, from spec to bytecode. By extending the language with declarative display annotations describing how contract actions should appear to a user, the compiler could automatically generate the ERC-7730 descriptor, the corresponding ZK circuit, and the verification key. The contract itself then embeds a commitment to these verification keys. Clear signing becoming a property of the protocol itself rather than an external service.

The verification key is small (a few hundred bytes), immutable once deployed, and sufficient to verify any computation delegated through the circuit. It is, in a sense, the smart contract of the ZK layer.

## Current implementation status

Everything released today is functional. The pairing implementation (`zkn_pairing_384`), the Groth16 verifier, and the Aave v3 clear signing circuit are all working end-to-end. To our knowledge, this is the first time a complete BLS12-381 pairing and a full Groth16 verifier have run natively inside a hardware wallet secure element.

The Groth16 verifier adds the following on top of the pairing:

* scalar multiplication on G1 to compute `vk_x = Σ pub_i · IC[i]`
* point addition on G1 to accumulate the terms
* G1 negation, trivial: `neg(x, y) = (x, p - y)`, to rewrite the equation as a single multi-pairing equal to 1
* multi-pairing on 4 pairs: one Miller loop, one final exponentiation

The Circom circuit covers 13 Aave v3 actions: supply, borrow, repay, withdraw, liquidation call, flash loan, collateral management, eMode, delegation with and without signature, approve, and permit. The Groth16 proving pipeline uses snarkjs. Test vectors for all 13 actions pass end-to-end, from raw calldata to verified proof.

The circuit, the proving scripts, and the verifier C implementation are all available in the repository. The remaining integration steps involve exposing the verifier through the Ledger APDU protocol, handling the chunked transmission of the proof elements (448 bytes: `π.A` 96B, `π.B` 192B, `π.C` 96B, two 32B public signals), the verification key lookup flow, and linking `h(tx)` with `tx` itself using the Poseidon2 BLS12-381 primitive natively on the device.

## Beyond clear signing: what else can run on a constrained verifier

Clear signing is the first application, but the principle is general. Any deterministic public computation that can be encoded in a circuit can be delegated to an untrusted prover and verified in constant time on the device. The only limit is the capacity to prove.

Two directions stand out as particularly compelling for hardware wallets.

The first is chain synchronization. A hardware wallet that wants to verify the current state of a blockchain without trusting a third-party RPC must either run a full node or accept someone else's word for the chain tip. Neither is practical. ZK light clients such as Helios, or storage proof systems in the spirit of Herodotus, produce succinct proofs of consensus and state that a constrained device can verify directly. A hardware wallet running a ZK light client verifier would have trustless, self-sovereign access to on-chain state, including the verification key registry described above, without any network dependency beyond receiving the proof itself.

The second is L2 anchoring. A hardware wallet secure element, once it can verify a Groth16 proof, can serve as a trust anchor for any rollup that settles via a pairing-based proof. The device becomes capable of independently verifying the validity of an L2 state transition, not just signing a transaction that assumes it. This opens the door to hardware-enforced validity guarantees for L2 interactions, which today are entirely delegated to the rollup's sequencer and prover infrastructure.

The underlying constraint is proving capacity, not verification capacity. Verification is already solved: constant time, constant size, fits in a secure element. The question is what can be expressed as a circuit and proven efficiently enough to be practical. As proving systems improve, that frontier expands.

One direction worth watching is recursive proof composition. A Halo-like system that takes a STARK as input and wraps it in a Groth16 output would allow arbitrary computation, including incrementally verifiable computation over long sequences of state transitions, to be verified on a device that only knows how to check a pairing equation. The STARK handles the expressiveness and the recursive accumulation; the Groth16 wrapper provides the constant-size proof that the secure element can verify. The hardware wallet would not need to know anything about the inner proof system. It would only ever see a Groth16 proof and a verification key.

## Conclusion

ZK proofs are a privacy tool. Their useful  property here is the ability to delegate arbitrary deterministic computation to an untrusted prover, and verify the result in constant time on a constrained device.

Applied to clear signing, this means a hardware wallet can display a human-readable transaction summary with the same cryptographic guarantee it has over the raw transaction bytes — without relying on any external service, without requiring the device to implement protocol-specific parsing logic, and without trusting anyone except the circuit's verification key.

The verification key, in turn, can be anchored in the protocol's own governance. This closes the trust loop entirely.

We called it impossible to do. We then did it anyway.

🔐 Let's build trustless hardware wallets.

## References

  - [EIP-7730 - Clear Signing Format for Wallets](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7730.md)

  - [Groth16 - On the Size of Pairing-based Non-interactive Arguments](https://eprint.iacr.org/2016/260.pdf)

  - [BLS12-381 curve specification](https://github.com/zcash/pasta_curves/blob/main/src/spec.md)

  - [poseidon-bls12381-circom](https://github.com/iden3/poseidon-bls12381-circom)

  - [Circom 2 documentation](https://docs.circom.io)

  - [snarkjs](https://github.com/iden3/snarkjs)

  - [Aave v3 technical documentation](https://docs.aave.com/developers/core-contracts/pool)

  - [Verity](https://github.com/lfglabs-dev/verity) --- Formally verified smart contracts. From spec to bytecode.

## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found a typo, or want to improve the note? Our blog is open to PRs.</small>
