[category]: <> (General)
[date]: <> (2025/04/xx)
[title]: <> (Bandersnatch, GLV and fakeGLV: Pectra optimal BLS12-381 arithmetic for ZK Dapps)



## Introduction
Ethereum's update PECTRA comes in the next weeks as an important update bringing evolutivity and security improvments. Among those, the integration of [BLS12-381](https://eips.ethereum.org/EIPS/eip-2537) in clients opens up perspectives for elliptic curves primitives (such as multi/threshold signatures) with zero-knowledge applications. 
Among those are private payments (RAILGUN).

In this blogpost, we present how to optimize  elliptic curve operations in the context of PECTRA update, with a focus on [BanderSnatch](https://eprint.iacr.org/2021/1152). In particular, the first known implementation mixing FakeGLV and GLV over Bandersnatch is provided, leading to the most efficient in-circuit verification algorithm over BLS12-381 to date. More general tricks for generic curves (ZKMAIL, ZKWebAuthn) are also discussed.

## Pectra

##### From BN254 to BLS12-381

BN254 is an elliptic curve that has been widely used in zero-knowledge (ZK) cryptography due to its efficiency and  small parameter size, but it only provides around 100 bits of security, which is insufficient for modern cryptographic applications. For stronger security guarantees, another curve, BLS12-381, has been designed together with ZK properties. This curve fulfills approximately 128 bits of security, making it more resistant to potential future attacks. While it requires slightly larger parameters and computational overhead compared to BN254, the tradeoff is well worth it for applications that need stronger cryptographic assurances. Therefore, shifting from BN254 to BLS12-381 is a prudent choice for improving the security of zero-knowledge systems. Pectra integrates precompiles for the arithmetic of this curve (see [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537)). In a recent post Distributed Labs provides some insight on the prover complexity which, are not very far from its less secure version. Those complexity are however in a range where linear improvments are felt by the user (a few seconds).

##### Cryptographic primitive _above_ BLS12-381

In the context of zero-knowledge proofs, it is sometimes required to compute elliptic curve arithmetic that will be, later on, verified in-circuit using BLS12-381. It is common to choose an elliptic curve designed to make ZK proofs efficient, called _embedded curves_. The curve is selected so that the verification algorithm involves native arithmetic for the ZK proof circuit. For BLS12-381, the ZK circuit is defined modulo a prime $r$ (which is BLS12-381 _scalar field order_). In this context, an embedded curve is defined over $\mathbb F_r$. While in-circuit verification is made efficient by this choice of base field, signature generation must also be fast in specific use-cases. Two curves have been designed for this purpose: [Jubjub](https://bitzecbzc.github.io/technology/jubjub/index.html) and [Bandersnatch](https://ethresear.ch/t/introducing-bandersnatch-a-fast-elliptic-curve-built-over-the-bls12-381-scalar-field). The latter has been designed so that scalar multiplications are more efficient. In the next section, we dig into the details of elliptic curve scalar multiplications in order to understand the benefits of Bandersnatch.

## Elliptic curve arithmetic

Elliptic curves are used in cryptography to construct secure key exchange protocols and digital signatures, leveraging their algebraic structure to provide strong security with relatively small key sizes.

##### Scalar multiplication (SM)
The critical algorithm used in cryptography based on elliptic curves (ECC) is the _scalar multiplication_. Given a scalar $k$ (usually of 256 bits), and a point $P$ of the curve, the point $[k]P$ is computed using the group law defined on the curve. This computation depends on the model used for the curve, but the cost is about $2\log_2(k)$ point additions. We do not go into the details of this cost in order to keep things as simple as possible.

##### Multi-scalar multiplication (MSM)
In signature verification, it is common to compute multi-scalar multiplications (MSM) $[k]P + [\ell]Q$ for scalars $k,\ell < r$. After precomputing $P+Q$, it is possible to compute $[k]P+[\ell]Q$ in only $2\log_2(r)$ point additions, by reading simultaneously the bits of $k$ and $\ell$. More generally, a $n$-MSM $\sum_{i=1}^n [k_i]P_i$ can be computed in $2^n - n - 1$ precomputation additions, and $2\log_2(r)$ additions for the simultaneous computation. From now, we denote $\text{MSM}(n,N)$ the cost in elliptic curve additions of a multi-scalar multiplication of $n$ points with scalar of $N$ bits: $\text{MSM}(n,N) \approx 2^n -n -1 + 2N$. Note that in practice, additional operations are required and not taken into account in this blog post.

##### Fixed point SM
When $P$ is fixed, we can use the above technique in order to speed-up a SM: precomputing $P_i = [2^{iN/n}]P$ and $k = \sum_{i=1}^n k_i 2^{iN/n}$, we can decompose $[k]P = \sum_{i=1}^n [k_i]P_i$. This technique works in practice, but the precomputation part becomes expensive as long as $n$ grows, as illustrated in the following table (where the costs are estimated in point additions, with the simplified formula above):

|MSM|(1,256)|(2,128)|(3,86)|(4,64)|(5,52)|(6,43)|(7,37)|(8,32)|(9,29)|
|-|-|-|-|-|-|-|-|-|-|
|Precomputation | 0 |  1| 4 | 11 | 26 | 57 |  120 | 247 | 502 |
|Computation | 512 | 256 | 170 | 128 | 102 | 85 | 73 | 64 | 56 |
|**Total** | **512** | **257** | **174** | **139** | **128** | **142** | **193** | **311** | **558** |

In the case of signature verification for an account, where the public key is the fixed point, this speed up can be used. It is implemented in efficient libraries, such as BOLOS, FCL and OpenZeppelin P256 libraries (leading to their lesser gas cost compared to Daimo), and SCL generic one. This algorithm is also the scope of [RIP7696](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7696.md). However in the case of ZK, where public key is kept as a secret input, it is not possible to use this algorithm. 

**BanderSnatch solves this using a combination of GLV and fakeGLV.**

## Bandersnatch

Bandersnatch is an embedded curve, such as BabyJujub, which presents a GLV endomorphism. Having a GLV endomorphism allows faster SM.

##### [GLV](https://www.iacr.org/archive/crypto2001/21390189.pdf) optimization
Small discriminant curves have a specfic structure that speeds up the scalar multiplication: there exists an (efficiently computable but non trivial) endomorphism $\phi$ that has an eigenvalue $\lambda$ on the points of order $r$. It results that we can decompose $k = k_1 + \lambda k_2 \mod r$ with $\log_2(k_i) = 128$, and the cost of a scalar multiplication is thus obtain $\text{MSM}(2,128)$.

##### Fake-GLV: a hinted verification for ZK uses.

Zero-knowledge proofs are widespread cryptographic tools in blockchain, and one expensive computation is the scalar multiplication. In this context, we want to prove that $[k]P = Q$ and $Q$ is a hinted point (provided as additional helper input).FakeGLV, was recently introduced by [[YEH]](https://ethresear.ch/t/fake-glv-you-dont-need-an-efficient-endomorphism-to-implement-glv-like-scalar-multiplication-in-snark-circuits/20394) using a fractional decomposition of $k = u/v \mod r$. It is possible to find $u,v$ of size almost $128$ bits and get the same speed-up as for GLV: $[k]P = Q \iff [u]P - [v]Q = 0$. In this context, we can verifiy the scalar multiplication in-circuit in $\text{MSM}(2,128^+)$. This technique can be combined with GLV (as mentioned by Liam Eagen [here](https://ethresear.ch/t/fake-glv-you-dont-need-an-efficient-endomorphism-to-implement-glv-like-scalar-multiplication-in-snark-circuits/20394/2)) in order to compute the verification in $\text{MSM}(4, 64^+)$. The bound on the obtained scalars can be estimated using lattice reduction.

##### In-circuit MSM

If ZK is used for **validity** and not privacy, then it is possible to use MSM.
When applying the previous technique for multi-scalar multiplications, it is possible to reduce the cost of a $2$-MSM (and more generally a $n$-MSM). However, the gain is not significant in R1CS due to lookups cost for native curves. It has a potential outcome for non native, such as P256 as used by ZKMAIL, ZKWebAuthn. 


## Use cases

##### Private Wallets/Privacy Pools

All cryptographic primitives that can be converted into zero-knowledge schemes should be implemented using Bandersnatch. [Railgun](https://www.railgun.org/) enables privacy in Ethereum using a ZK construction with BabyJubjub and the pairing-based curve BN254. This shall be updated to work with Bandernsatch and BLS12-381 in order to reach a state of the art  security level as well, without loss of efficiency.

##### ZKWebAuthn, ZKMail

ZKMail and ZKWebAuthn are  systems that allow users to prove ownership of an email address (resp. Passkey credential) without revealing the actual email content, metadata, or even the email address itself (resp. credentials). During authentication, the server sends a challenge, signed by the user, but rather than the signature, a ZK-proof of the signature is send instead and verified onchain.



## Conclusion

This note described several optimizations to improve both security and UX (reducing the prover computations, i.e the latency of the phone/labtop) for the most popular ZK applications. GLV is linked to Bandersnatch, but fakeGLV+2MSM principle can be applied (with lesser gain) to generic curves. The provided python code is a first step before developing the circuits for an integration into proving backends. When moving to BLS12, Bandersnatch outperform Jujub and is the optimal choice.


#### Acknowledment

The fakeGLV is an original idea from Youssef el Housni. The mixing of fake and true has been discussed in [ethresearch]((https://ethresear.ch/t/fake-glv-you-dont-need-an-efficient-endomorphism-to-implement-glv-like-scalar-multiplication-in-snark-circuits/20394)). 
The developments into ZK backend are currently in progress, along with a full article with  from Consensys.  


#### Github

Find python implementation of the discussed algorithm here:


🚀 Let’s future-proof Ethereum together!

## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found typo, or want to improve the note ? Our blog is open to PRs.</small>