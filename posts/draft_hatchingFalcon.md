[category]: <> (General)
[date]: <> (2025/02/24)
[title]: <> (Hatching a Falcon: developer diary)

<p align="center">
<img src="../../../../../images/hatching.png" alt="drawing" class="center" width="700"/>
<p align="center">
<small>(Still to small to hire graphic designers, sorry.)</small>

In a previous note, the stakes for a post quantum Ethereum future was described. 
This note describes the last weeks effort ZKNOX provided to implement a post-Quantum signer, along with the difficulties we faced, the choice we made and the hacks and tricks that were used.

## Introduction

Among lattice candidates, FALCON and DILITHIUM have been selected as finalist by NIST. Due to its smaller bandwidth and faster verification FALCON is the natural choice regarding on-chain constraints. A early hackathon project by [Tetration]() proposed an implementation, translating their author python code into solidity, making some adaptations in the specification in order to reduce gas cost. Despite those adaptation, the gas cost remained quite expansive, around $24M$, which is impractical. Our team then decided to operate the follwing work:

- examine the security of the Tetration implementation, looking at the impact of the alternate specs, and at implementation level (reversing the code to extract its formal specification).

- identify non optimal algorithmic choice at a mathematical level

- apply low level optimizations (Yul), and generic transformations


## Audit Tetration FALCON implementation


### PRNG

In cryptography, a hash function with desired ouput length is called a XOF (extendable output function). This is a useful primitive to be used as Pseudo determinictic generator. In the original FALCON specification, the SHAKE function standard is used as XOF to generate valid polynomial without biases or collisions. The problem is that SHAKE is not part of evm [available opcodes](https://www.evm.codes/). As such it requires both developper ressources, and a previsional gas cost above 4M just to hash a nonce to the polynomial ring. Tetration replaced it using Keccak, but in a "non-conventional" way, such that update of the internal state is also used as output. While not being able to derive an attack from this 
 property, it was decided during usefull exchange with Zhenfei, one of falcon authors, to replace it with a standard "counter-mode" like generation.

### Encodings

In FALCON, the raw signature before compression is followed by a Compress function which reduce the footprint by 30\%. In a classical architecture, this compression phase is negligible. In our case, the many binary operations have an important case. So Tetration decided to take as input the raw signature.
In FALCON, the encoding of a signature is unique. This is enforced by an encoding of the coefficient signs. Tetration choice restored a malleability property in the signature. 
It means it is possible for an attacker to replace a signature by another one, a lattice equivalent of the ecdsa property which led to Mount Gox disaster. ZKNOX suggested to restore malleability by forcing the first coefficient to be positive (which is enough to fix the sign of others).


### Check implementation

Looking at the code, a major flaw was revealed. A lack of control of input parameters enabled an attacker to forge a signature (produce different input message with same signature), with maximal impact: the target forge being any message. While the repo doesn't seem active anymore, a PR was pushed to fix all issues, along with failing test vectors:

https://github.com/Tetration-Lab/falcon-solidity/pull/1



## ZKNOX implementation



### Python signer

In order to enable on-chain transaction, a python signer was developped. Renaud was in charge of solidity, while Simon would be in charge of the python. Another important fact is that this double coding reduces the possibility that the same developper replicates the same error both in signing and verification. The versatility of python also enables the fast generation of test vectors and edge cases for the testbench.


### Optimal NTT

As for any asymmetric cryptographic primitive, the lowest level operations are the key for an efficient implementation. That's why NTT was digged first, 
Before implementing it in Yul, the low level description language of the EVM, the optimal algorithm was investigated by the team. After benching the recursive NTT (Tetration used) and the [Longa and al.]() , our experiments confirmed that the latest provided a x3 gas cost speed up. Upon confirmation, NTT and its inverse was then Yuled (written in Yul, the EVM assembly). 

### Hacking memory cost

FALCON require access to constant values, requiring to store them in the contract. In the EVM, the storage has high access cost. When a data is not meant to be modified, it is possible to circumvent this by deploying a contract meant to store those data, and access them through the opcode EXTCODECOPY. This reduces the access cost by a factor x26. 
 Note that this will not be possible after the EOF EIP implementation (maybe in Fusaka). The contract we deployed are using proxy mechanism, which enables creation of new account using falcon even after EOF.


### Reduce call data

Original APIs encoded each 14 bits coefficients over a full 256 bits word. While requiring additional shifts and binary logic, it is more efficient to use a compact representation, encoding each coefficients over 16 bits only (16 bits for memory alignment)

## Remaining work

## Conclusion

## Reach us

🔐 Practical security on the whole chain.

[Github](https://github.com/zknoxhq) | [Website](https://www.zknox.com) | [Twitter](https://x.com/zknoxhq) | [Blog](https://zknox.eth.limo) | [Contact Info](mailto:gm@zknox.com)

<small>Found typo, or want to improve the note ? Our blog is open to PRs.</small>