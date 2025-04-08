[category]: <> (General)
[date]: <> (2025/03/21)
[title]: <> (ETHDILITHIUM and ETHFALCON for Ethereum PQ Era)


<p align="center">
<img src="../../../../../images/hatching.png" alt="drawing" class="center" width="700"/>
<p align="center">
<small>(Hatching Ethereum FALCON)</small>


In a previous [note](https://zknox.eth.limo/posts/2025/02/24/ETHEREUM_for_PQ_era_250224.html), we discussed the stakes of a post-quantum Ethereum future. This entry highlights ZKNOX's efforts over the past weeks to implement post-quantum signature schemes: FALCON and DILITHIUM.

## Introduction

Among lattice-based signatures, DILITHIUM and FALCON have been selected by NIST as suitable replacements for a digital signature algorithm. FALCON is faster and more compact than DILITHIUM, and thus preferred for on-chain applications. However, the signing algorithm of FALCON is more complicated from an implementation point of view, while DILITHIUM signing algorithm is hardware-friendly and is expected to see secure element implementations in a near future. All these factors led us to implement DILITHIUM as well.

## EVM-Friendly Versions

#### Profiling

Before a full implementation, our team performed an initial assessment of the critical components of both algorithms. A previous post outlined the core operation—polynomial multiplication—and its optimization using the Number Theoretic Transform (NTT). ZKNOX successfully reduced a prior Solidity NTT implementation from 20M to 1.5M gas. Using an optimized NTT, the remaining cost of the verification is a hash computation.

FALCON requires SHAKE as its hash function, but since SHAKE is not natively supported by the EVM, it must be emulated. Even an optimized Yul implementation of SHAKE’s core permutation requires around 1M gas, resulting in a total of 10M gas for a full FALCON signature. To address this, we propose security-equivalent but more gas-efficient alternatives: _ETHFALCON_ and _ETHDILITHIUM_.

#### PRNG

In cryptography, a hash function with a configurable output length is called an XOF (Extendable Output Function). The FALCON specification uses SHAKE as an XOF to generate valid polynomials without bias nor collisions. However, SHAKE is not available as an EVM opcode [(see list)](https://www.evm.codes/), making its implementation costly (>4M gas per nonce-to-polynomial conversion). Some proposals replaced SHAKE with Keccak in unconventional ways, deriving output from internal state updates. After discussions with Zhenfei Zhang, one of FALCON’s authors, we decided to replace this approach with a standardized counter-mode generation method.

#### Encodings

FALCON’s raw signature undergoes a _compression function_ that reduces its size by 30%. While this is computationally negligible in conventional environments, this bitwise operations become cumbersome in Solidity, making the compression inefficient on-chain. As a result, _Tetration_ opted to use raw signatures as input.

In standard FALCON, signature encoding is unique, enforced by encoding coefficient signs. However, Tetration’s approach reintroduced _signature malleability_, allowing an attacker to replace a valid signature with another, (as with the ECDSA vulnerability behind the Mt. Gox disaster). To mitigate this, ZKNOX proposed enforcing a fixed sign for the first coefficient, ensuring a unique encoding.

#### Recovery Version

A key advantage of FALCON over DILITHIUM is its potential for a _recovery-based verification model_, similar to ECDSA. ZKNOX proposes a recovery version of FALCON that modifies the hash function specification to use the public key’s NTT representation. This allows verification using only an _NTT forward transform_, eliminating the need for an inverse NTT.

## Ongoing work



#### Toward a PQZK Future

One of Ethereum’s long-term visions is a _zero-knowledge (ZK) endgame_. ZK circuits working on non-native fields introduce additional proving costs. To address this, we specified _ZK-friendly alternatives_ using _M31_ and _BabyBear_ fields, optimized for _STARK-based proving systems_ (e.g., STWO and RISC0). Our goal is to provide a migration path from BabyJubJub, JubJub, and Bandersnatch curves to _FALZKON_ and _ZKDILITHIUM_ for private payments. The security implications of switching fields will be discussed in a future post.


#### Reduce gas using [EVMMAX](https://eips.ethereum.org/EIPS/eip-6690)


At the current time of writing, some experiments using the EVMMAX precompile to further speedup the NTT (EIP-6690) are conducted by Ipsilon. A rough analysis suggests potential speedup around a factor 4 (down to 500K). This is very experimental as EVMMAX is not planned yet.



## Results

The modifications presented let us reduce the verification cost, but also increase the siz eof the public key and signatures, compared to the NIST standardized version:

| Scheme | Public key | Signature | Comments|
|-|-|-|-|
|FALCON|897 B|666 B| From the NIST standardization.|
|ETHFALCON|1 024 B|1 064 B|Decompressions and NTT increase the size, but reduce verification.|
|DILITHIUM|1 312 B|2 420 B| From the NIST standardization.|
|ETHDILITHIUM|20 512 B|9 248 B|Expansions and NTT increase the size, but reduce verification.|

The table below summarizes implementation results. While ETHFALCON has been optimized, there is room for improvements in terms of gas saving.


| Function                   | Description               | Gas Cost | Test Status |
|----------------------------|---------------------------|----------|-------------|
| ZKNOX_ethfalcon.sol        | EVM-friendly FALCON       | 1.9M     | ✅           |
| ZKNOX_ethdilithium.sol     | EVM-friendly DILITHIUM    | 8.8M     | ✅           |
| ZKNOX_falcon.sol           | NIST-compliant FALCON     | 7M      | ✅         |
| ZKNOX_dilithium.sol        | NIST-compliant DILITHIUM  | 13M      | ✅         |
| ZKNOX_zkdilithium.sol      | ZK-friendly DILITHIUM     | N/A      | WIP         |
| ZKNOX_falzkon.sol          | ZK-friendly FALCON        | N/A      | WIP         |


##### FALCON: On-Chain Favorite, Signer’s Nightmare

As expected, FALCON is **the most efficient** scheme for verification, with the **shortest bandwidth**. However, implementing its signer in Python provided insight into the challenges hardware implementations will face. Memory consumption is high, and the Gaussian sampler relies on complex floating-point arithmetic.

Discussions with hardware vendors revealed a _strong preference for DILITHIUM_ due to these difficulties. However, given Ethereum’s on-chain constraints, FALCON remains the preferred choice for verification.

##### DILITHIUM: Less Efficient, but Valuable Features

DILITHIUM verification is _slower_ than FALCON on-chain, with _4× larger footprint and gas cost_. However, it offers several advantages:

- **Easier signer implementation:** Secure element vendors are more likely to implement DILITHIUM, making it a strong candidate for widespread adoption.
- **ZK-friendliness:** A ZK-adapted version of DILITHIUM is more efficient than FALCON’s ZK counterpart.
- **MPC compatibility:** DILITHIUM is better suited for multi-party computation (MPC) than FALCON, which could simplify adoption in TSS-based wallets like [Unruggable Wallets](https://github.com/rdubois-crypto/UnruggableWallet/tree/main).

| Feature                | FALCON ✅/❌ | DILITHIUM ✅/❌ |
|------------------------|------------|---------------|
| **Gas Efficiency**      | ✅         | ❌            |
| **Bandwidth**          | ✅         | ❌            |
| **Signer Simplicity**  | ❌         | ✅            |
| **ZK Adaptability**    | ❌         | ✅            |
| **MPC Friendliness**   | ❌         | ✅            |


## The 2 minutes testing

Generate keys, sign and verify onchain with FALCON in less than 2 minutes.

- Navigate to [ZKNOX FALCON repo](https://github.com/ZKNoxHQ/ETHFALCON)

- type make install, then make test

- Use the following commands to generate, sign a message and verify it with the onchain contract

```bash
# generate public and private keys using 'falcon' or 'ethfalcon'
./sign_cli.py genkeys --version='falcon'
# generate a signature for the message "This is a demo"
./sign_cli.py sign --privkey='private_key.pem' --data=546869732069732061207472616e73616374696f6e
# verify onchain the  signature using address of contract specified below (ensure --version is compliant with address)
./sign_cli.py verifyonchain --pubkey='public_key.pem' --data=546869732069732061207472616e73616374696f6e --signature='sig' --contractaddress='0x5dc45800383d30c2c4c8f7e948090b38b22025f9' --rpc='https://ethereum-holesky-rpc.publicnode.com'
```
The contract address refers to the contract implementing FALCON in Solidity. This should output:
```
0x0000000000000000000000000000000000000000000000000000000000000001
```
Congratulation, you just verified your first Post quantum signature on chain. So much happyness deserves starring the repo to support our Open source work.

## Conclusion

Thanks to ZKNOX’s work, **on-chain post-quantum verification is now feasible** for experimentation. While gas costs are acceptable for L2s, they remain prohibitively high for most L1 use cases—except for verifying high-value transactions. The team continue to work on the ZK versions, and will start embedded implementation.


## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found typo, or want to improve the note ? Our blog is open to PRs.</small>