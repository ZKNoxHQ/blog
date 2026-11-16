[category]: <> (Security research, Privacy, Post-quantum)
[date]: <> (2026/11/05)
[title]: <> (Analysis of the quantum threat on the privacy of Kohaku protocols)


This blogpost is a summary of the talk ["You can't withdraw your privacy"](https://www.youtube.com/watch?v=XffwTy3S_FI) presented at Devcon 2026 in Mumbai. It digs into the technical details omitted during the presentation.

In this post we study three privacy protocols integrated in [Kohaku](https://github.com/ethereum/kohaku), the Ethereum privacy SDK: Tornado Cash, Privacy Pools and Railgun.

<img src="../../../../../images/kohaku-logo.svg" alt="Kohaku" class="transparent" width="120" style="display:block;margin:0 auto"/>

An efficient quantum computer breaks most of today's public-key cryptography. Running Shor's algorithm breaks factoring (RSA) and discrete logarithms (elliptic curves, pairings). Symmetric primitives (AES, ChaCha, hash functions) remain safe with appropriate parameters. In consequence, Ethereum must migrate the cryptography to quantum-safe primitives. This topic is tackled by several cryptographers, mostly at the _authentication_ level.


## Privacy vs authentication

The security of Ethereum relies on cryptographic primitives, and some of them are threatened by the arrival of a cryptographically relevant quantum computer. Most of the discussion so far has been about **authentication**: how transactions are validated at the execution level with a cryptographic signature, how the validators agree at the consensus level, with a signature aggregation. Justin Drake provided an overview of the situation in [this talk](https://www.youtube.com/watch?v=rqJ5ir-8hAQ) during Devcon Mumbai.

On the other side, the **privacy** of transctions is made through a construction with a ZK proof together with a Merkle tree circuit, and nullifiers (see later the details for each protocol). While a ZK proof system is perfectly zero-knowledge (input size is unbounded, but the output is succinct), even with a quantum computer, the extra elements (commitments in the Merkle tree and nullifiers) might weaken the privacy when an efficient quantum computer is able to break some of the cryptographic primitives.

The migration of a privacy-preserving protocol to a quantum-resistant privacy version has a different deadline:
- The authentication (signatures, proofs) is only at risk for transactions made *after* Q-day. A signature verified in 2026 cannot be forged retroactively: the transaction is already finalized, and after the migration, the sender of the transaction will have moved their funds to a quantum-safe account. This means that migrating before Q-day is enough.
- In contrast, the privacy is at risk *retroactively*. Every byte ever published on-chain stays there forever. An adversary does not need to act today, they only have to wait for the release of the quantum computer, and break the past privacy. This means that the privacy property must be quantum-safe *today* in order to keep the privacy. 

## A general privacy-preserving construction

In this section, we describe a simple and generic model for building private transactions. We present the keys needed for this to work, and also a first way for a quantum computer to break the privacy at the wallet level.

The idea is very simple: users deposit funds in a smart account that accepts withdrawals only for owners of the deposits. More precisely, the smart account contains a Merkle tree of note commitments. When a user deposits a note, the Merkle tree is updated with a new leaf, a commitment of the note. During a withdrawal, the user provides a nullifier of the note (preventing double spending), and a proof that the nullified note corresponds to a note of the tree. Deposits and withdrawals are public and can be observed on-chain. We can see one user depositing on the smart account, another address receiving some funds later, but the proof is zero-knowledge, meaning that it is not possible to know which deposited note corresponds to the withdrawal.

In this simple setting, withdrawing a note requires a zero-knowledge proof. Generating such a proof does not fit in a hardware wallet, which makes Tornado Cash and Privacy Pools hardware integration impossible. Railgun, on the other hand, uses a different approach (à la Zcash) and it is possible to have hardware security of the spending key.

In terms of keys, the user needs secret keys for computing the commitment and the nullifier of the note. Depending on the way these keys are derived, the privacy might be affected. Before diving into the protocols, a point that affects all three of them: how are the private secrets derived in wallets? Two approaches coexist.

- **Derivation path from the mnemonic** (originally specified by [Fat Solutions](https://www.fatsolutions.xyz/) for Kohaku): the secrets are derived from the seed with a hash-based derivation path, like any other BIP-32 key. This is **post-quantum safe** as long as the hash function is quantum-resistant (BIP-32 does, for example).
- **Derivation from an Ethereum signature** (as done in Kohaku now): the wallet signs a fixed message with the Ethereum account, and the privacy secrets are derived from the signature. One advantage of this construction is that it enables a "hardware wallet" to derive its spending keys using the existing Ethereum app, export it to a software host that would compute the ZK proof. Note that this is not hardware security because the spending key is exported to the host. More importantly (from a quantum attacker perspective), ECDSA signatures are deterministic (RFC 6979), and the public key of any account that has sent a transaction is on-chain. A quantum adversary recovers the ECDSA private key with Shor, recomputes the same signature, and derives all the privacy secrets. This is **quantum broken**, regardless of how good the privacy protocol is.

Only the first option leads to quantum privacy, and it should become the norm in wallets if the quantum-resistance is considered. We described a first way of breaking the privacy with a quantum computer at the wallet level. We now consider the protocol level, for the three protocols integrated into Kohaku.

## Kohaku protocols

### Tornado Cash <img src="../../../../../images/tornado-logo.svg" alt="Tornado Cash" class="transparent" height="30" style="vertical-align:middle"/>

Tornado Cash uses fixed-denomination pools. The construction described above is exactly what is used in this protocol. To deposit, a user samples a random nullifier $n$ and secret $s$ and publishes a commitment $c= \mathsf{Ped}(n \Vert s)$, which becomes a new leaf of a Merkle tree. To withdraw to a recipient address, the user publishes the nullifier hash $\mathsf{nf}= \mathsf{Ped}(n)$ together with a zero-knowledge proof that "$\mathsf{nf}$ corresponds to an unspent leaf of the tree". 

Both values are computed with a [Pedersen hash](https://iden3-docs.readthedocs.io/en/latest/iden3_repos/research/publications/zkproof-standards-workshop-2/pedersen-hash/pedersen.html) over the Baby Jubjub curve. A Pedersen hash is a multi-scalar multiplication: the input bits are cut into windows and each window multiplies a fixed generator. It is collision resistant under the discrete logarithm assumption, which a quantum computer breaks. More importantly, it is somehow **linear**: since $n$ is the prefix of $n \Vert s$, the nullifier contribution cancels out in $c - \mathsf{nf}$, which only depends on $s$.

#### Attacking Tornado Cash

In order to break the privacy of Tornado Cash, an attacker would use Shor's algorithm in order to compute the discrete logarithms of the generators of the Pedersen hash specification (once and for all) and of every commitment and nullifier hash ever published. Given a candidate pair $(c, \mathsf{nf})$, it gets $\delta = \mathrm{dlog}(c) - \mathrm{dlog}(\mathsf{nf})$, and checks whether $\delta$ can be written as the contribution of a 248-bit secret $s$. Concretely, $s$ spans 62 windows of 4 bits, encoded as digits in $\lbrace \pm1, \dots, \pm8 \rbrace$, so the question is to find $x \in \lbrace \pm1, \dots, \pm8 \rbrace^{62}$ such that $\sum_{i=1}^{62} c_i x_i \equiv \delta \bmod L$, where the $c_i$ are public constants derived from the generators. This is a 62-dimensional lattice problem, well within reach of standard lattice reduction once the discrete logarithms are known.
- If $(c, \mathsf{nf})$ is a genuine deposit/withdrawal pair, a solution exists. 
- If not, a solution still exists with probability about $2^{248}/2^{250.6} \approx 16\%$, since there are $2^{248}$ digit vectors for a group of order $L \approx 2^{250.6}$. These false openings are genuine openings: no algorithm can tell them apart from the real one.

This attack does not completely break the privacy, because some openings might be wrong. However, the attack reduces the number of deposits that open to a given nullifier hash. Although it does not directly output the deposit address of a given recipient address, it already shrinks the size of the pool containing the deposited notes.

#### Improvement with metadata

The quantum test becomes devastating when combined with on-chain metadata. Indeed, many users deposit several notes from the same address, and withdraw them to the same recipient address. If an address `0xa` made $k$ deposits and an address `0xb` received $k$ withdrawals, the adversary tests all the pairs. For a wrong candidate, all $k$ tests pass with probability $0.16^k$: about $2.7\%$ for two notes, $0.07\%$ for four, and $0.0003\%$ for seven.

To get a sense of how much metadata is available, we analyzed every deposit and withdrawal of the [**100 ETH pool**](https://etherscan.io/address/0xA160cdAB225685dA1d56aa342Ad8841c3b53f291) on Ethereum mainnet, up to block 26,387,275:

- 50,146 deposits from 10,506 distinct addresses, and 47,271 withdrawals to 21,109 distinct recipient addresses.
- Depositors reuse their address a lot: 89% of the deposits come from an address that deposited more than once.
- 29% of the recipient addresses received more than one withdrawal, accounting for 68% of the withdrawals.

The table below gives the number of addresses that made exactly $k$ deposits, and the number of addresses that received exactly $k$ withdrawals:

| $k$ | depositor addresses with $k$ deposits | recipient addresses with $k$ withdrawals |
|---|---|---|
| 1 | 5,577 | 15,075 |
| 2 | 1,521 | 2,287 |
| 3 | 826 | 1,156 |
| 4 | 482 | 626 |
| 5 | 373 | 463 |
| 6 | 264 | 404 |
| 7 | 193 | 206 |
| 8 | 156 | 150 |
| 9 | 99 | 127 |
| 10 | 112 | 163 |
| 11–50 | 773 | 419 |
| 51+ | 130 | 33 |

In other words, 89% of the deposits come from a reused address, and 68% of the withdrawals reach a recipient address that received several of them. For these users, the quantum test is not applied to a single note but to a group of notes, and a wrong candidate passes all the tests with probability $0.16^k$. This makes the privacy of Tornado Cash weak in practice.

The timing of the transactions shrinks the pool even more: a withdrawal can only spend a note deposited before it, so for each nullifier hash, only the earlier commitments, and the depositor addresses active at that time, are candidates. A real adversary will also combine amounts across pools, gas price habits, relayer choices, and funding of the addresses.

The conclusion for Tornado Cash is that its privacy is **seriously weakened against a quantum adversary**, and broken for the users who repeat the same deposit and withdrawal pattern. Using one-time withdrawal addresses keeps the target deposit addresses larger, but the real fix requires a contract upgrade: the commitments and nullifier hashes are already on-chain.

### Privacy Pools <img src="../../../../../images/privacypools-logo.svg" alt="Privacy Pools" class="transparent" height="30" style="vertical-align:middle"/>

Privacy Pools v1 follows the same deposit/withdraw design as Tornado Cash, with a compliance layer (Association Set Providers). The first version replaced the Pedersen hash with Poseidon, a hash function that is not based on any algebraic structure exploitable by Shor: $c = \mathsf{Pos}\bigl(v, \ell, \mathsf{Pos}(n, s)\bigr)$ and $\mathsf{nf} = \mathsf{Pos}(n)$.
Commitments and nullifiers do not leak anything to a quantum adversary: **Privacy Pools v1 is post-quantum private**.

The second version moves to a **UTXO model**: notes can be split and sent to other users inside the pool. When Alice spends her note of 123 ETH to create a note for Bob, Bob must learn that the new note is his, together with its opening $(n', s')$. This requires encryption:

- Bob registers a viewing public key $\mathsf{vk} \cdot G$ in an on-chain keystore.
- Alice samples $r$, computes a shared key $K = \mathsf{KDF}(r \cdot \mathsf{vk} \cdot G)$ with a static ECDH, and publishes the note encrypted under $K$ with XChaCha20.
- Bob recomputes $K = \mathsf{KDF}(\mathsf{vk} \cdot r G)$ and decrypts.

The symmetric encryption is quantum safe, but the ECDH is not: with Shor, the adversary recovers every viewing key $\mathsf{vk}$ from the keystore and decrypts every note ever sent. **Privacy Pools v2 encryption is quantum broken.** A fix is possible: hybrid encryption combining ECDH with a post-quantum KEM such as ML-KEM. There are subtleties for implementing hybrid encryption properly. There exist standards for hybrid encryption (in TLS or Signal messenger, for example), keeping the privacy introduces a layer of complexity. Two properties are at stake, and they do not combine the same way:
- **Confidentiality**: with $K = H(K_{\mathsf{ecdh}} \Vert K_{\mathsf{kem}} \Vert \dots)$, the note stays confidential as long as *either* ECDH *or* ML-KEM holds. Breaking it requires breaking both.
- **Key privacy** (who is the sender, who is the recipient): every public value tied to a key can leak this information. It is broken as soon as *any* of them leaks.

### Railgun <img src="../../../../../images/railgun-logo.svg" alt="Railgun" class="transparent" height="30" style="vertical-align:middle"/>

Railgun is a UTXO protocol: funds are *shielded* into the pool, transferred privately between `0zk` addresses, and *unshielded* back. Railgun has an important design advantage, *à la* Zcash: the spending authorization is a **signature verified inside the ZK proof**. The hardware wallet holds the spending key and signs the transaction $\sigma = \mathsf{Sign}_{sk}(\mathsf{tx})$. The host computes the proof using $\sigma$, without ever learning the spending key, and the signature authorizes this transaction only. Railgun therefore provides real **hardware security** of the spending key.

As in Privacy Pools v2, notes are encrypted to their recipient with an ECDH-based scheme, and suffer from the **same quantum break**. The same fix as for Privacy Pools is possible, and we implemented a proof of concept for it.

#### PQ Railgun

We built a proof of concept of a post-quantum private Railgun wallet, available at [pq-railgun.netlify.app](https://pq-railgun.netlify.app):

- Keys are derived through a derivation path from the mnemonic, following the BIP-32 specification.
- At the encryption level, $V'_S$ is itself encrypted under $H(K_{\mathsf{kem}})$, so that **no curve point is published on-chain**. The public part is only an ML-KEM ciphertext and an AES-GCM ciphertext, and key privacy reduces to the anonymity (ANO-CCA) of ML-KEM. The sender blob is keyed by $H(v_S)$, derived from the seed and out of reach of Shor, which preserves sender recovery.
- We provide hardware blind signing with a Ledger integration. Note that blind signing is not affected by the quantum encryption. Clear-signing would require computing the encryption on the device. In the case of Ledger devices, the interface for ML-KEM encryption is already available.

One drawback of this construction is that the `0zk` address is now much larger (it includes an ML-KEM public key). This is problematic at the UX level, but is not a blocker on-chain. On Sepolia, this costs 1,205 additional bytes of calldata per note, and 2.8% more gas. This increase is not significant, mainly because this data is not stored in the contract (not part of the Merkle tree), but simply part of the data log. [Here](https://sepolia.etherscan.io/tx/0xcd99f3932feffd7df6d1a9a044ce23c1818e853d59d9ff741479f9c9bd98c71e#eventlog) is an example of a private transaction with hybrid-encrypted notes on Sepolia: the ciphertexts in the `Transact` event contain the ML-KEM encapsulations, and no curve point. Only the broadcaster fee note is kept in classical ECDH encryption; a PQ broadcaster could also be used in practice to reduce the metadata quantum leak. We did not investigate this part yet. 

## Conclusion

- **Tornado Cash** is weakened because of Pedersen hashes. The quantum pairing test alone only divides the anonymity set by about 6, but combined with on-chain metadata, it de-anonymizes users who deposit and withdraw several notes with the same addresses, which is probably a large part of the users.
- **Privacy Pools** v1 is post-quantum private. v2 is broken because of its ECDH note encryption, but ML-KEM hybrid encryption is possible, and wallets must derive the secrets with a derivation path from the mnemonic.
- **Railgun** is broken, because of the ECDH keys published on-chain. ML-KEM hybrid encryption is already implemented in our proof of concept, and here as well, wallets must derive the keys from the mnemonic.

Making **privacy** quantum safe is possible today, and it is urgent: every note encrypted with ECDH today will be decrypted on Q-day. Making **authentication** quantum safe is harder (STARK proofs, Ethereum signatures, consensus), but it has a deadline that is not reached yet.


## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found a typo, or want to improve the note ? Our blog is open to [PRs](https://github.com/ZKNoxHQ/blog/pulls).</small>
