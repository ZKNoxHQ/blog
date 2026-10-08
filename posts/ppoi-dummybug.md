[category]: <> (General)
[date]: <> (2026/10/08)
[title]: <> (Private Proofs of Innocence: a circuit flaw and a four-year retrospective)



In this blog post, we dig into the details of one important feature of recent privacy-preserving protocols: regulatory compliance.

ZKNOX found a soundness flaw in Railgun's Private Proof of Innocence circuit, supplied the patch code, and the Railgun team deployed it. Following the flaw discovery, ZKNOX analyzed this vulnerability with on-chain data in order to detect whether notes were shielded and blocked by PPOI, and later unshielded to a new address with a valid PPOI and concluded it had not been exploited. It was also an opportunity to take stock of how well a mechanism like PPOI actually performs in practice, which turned out to be the more interesting result. The first part of this post is the description of the system and the bug, the second one gives some elements of the forensic.

## Compliance across the different privacy protocols

In this post, we focus on Ethereum privacy-preserving protocols. Tornado Cash was historically the first scheme enabling privacy-preserving transactions, but it has also been criticized for money laundering. More recently, Railgun has been introduced, enabling a broader range of possibilities, with a real private UTXO model, and many features. In this protocol, it is possible to keep private funds secured by a hardware device, a feature that is not fully possible on Tornado Cash. Another protocol has also been deployed with the aim of improving Tornado Cash in different aspects. In order to prevent money laundering, these protocols have integrated private proofs attesting that the funds interacted only with accepted actors:

- Tornado Cash can be used together with a proof of innocence provided by Chainway (https://poi.chainway.xyz/).
- Privacy Pools controls illicit funds through an Association Set Provider Layer (https://docs.privacypools.com/layers/asp),
- Railgun integrates Private Proof Of Innocence (https://docs.railgun.org/wiki/assurance/private-proofs-of-innocence), a separate system also based of ZK proofs.

In all of these technologies, the protocol relies on several entities that provide lists of bad actors. In the case of Railgun, five providers are queried, and any address blacklisted by at least one of them would be considered a bad actor. This list is thus updated in real time in order to prevent even the most recent actors from laundering.

## Railgun and PPOI

In this blog post, we focus on PPOI and Railgun. Before digging into the details of PPOI, we need to recall how Railgun works.

Private transactions are made using a UTXO model, where a private address (starting with 0zk) owns encrypted notes. A private address encodes the necessary information necessary to enable transactions without revealing any information about the participants. We now recall the main actions in Railgun (shield, transact and unshield), and how PPOI interacts with them.

### Shield

In privacy systems, moving funds into the private model is called a shield. More precisely, some funds are sent (transparently) to the Railgun contract, and a note is created in the private domain for the corresponding 0zk address.

A shield does not become spendable immediately. The waiting period before the attestation is issued is the window the chain analyzers need to do their work, and it is also the latency that lets them catch an exploit on another protocol and flag the attacker's addresses before the stolen funds can obtain an attestation here. Without it, a shield deposited minutes after a hack would be screened against a list that does not yet know about the hack.

Railgun wallets allow a user to later transact with this note only if the note has a valid PPOI. Here is an example of a valid shield:

- Vitalik sends 400 ETH from vb2 to 0x1810c87a85B1d3AFf71F3bd7fe45e4dc03EFF10E: (link (https://etherscan.io/tx/0x16101b1eecc913710a2f878543590e702d7012d180f78f8d37a5c128b4afd516))
- This wallet shields the 400 ETH into WETH in the Railgun contract (link (https://etherscan.io/tx/0x9cc42e39aa3af5654183a6a82f09631135b2044e5ab4c423b596ad88ed1b289b))
- The proof of innocence is available here (https://ppoi.info/Ethereum/tx/0x9cc42e39aa3af5654183a6a82f09631135b2044e5ab4c423b596ad88ed1b289b).

When a shield is blocked by PPOI, its owner has no other choice than to unshield to the origin address, i.e. send back the money to the sender in the transparent model. This technique prevents money laundering, as in this example (an attempt to launder of $3 091 755):

- The bad actor tries to shield 3 091 755 $DAI (link (https://etherscan.io/tx/0x2b6253700eb17c3691f880152c1b58fc96a1339b9102a01397445292077ed2bb))
- The shield is blocked by PPOI (link (https://ppoi.info/Ethereum/tx/0x2b6253700eb17c3691f880152c1b58fc96a1339b9102a01397445292077ed2bb))
- The bad actor unshields to origin (link (https://etherscan.io/tx/0x5b9e359f6ce445fb451e1d4cd688230eb8d47bd5bfb67d04ae5363b7492ea1bf))
- He later tries to send the funds to other addresses, but all of them are also blocked. He has no other choice than to unshield to the origin address for every shield.

In practice, a shield always requires a valid PPOI to later be able to unshield. This comes with a drawback in terms of user experience: shielding a note requires waiting for validation from the providers before getting the PPOI.

### Transact

PPOI achieves its goal using a zero-knowledge proof, in which the circuit asserts that the (private input) spent notes are not interacting with the updated list of bad actors. Unlike Railgun transaction proofs, PPOI proofs are sent and verified off-chain, and do not update the state of the private notes.

As a UTXO model, transactions are identified through a hash of the input (spent) and output (created) notes. In Railgun, it is possible to transact with several input and output notes. As an example, for a transaction of $2 from Alice to Bob (where Alice owns a $3 note), the Railgun transaction is formatted as 1x2:

- One note is spent (the note of $3 owned by Alice),
- A note is created for Bob (a note of $2),
- A change note is also created for Alice (a note of 3-2 = $1).

During a private transaction, no PPOI is required. The last action we will describe is Unshield, and it does require a valid PPOI.

### Unshield

An unshield follows the same structure as a transact, but the main difference is that one of the recipients is a 0x address, rather than a 0zk private address. This unshield requires (at the wallet level) a valid PPOI in order to be executed. As in the Railgun contract, PPOI indexes the transaction through a hash of input and output notes. While any number of notes could be considered, PPOI supports up to 13 input and output notes (which is more than enough in practice). The architecture is generic, and the example of Alice's transaction (1x2) would actually be considered as a 13x13 transaction, thanks to dummy notes. In other words, some 0-value notes pad the transaction so that it is in the format 13x13. For the above example, we would have:

- Spent notes: ($3; own=A), twelve times ($0, own=_),
- Created notes: ($2, own=B), ($1; own=A), eleven times ($0; own=_).

## A flaw in the PPOI circuit

PPOI verifies the compliance of the input notes by checking every transaction involving each note and its ancestors. Obviously, the dummy notes are bypassed in order to make the construction work. We provide here the corresponding section of the code that checked dummy notes:

```circom
// 3. Check dummy inputs (i.e., with zero value)
component isDummy[nInputs];
for(var i=0; i<nInputs; i++) {
    isDummy[i] = IsZero();
    isDummy[i].in <== valuesIn[i];
}
```

Here, dummy notes are characterized by amount == 0, but this allows a bad actor get a valid PPOI for a blocked note by simply setting the note amount to 0. As the PPOI is external to the contract and does not change the private state, the PPOI is validated and the actor is able to unshield with a fake proof of innocence.

For instance, Alice can bypass PPOI and send an illicit note of $1000 to Bob by submitting the following information to PPOI:

```
INPUT NOTES
-----------
Note 1:  Owner=Alice, Amount=0
Note 2:  Owner=None, Amount=0
.
.
.
Note 13:  Owner=None, Amount=0

OUTPUT NOTES
------------
Note 1: Owner=Bob, Amount=1000
Note 2:  Owner=None, Amount=0
.
.
.
Note 13:  Owner=None, Amount=0
```

For this submission, the PPOI circuit will bypass the check on the first input note (considering it as dummy). Note that the Railgun contract and the PPOI circuit check distinct assertions:

- Railgun checks the nullifier computation (for input notes), commitment computation (for output notes) check the balance of amount (and token type) for input vs output notes, etc. The onchain state is then modified (updating of the spent and created notes sets).
- PPOI checks nullifiers and commitments for the non-dummy notes, but do not verify the balance check. Also, the value of the nullifier does not depend on the amount of the note. The PPOI proof is independent from the onchain state, and so the note owned by Alice remains with amount=$1000 (but is nullified).

ZKNOX delivered to PPOI a new version of the circuit in order to fix this vulnerability. A dummy note is now characterized by a fixed leaf in the set of nullifiers:

```circom
// 3. Check dummy inputs (i.e., with zeroLeaf as nullifier)
component isDummy[nInputs];
for(var i=0; i<nInputs; i++) {
    isDummy[i] = IsZero();
    isDummy[i].in <== nullifiers[i] - zeroLeaf;
}
```

With this fix, dummy notes are correctly characterized and a bad actor cannot bypass the POI through a dummy note.

The collaboration with the Railgun team continues on the shield qualification policy, which is the subject of the analysis below.

## Analysis

We analyzed this vulnerability with onchain data in order to detect whether notes were shielded and blocked by PPOI, and later unshielded to a new address with a valid PPOI.

### What a blocked shield is supposed to do

The proofs themselves cannot settle the question. A proof built the way described above is indistinguishable from an honest one at every interface a consumer can see: the public signals are byte-identical, and `TransactProofData` carries no per-input information at all. The answer has to come from the chain.

So we rebuilt the PPOI accumulator client-side from public data and cross-referenced it against every shield and unshield on Ethereum L1, against the default list published by Private Proofs Inc (`efc6ddb5…`), which aggregates the providers named earlier and is the list the wallets consult.

The baseline matters more than it may seem. A blocked shield is terminal on that list: it will never receive a POI, so the funds behind it can never be spent as innocent. The intended way out is the one shown earlier in this post. The owner unshields back to the origin address, with no attestation attached, and takes the funds back in the open. That exit carries no POI, and **that is not a defect**. Railgun is permissionless at the contract level: nothing on chain requires a proof of innocence. PPOI is an attestation layer above it, and a no-POI exit simply means the funds come out without one, visibly and traceably. The escape hatch exists on purpose, so that a blocked user is never expropriated.

Which turns the question around. If reclaiming your money is always available, leaving it locked in the pool is the odd choice, and the obvious reason to make it is that claiming the funds would publish a link their owner would rather not publish. **The blocked notes still sitting in the pool are the ones worth counting.**

### What the chain says

Our accumulator snapshot stops at block 25990627. Shields deposited after that point are absent from it, which is indistinguishable from being refused, so 2026-Q3 and 2026-Q4 are outside what we can read and are excluded. What remains is nine quarters and 983 blocked shields.

| quarter | blocked | | | paid back to origin | | | still in the pool |
|---|---|---|---|---|---|---|---|
| | n | $stable | WETH | n | $stable | WETH | n |
| 2024-Q2 | 14 | 0 | 1,123 | 14 | 0 | 1,123 | 0 |
| 2024-Q3 | 181 | 9.73M | 7,977 | 174 | 9.73M | 7,873 | 0 |
| 2024-Q4 | 113 | 2.32M | 4,158 | 103 | 2.32M | 4,058 | 0 |
| 2025-Q1 | 148 | 1.66M | 4,763 | 140 | 1.66M | 4,758 | 0 |
| 2025-Q2 | 160 | 8.70M | 2,812 | 146 | 8.70M | 2,808 | 0 |
| 2025-Q3 | 74 | 929.0k | 1,328 | 66 | 823.3k | 1,263 | 0 |
| 2025-Q4 | 67 | 5.06M | 3,479 | 61 | 5.06M | 3,478 | 0 |
| 2026-Q1 | 107 | 471.8k | 5,440 | 82 | 73.5k | 5,037 | **1** |
| 2026-Q2 | 119 | 2.31M | 2,475 | 96 | 2.31M | 2,468 | 0 |
| **total** | **983** | **31.18M** | **33,555** | **882** | **30.68M** | **32,866** | **1** |

By count, 89.7% of blocked shields went home. By value the figure is far higher: **98.4% of the blocked stablecoins and 97.9% of the blocked WETH were unshielded back to their own depositor**, without any attestation, in full public view.

### The settled quarters

A blocked shield is not reclaimed the same day. The owner has to notice, decide, and send a transaction, so the most recent quarters have had less time for that to happen and their figures are still moving. Restricting to the seven quarters old enough to have fully resolved, 2024-Q2 through 2025-Q4:

- **757 blocked shields, and not one of them is still in the pool.**
- $28.29M of $28.40M in stablecoins went back to the depositor: **99.6%**.
- 25,361 of 25,640 WETH went back: **98.9%**.
- What did not come back: $106,800 and 279 WETH, spread over 53 shields.

That is the system working as designed, on every blocked shield old enough to judge.

### The exception

Across the whole nine quarters there is exactly one blocked note still sitting in the pool:

```
WETH 212.36775   block 24470430   2026-02   0x640Fb638EfCC0868F5E95536678087e14A2e96Ab
```

Eight months old, in a dataset where the comparable population reclaimed their funds within weeks, and worth more on its own than everything else left unreturned across seven settled quarters.

We also screened every blocked depositor and every address on the exit side against 603 unique denylisted addresses, pooled from the Chainalysis on-chain oracle, the OFAC SDN list and Etherscan's blocked-address set. **Zero hits on either side**, which is consistent with notes blocked through an ancestor rather than through the depositor himself.

### What a no-POI exit tells an observer

That one note is the thread worth pulling. Its depositor, `0x640Fb638…A2e96Ab`, had two shields blocked for a combined 393 WETH. One is the note still in the pool. The value behind the other did not go back to origin: it left through a no-POI unshield.

That exit is permitted, and it is also conspicuous. Every mainstream Railgun wallet (Railway, Kohaku, Railoxide, anon) enforces the attestation client-side and will not build an unshield without one. The contract does not care, so the transaction is perfectly valid, but producing it means stepping outside the standard clients. A no-POI exit is therefore both allowed by the protocol and self-marking in the data.

This is the property that makes the whole analysis possible, and it is worth stating plainly because it is easy to read as a weakness. Funds can always leave: that is what permissionless means, and it is why a blocked user is never expropriated. What they cannot do is leave unnoticed. The attestation is not a lock on the exit, it is a label on it, and the absence of that label is itself public and permanent on chain. Anyone can enumerate the no-POI exits, as we did here, and so can an exchange, a compliance team or an analytics firm deciding what to do with funds that arrive carrying that history.

So the answer to the question we started with does not depend on resolving every note individually. It rests on what blocked depositors did in the aggregate: they overwhelmingly took the public route, and the few exits that did not are flagged by their own absence of attestation.

Where the remaining work sits is a policy question rather than a cryptographic one, and at a different layer than the circuit. An aggregator node already knows which transactions carry no POI and could weigh that information when qualifying later activity from the same address. Following funds further, across intermediate hops, is address-graph analysis and belongs with the firms that do it. Moving POI enforcement on chain, where the contract itself would require a valid proof, closes the question at the root, at the cost of the permissionless property the escape hatch exists to preserve.

## Conclusion

The dummy-note flaw was real, it worked against the production proving key, and it was indistinguishable from an honest proof at every consumer-visible interface. It is fixed.

Our retrospective analysis found no evidence that it was ever used, and in the course of looking it produced a measurement of PPOI itself that is worth more than the answer we went in for. Over the seven quarters old enough to judge, **99.6% of the blocked stablecoin value and 98.9% of the blocked WETH went back to the depositors who had put it in**, publicly and without an attestation, and not one blocked note from that period is still sitting in the pool.

Those numbers are the system working. A shield that the list refuses does not get spent as innocent, and the people holding those notes did the only thing left to them: they took their money back in the open, at full cost to the privacy they had paid for. That is the outcome the designers intended, and it happens at a rate of around 99% of value on every quarter with the time to resolve.

What makes it work is the shape of the mechanism rather than its strictness. PPOI does not seize funds and does not block transactions on chain, which is what keeps Railgun permissionless and keeps a wrongly listed user from being expropriated. What it does instead is make compliance legible. An attestation is a label, its absence is also a label, and both are public and permanent. Funds can always leave; they cannot leave quietly. Every downstream party, from an exchange to a compliance desk, gets to decide for itself what to do with value that carries no proof of innocence, and the near-total return rate says that for anyone with legitimate funds the attested path is simply the one worth taking.

Since disclosure, we are working with chain analyzers and the Railgun team, on how shields are qualified in addition on how proofs are verified. ZKNOX cares about both ends of this balance, and not in the abstract: the wave of violent crime targeting crypto holders in France has come close to us, and at the same time France is sliding into blanket surveillance. Privacy and the fight against criminality are usually presented as opposites. A mechanism like PPOI is the argument that they need not be.

## References

- Railgun, Private Proofs of Innocence (https://docs.railgun.org/wiki/assurance/private-proofs-of-innocence)
- PPOI circuits, Railgun-Privacy/proof-of-innocence-circuits (https://github.com/Railgun-Privacy/proof-of-innocence-circuits)
- PPOI node, Railgun-Community/private-proof-of-innocence (https://github.com/Railgun-Community/private-proof-of-innocence)
- Privacy Pools, Association Set Provider layer (https://docs.privacypools.com/layers/asp)
- Tornado Cash proof of innocence, Chainway (https://poi.chainway.xyz/)
- SEAL 911 (https://www.seal911.org/)

## Signal bad behavior

If you are witnessing or have been hit by an ongoing attack on a protocol, SEAL 911 (https://www.seal911.org/) reaches a vetted group of security researchers and incident responders directly, at any hour.

## Reach us

🔐 Practical security on the whole chain.

Github (https://github.com/zknoxhq) | Website (https://www.zknox.com) | Twitter (https://x.com/zknoxhq) | Blog (https://zknox.eth.limo) | Contact Info

<small>Found typo, or want to improve the note ? Our blog is open to PRs. (https://github.com/ZKNoxHQ/blog/pulls)</small>
