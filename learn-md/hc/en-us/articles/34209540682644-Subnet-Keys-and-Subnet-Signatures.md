# Subnet Keys and Subnet Signatures

Each subnet on ICP manages cryptographic keys that are used in several parts of the protocol:

- An unbiased random beacon determines the block maker in each consensus round.
- Messages to other subnets are signed and can be validated by the receiving subnet based on knowledge of only the public key of the sending subnet, which enables horizontal scalability of ICP.
- Client applications can validate information retrieved from the subnet using only the public key of the subnet, enabling these applications to be resource-efficient (even run as part of a standard website) and fully trustworthy.
- Each canister has access to an unbiased and unpredictable source of randomness.

## Threshold BLS Signatures

The threshold signature scheme implemented by the IC for the above-mentioned tasks is a threshold version of the well-known [BLS signature scheme](https://en.wikipedia.org/wiki/BLS_digital_signature). One reason for using the BLS signature scheme is that it is the only one that yields a threshold signing protocol that is very simple and efficient. Indeed, a machine holding a share of the secret signing key can very easily generate a share of a signature on a message, and these signature shares can be combined to form a BLS signature on a message – no further interaction between these machines is required.

Another reason for using the BLS signature scheme is that signatures are *unique*, meaning that for a given public key and message, there is only one valid signature on that message. This unique-signature property is essential for the application to generating unpredictable and unbiased pseudo-random numbers for smart contracts: after a smart contract requests a pseudo-random number (and not before!), a signature on a special message is generated, and this signature is passed through a hash function to derive a seed from which the required pseudo-random numbers are generated. By the security property of the signature scheme, neither this seed nor the derived pseudo-random numbers can be predicted or biased.

## Distributed Key Generation

While signing with threshold BLS is quite straightforward, designing a secure, decentralized protocol for generating and distribution the shares of the secret signing key – that is, a DKG, or Distributed Key Generation protocol – remains a challenge. While there has been quite a bit of research on DKG design, the vast majority of DKG protocols in the literature do not meet the demanding requirements of the Internet Computer, in that they either assume a *synchronous network* (meaning that the protocols will fail or become insecure if messages are unexpectedly delayed) or provide *no robustness* (meaning that the ability to produce signatures is completely lost if a *single* node should crash) or *both*. Neither of these assumptions are acceptable on the IC: security and liveness must hold even an *asynchronous network* with many faulty nodes.

DFINITY has designed, analyzed, and implemented [a new DKG protocol](https://eprint.iacr.org/2021/339) that works over an *asynchronous network* and is quite *robust* (it will still succeed if up to a third of the nodes in a subnet are crashed or corrupt) while still delivering acceptable performance. In addition to generating a new key, this protocol can also be used to reshare an existing key. This functionality is essential to enable autonomous evolution of the IC topology as subnet membership changes over time.
