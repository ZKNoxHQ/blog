[category]: <> (General)
[date]: <> (2025/02/26)
[title]: <> (ZKNOX: Roadmap 2025)

This post outlines the technical roadmap for ZKNOX in 2025.

## 7702 + 4337 for Current Hardware Wallet Platforms

Hardware wallet platforms often lag behind in adopting new standards and may view Account Abstraction (AA) as either unnecessary or even a threat. Our goal is to change this perception by providing easy-to-integrate code that demonstrates the benefits of AA for both hardware wallet manufacturers and their users.

To achieve this, we will develop a clear and practical 7702 + 4337 integration scenario tailored for hardware wallets. This scenario will highlight the enhanced security offered by AA, such as allowing low-value transactions to be signed via a mobile device while requiring the hardware wallet for high-value transactions. By making adoption straightforward and showcasing security improvements, we aim to encourage broader industry support for these technologies.

## Protecting Ethereum from the Quantum Threat

With recent advancements in quantum computing, concerns about its potential impact on Ethereum security are increasing. As highlighted in excellent research by [Asanso](https://ethresear.ch/t/so-you-wanna-post-quantum-ethereum-transaction-signature/21291) and [Miller](https://ethresear.ch/t/tasklist-for-post-quantum-eth/21296), Ethereum's reliance on ECDSA for externally owned account (EOA) signatures makes it vulnerable to quantum attacks.

While post-quantum (PQ) cryptographic algorithms exist, on-chain implementations are scarce and prohibitively expensive, often exceeding 24 million gas. Leveraging our extensive experience in cryptographic optimization, both at the embedded (hardware) level and [on-chain](https://eprint.iacr.org/2023/939), ZKNOX is committed to advancing efficient PQ implementations across the entire Ethereum stack, from wallets to smart contracts.

Notably, we have already reduced the on-chain cost of FALCON signatures from 24M to 2.5M gas and proposed [EIP-7885](https://eips.ethereum.org/EIPS/eip-7885) to accelerate lattice-based cryptographic primitives. Moving forward, we will contribute to RIPs, investigate alternative PQ candidates such as DILITHIUM, and explore methods to make them more EVM- and ZK-friendly.

## Optimizing Ethereum Execution

Several Ethereum Improvement Proposals (EIPs) aim to enhance the efficiency of cryptographic computations. These include RISC-V-based virtual machines (VMs), EWASM, SIMD ([EIP-616](https://eips.ethereum.org/EIPS/eip-616)), EVMMAX, EIP-7885, and RIP-7696—listed here in decreasing order of generality and complexity.

SIMD strikes a balance between a full RISC-V VM switch and less flexible precompiles. Our team will experiment with its implementation on a fork to assess its impact on various cryptographic algorithms, beginning with post-quantum candidates. This work will be carried out in synergy with our ongoing PQ research.

## Privacy-Focused Hardware Wallets and Governance

Last year, our team delivered a threshold signature scheme (TSS) implementations of FROST and MuSig2 over secp256k1 and contributed to the BanderSnatch curve. Building on our experience with embedded cryptographic development, we plan to extend these implementations to hardware wallets, integrating MPC-based governance mechanisms.

This initiative aims to enhance security and resistance against malware for privacy-preserving protocols that use custom elliptic curves, such as Railgun. By embedding MPC directly into hardware wallets, we can strengthen user security while enabling advanced governance models for privacy-focused applications.

---

ZKNOX remains committed to pushing the boundaries of cryptographic security, efficiency, and usability. Stay tuned for further updates as we execute this ambitious roadmap.

