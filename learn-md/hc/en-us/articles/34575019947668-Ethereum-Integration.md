# Ethereum Integration

Canister smart contracts on ICP can directly interact with the Ethereum network and other networks that are using the Ethereum Virtual Machine (EVM), such as Polygon and Avalanche. This integration is possible thanks to ICP's HTTPS outcalls and chain-key signatures, which allow Ethereum state to be queried and Ethereum transactions to be signed and submitted by canisters.

- [HTTPS outcalls:](/hc/en-us/articles/34211194553492) To query information from Ethereum and other EVM networks, HTTPS outcalls are used. HTTPS outcalls can obtain information from external sources. In this integration, they're used to obtain data from JSON-RPC services by querying Ethereum's transactions, addresses, and block information. To facilitate JSON-RPC calls, the [EVM RPC canister](https://dashboard.internetcomputer.org/canister/7hfb6-caaaa-aaaar-qadga-cai) provides an API endpoint that canisters can use.
- [Chain-key signatures for ECDSA:](/hc/en-us/articles/34209497587732) A canister can have an Ethereum address and sign transactions for that address in a secure and decentralized way using chain-key cryptography. This allows canisters to hold Ethereum natively. Messages sent by the smart contract can be signed in this way, enabling calling any smart contract on Ethereum from the canister.

This functionality also forms the basis for EVM-based [chain-key tokens](/hc/en-us/articles/34211397080980), like ckETH, ckUSDC, and many more.

## EVM RPC canister

Canisters deployed on ICP are able to communicate with the Ethereum blockchain and other EVM-compatible networks using the EVM RPC canister.  By sending messages to this canister, Ethereum smart contract states can be queried and Ethereum transactions can be submitted.

Beyond the Ethereum blockchain, this canister also has partial support for Polygon, Avalanche, and other popular EVM networks.

###

To interact with these external chains, the EVM RPC canister utilizes the ICP's HTTPS outcalls to make calls to JSON-RPC service providers. These services, such as Cloudflare and Alchemy, provide public APIs for interacting with blockchain networks. The EVM RPC canister acts as a gateway for a dapp's canisters to communicate with and query information from EVM-compatible chains. It provides endpoints that ICP developers can use to interact with Ethereum smart contracts and ensures that the responses received from the Ethereum network are secure and immediately useful within a canister.

When a canister makes a request to the EVM RPC canister for a specified RPC method, the EVM RPC canister makes a HTTPS outcall to one or more RPC endpoints on behalf of that canister. The HTTPs outcalls mechanism guarantees that at least 2/3 of the subnet's nodes agree on the response obtained from the server. Once the response is validated, it is sent to the canister that originated the request.

By default for Candid-RPC methods such as `eth_getTransactionReceipt`, the EVM RPC canister sends the same request to at least three different RPC providers and compares the results. If there are discrepancies, the caller receives a set of inconsistent results to handle in a way that makes sense for the use case. Instead of relying on the default, the caller can specify the total number of providers to be queried or even list the concrete providers of choice. Moreover, the caller can also set a minimum number of providers that must return the same (non-error) result.

The EVM RPC is controlled by the [Network Nervous System DAO](/hc/en-us/articles/33692645961236), i.e., its functionality cannot be changed by a single entity. Together, these mechanisms ensure that no trust in additional parties (bridges or oracles) are necessary for the caller canister to send transactions and to condition executions on Ethereum state.

## Additional Resources

[Blog article](https://medium.com/dfinity/icp-ethereum-how-icps-evm-rpc-canister-connects-the-networks-b57909efecf6)

[Developer docs on EVM RPC canister](https://internetcomputer.org/docs/current/developer-docs/multi-chain/ethereum/evm-rpc/overview)

<https://github.com/dfinity/evm-rpc-canister>
