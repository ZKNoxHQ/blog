[category]: <> (General)
[date]: <> (2025/04/xx)
[title]: <> (Improving cryptography efficiency in Pectra)

## Introduction
Ethereum's update PECTRA comes in the next weeks as an important update of the chain from the cryptography point of view. The integration of BLS12-381 at the node level opens up perspectives for elliptic curves primitives (such as multi/threshold signatures) with zero-knowledge applications. In this blogpost, we present how to optimize elliptic curve operations in the context of PECTRA update.

## Pectra

##### From BN254 to BLS12-381

BN254 is an elliptic curve that has been widely used in zero-knowledge (ZK) cryptography due to its efficiency and relatively small parameter size, but it only provides around 100 bits of security, which is considered insufficient for many modern cryptographic applications. For stronger security guarantees, another curve, BLS12-381, has been designed for a higher security level together with ZK properties. This curve fulfills approximately 128 bits of security, making it more resistant to potential future attacks. While it requires slightly larger parameters and computational overhead compared to BN254, the tradeoff is well worth it for applications that need stronger cryptographic assurances. Therefore, shifting from BN254 to BLS12-381 is a prudent choice for improving the security of zero-knowledge systems. Pectra integrates precompiles for the arithmetic of this curve (see [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537)).

##### Cryptographic primitive _above_ BLS12-381

In the context of zero-knowledge proofs, it is sometimes required to compute elliptic curve arithmetic that will be, later on, verified in-circuit using BLS12-381. It is common to choose an elliptic curve designed to make ZK proofs efficient, called _embedded curves_. The curve is selected so that the verification algorithm involves native arithmetic for the ZK proof circuit. For BLS12-381, the ZK circuit is defined modulo a prime $r$ (which is BLS12-381 _scalar field order_). In this context, an embedded curve is defined over $\mathbb F_r$. While in-circuit verification is made efficient by this choice of base field, signature generation must also be fast in specific use-cases. Two curves have been designed for this purpose: [Jubjub](https://bitzecbzc.github.io/technology/jubjub/index.html) and [Bandersnatch](https://ethresear.ch/t/introducing-bandersnatch-a-fast-elliptic-curve-built-over-the-bls12-381-scalar-field). The latter has been designed so that scalar multiplications are more efficient. In the next section, we dig into the details of elliptic curve scalar multiplications in order to understand the benefits of Bandersnatch.

## Elliptic curve arithmetic

Elliptic curves are used in cryptography to construct secure key exchange protocols and digital signatures, leveraging their algebraic structure to provide strong security with relatively small key sizes.

##### Scalar multiplication
The main algorithm used in cryptography based on elliptic curves is the _scalar multiplication_. Given a scalar $k$ (usually of 256 bits), and a point $P$ of the curve, the point $[k]P$ is computed using the group law defined on the curve. This computation depends on the model used for the curve, but the cost is about $2\log_2(k)$ point additions. We do not go into the details of this cost in order to keep things as simple as possible.

##### Multi-scalar multiplication
In signature verification, it is common to compute multi-scalar multiplications (MSM) $[k]P + [\ell]Q$ for scalars $k,\ell < r$. After precomputing $P+Q$, it is possible to compute $[k]P+[\ell]Q$ in only $2\log_2(r)$ point additions, by reading simultaneously the bits of $k$ and $\ell$. More generally, a $n$-MSM $\sum_{i=1}^n [k_i]P_i$ can be computed in $2^n - n - 1$ precomputation additions, and $2\log_2(r)$ additions for the simultaneous computation. From now, we denote $\text{MSM}(n,N)$ the cost in elliptic curve additions of a multi-scalar multiplication of $n$ points with scalar of $N$ bits: $\text{MSM}(n,N) \approx 2^n -n -1 + 2N$. Note that in practice, additional operations are required and not taken into account in this blog post.

##### Fixed point SM
When $P$ is fixed, we can use the above technique in order to speed-up a SM: precomputing $P_i = [2^{iN/n}]P$ and $k = \sum_{i=1}^n k_i 2^{iN/n}$, we can decompose $[k]P = \sum_{i=1}^n [k_i]P_i$. This technique works in practice, but the precomputation part becomes expensive as long as $n$ grows, as illustrated in the following table (where the costs are estimated in point additions, with the simplified formula above):

|MSM|(1,256)|(2,128)|(3,86)|(4,64)|(5,52)|(6,43)|(7,37)|(8,32)|(9,29)|
|-|-|-|-|-|-|-|-|-|-|
|Precomputation | 0 |  1| 4 | 11 | 26 | 57 |  120 | 247 | 502 |
|Computation | 512 | 256 | 170 | 128 | 102 | 85 | 73 | 64 | 56 |
|**Total** | **512** | **257** | **174** | **139** | **128** | **142** | **193** | **311** | **558** |

##### GLV optimization
Small discriminant curves have a specfic structure that speeds up the scalar multiplication: there exists an (efficiently computable) endomorphism $\phi$ that has an eigenvalue $\lambda$ on the points of order $r$. It results that we can decompose $k = k_1 + \lambda k_2 \mod r$ with $\log_2(k_i) = 128$, and the cost of a scalar multiplication is thus obtain $\text{MSM}(2,128)$.

##### In-circuit SM verification
Zero-knowledge proofs are widespread cryptographic tools in blockchain, and one expensive computation is the scalar multiplication. In this context, we want to prove that $[k]P = Q$ and $Q$ is a hinted point. A technique was recently introduced by YEH [LINK BLOGPOST] using a fractional decomposition of $k = u/v \mod r$. It is possible to find $u,v$ of size almost $128$ bits and get the same speed-up as for GLV: $[k]P = Q \iff [u]P - [v]Q = 0$. In this context, we can verifiy the scalar multiplication in-circuit in $\text{MSM}(2,128^+)$. This technique can be combined with GLV (as mentioned by Liam Eagen [here](https://ethresear.ch/t/fake-glv-you-dont-need-an-efficient-endomorphism-to-implement-glv-like-scalar-multiplication-in-snark-circuits/20394/2)) in order to compute the verification in $\text{MSM}(4, 64^+)$. The bound on the obtained scalars can be estimated using lattice reduction.

##### In-circuit multi-scalar multiplications
When applying the previous technique for multi-scalar multiplications, it is possible to reduce the cost of a $2$-MSM (and more generally a $n$-MSM). However, the gain is not significant, and lookups in the MSM might degrade the actual cost in practice.

## Speeding up Ethereum cryptography

With the update of Ethereum, a fast elliptic curve defined above BLS12-381 fastens privacy computations. While [Jubjub]() was designed by Zcash (and used by [Railgun] for example), Bandersnatch has a small discriminant, enabling the above optimizations for scalar multiplications. Using this implementation, we enable new directions for Ethereum privacy:

##### Multi-signatures
Multi-signatures allow multiple parties to collaboratively produce a single valid signature, ensuring that transactions or messages require authorization from a predefined set of participants. The scheme MuSig2 introduced [here](https://eprint.iacr.org/2020/1261.pdf) is based on elliptic curve Schnorr signatures and can be instantiated with Bandersnatch, enabling fast signing and pairing-based applications using BLS12-381.

##### Threshold signatures
A threshold signature is another variant of signature that is generated only if a minimum number of participants (threshold) cooperate, enhancing security and fault tolerance in distributed systems. The work presented [here](https://eprint.iacr.org/2020/852.pdf) introduces flexible Schnorr threshold signatues that can be implemented using Bandersnatch for efficiency purposes.

##### Zero-knowledge property
More generally, all cryptography primitives that can be converted into zero-knowledge schemes could be implemented using Bandersnatch. [Railgun](https://www.railgun.org/) enables privacy in Ethereum using a ZK construction with BabyJubjub and the pairing-based curve BN254. This could be updated to work with Bandernsatch and BLS12-381 in order to increase the security level as well as the efficiency (at least on the non-pairing computation side).

## Conclusion
TODO

🚀 Let’s future-proof Ethereum together!

## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found typo, or want to improve the note ? Our blog is open to PRs.</small>