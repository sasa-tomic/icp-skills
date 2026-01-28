# ICP Skills Development Plan

## Skill Categories

Based on the content in `learn-md/` (75 conceptual articles) and `portal/docs/` (318+ developer docs), here are all the logical skill categories for complete ICP coverage:

### Core Development Skills

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 1 | `icp-fundamentals` | ICP architecture, terminology, how it works (subnets, canisters, principals, consensus) | High |
| 2 | `icp-dev-environment` | dfx CLI, dfxvm, identities, cycles, local replica setup | High |
| 3 | `icp-backend-motoko` | Motoko language, patterns, actor model, stable memory, orthogonal persistence | High |
| 4 | `icp-backend-rust` | Rust CDK (ic-cdk), stable structures, memory management, async patterns | High |
| 5 | `icp-frontend` | Asset canisters, serving web apps, custom domains, React/framework integration | High |
| 6 | `icp-canister-management` | Deployment, upgrades, cycles top-up, settings, snapshots, logs, deletion | High |

### Integration & Communication

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 7 | `icp-candid` | Candid IDL, type system, interface definitions, serialization | High |
| 8 | `icp-agents` | JavaScript/Rust/Python agents, inter-canister calls, query vs update | Medium |
| 9 | `icp-authentication` | Internet Identity, alternative origins, session management | High |

### Chain Fusion (Cross-chain)

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 10 | `icp-chain-fusion-bitcoin` | Bitcoin integration, ckBTC, threshold ECDSA, signing transactions | High |
| 11 | `icp-chain-fusion-ethereum` | Ethereum integration, ckETH, EVM RPC canister, signing ETH transactions | High |
| 12 | `icp-chain-key-crypto` | Chain-key cryptography, threshold signatures, VetKeys | Medium |

### DeFi & Tokens

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 13 | `icp-tokens-icrc` | ICRC-1/2/7/37 standards, token creation, ledger integration | High |
| 14 | `icp-defi` | Ledgers, token swaps, Rosetta API, exchange integration | Medium |

### Governance

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 15 | `icp-governance-nns` | Network Nervous System, neurons, staking, voting, proposals | Medium |
| 16 | `icp-governance-sns` | Service Nervous System, launching DAOs, tokenomics, SNS lifecycle | Medium |

### Advanced Topics

| # | Skill Name | Description | Priority |
|---|------------|-------------|----------|
| 17 | `icp-network-features` | HTTPS outcalls, timers, randomness, SIMD, time/timestamps | Medium |
| 18 | `icp-security` | Security best practices, common vulnerabilities, auditing | High |
| 19 | `icp-testing` | PocketIC, unit testing, integration testing, benchmarking | Medium |
| 20 | `icp-optimization` | Performance tuning, cycle optimization, Wasm optimization | Low |

---

## Progress Tracker

- [ ] `icp-fundamentals`
- [ ] `icp-dev-environment`
- [x] `icp-backend-motoko`
- [ ] `icp-backend-rust`
- [ ] `icp-frontend`
- [ ] `icp-canister-management`
- [ ] `icp-candid`
- [ ] `icp-agents`
- [ ] `icp-authentication`
- [ ] `icp-chain-fusion-bitcoin`
- [ ] `icp-chain-fusion-ethereum`
- [ ] `icp-chain-key-crypto`
- [ ] `icp-tokens-icrc`
- [ ] `icp-defi`
- [ ] `icp-governance-nns`
- [ ] `icp-governance-sns`
- [ ] `icp-network-features`
- [ ] `icp-security`
- [ ] `icp-testing`
- [ ] `icp-optimization`

---

## Notes

### Source Content Mapping

| Skill | Primary Sources |
|-------|----------------|
| fundamentals | `learn-md/` (What is ICP, How does ICP work, Overview) |
| dev-environment | `portal/docs/building-apps/getting-started/`, `portal/docs/building-apps/developer-tools/` |
| backend-motoko | `portal/docs/motoko/` (submodule), tutorials |
| backend-rust | `portal/docs/tutorials/developer-liftoff-rust/` |
| frontend | `portal/docs/building-apps/frontends/` |
| canister-management | `portal/docs/building-apps/canister-management/` |
| candid | `portal/docs/building-apps/interact-with-canisters/candid/` |
| agents | `portal/docs/building-apps/interact-with-canisters/agents/` |
| authentication | `portal/docs/building-apps/authentication/` |
| chain-fusion-* | `portal/docs/building-apps/chain-fusion/`, `learn-md/` (Bitcoin/Ethereum integration) |
| tokens-icrc | `portal/docs/defi/token-standards/` |
| governance-* | `portal/docs/building-apps/governing-apps/`, `learn-md/` (NNS, Neurons, Proposals) |
| security | `portal/docs/building-apps/security/` |
| testing | `portal/docs/building-apps/test/` |

### Skill Dependencies

```
icp-fundamentals
    └── icp-dev-environment
            ├── icp-backend-motoko
            ├── icp-backend-rust
            └── icp-frontend
                    └── icp-canister-management
                            ├── icp-candid
                            ├── icp-agents
                            └── icp-authentication

icp-chain-key-crypto
    ├── icp-chain-fusion-bitcoin
    └── icp-chain-fusion-ethereum

icp-tokens-icrc
    └── icp-defi

icp-governance-nns
    └── icp-governance-sns
```

---

## icp-backend-motoko Remaining Improvements

Items not yet addressed for the Motoko skill:

### Language Features (SKILL.md gaps)

- [x] **Pipe operator (`|>`)** - Functional composition syntax for readable code chains
- [x] **async\*/await\* (Computation types)** - Efficient async abstraction without overhead of full futures
- [x] **Recursive types** - Complete coverage (added to advanced.md)
- [x] **Randomness** - raw_rand, Random module, fuzz/idempotency-keys packages
- [x] **Enhanced orthogonal persistence (EOP)** - The new default persistence mode
- [x] **`persistent actor` keyword** - New syntax for EOP actors
- [x] **64-bit heap storage** - Extended memory limits with EOP
- [x] **Float type and operations** - Base library Float module (added to patterns.md)
- [x] **Hash module** - Hashing utilities from base library (added to patterns.md)
- [x] **`transient` keyword** - Marking non-persistent actor fields in EOP (added to SKILL.md)
- [x] **try-finally** - Error handling with cleanup blocks (added to SKILL.md)

### Advanced Topics (advanced.md gaps)

- [x] **ExperimentalInternetComputer module** - Composite queries API details
- [x] **lowmemory system function** - Memory warning hook (was already present)
- [x] **Graph-copy-based stabilization** - Large heap migration process
- [x] **wasm_memory_persistence upgrade option** - IC upgrade options for EOP
- [x] **Migration from legacy to EOP** - Step-by-step migration guide

### Data Structures (patterns.md gaps)

- [x] **List module** - Functional linked list patterns
- [x] **Deque module** - Double-ended queue (added to patterns.md)
- [ ] **Heap module** - Priority queue / min-heap
- [ ] **Stack module** - LIFO data structure (use List instead)
- [x] **OrderedMap/OrderedSet** - Ordered key-value and set structures
- [ ] **RBTree** - Red-black tree from base library (OrderedMap covers most use cases)

### Popular mops Packages (patterns.md gaps)

- [x] **map package** - Stable hash maps (mo:map)
- [x] **vector package** - Memory-efficient resizable arrays (mentioned)
- [x] **stableheapbtreemap** - Persistent B-tree maps (mentioned)
- [x] **itertools** - Iterator utilities and combinators (in utility table)

### HTTP and Web (new section added)

- [x] **HTTP request/response handling** - http_request interface
- [x] **http-types package** - Standard HTTP types
- [x] **server package** - Express-like server framework
- [x] **Certified HTTP responses** - certified-assets, certified-http packages
- [ ] **WebSockets** - ic-websocket-cdk package (mentioned but no example)

### Cryptography (new section added)

- [x] **sha2/sha3 packages** - SHA hashing implementations
- [ ] **ed25519 package** - Signature verification (mentioned but no example)
- [ ] **libsecp256k1** - Bitcoin/Ethereum crypto
- [x] **ic-certification package** - Canister signatures (mentioned)

### Encoding and Serialization (patterns.md gaps)

- [x] **serde package** - JSON/CBOR serialization
- [ ] **candid package** - Candid encoding/decoding (mentioned but no example)
- [ ] **cbor package** - CBOR format support
- [ ] **json.mo package** - JSON formatting

### Utilities (patterns.md gaps)

- [x] **datetime package** - Date/time manipulation
- [x] **uuid package** - UUID generation (mentioned)
- [x] **bench package** - Benchmarking (added to testing.md)
- [x] **time-consts package** - Time constants (in utility table)

### Design Patterns (patterns.md)

- [x] **Objects and Classes** - `object` and `class` declarations for encapsulated state (added to patterns.md)
- [x] **Object subtyping** - Using objects as interface contracts (added to patterns.md)
- [x] **State Machine pattern** - Using variants for explicit state machines (added to patterns.md)
- [x] **Pagination pattern** - Cursor-based and offset-based pagination (added to patterns.md)
- [x] **Retry with backoff pattern** - Reliable inter-canister calls with exponential backoff (added to patterns.md)
- [x] **Authorization patterns** - Caller validation module and usage idioms (added to style.md)

### Testing (testing.md gaps)

- [x] **Benchmarking with `mops bench`** - Performance testing
- [ ] **Property-based testing** - Fuzz testing patterns (basic mention exists)

### External Integrations

- [ ] ExperimentalInternetIdentity module usage
- [ ] Certified assets in detail (beyond basic CertifiedData)

### Style Guide (style.md)

- [x] **Pipe operator usage** - Added idioms and when to use
- [x] **async* patterns** - Added anti-pattern section
- [x] **Loop with index** - Common pattern for indexed iteration
- [x] **Async in loops** - Sequential vs parallel async patterns
- [x] **Type aliases** - When and how to use for readability
- [x] **Variant exhaustiveness** - Pattern matching best practices
- [x] **Generic function patterns** - Using type parameters effectively (in advanced.md)
- [x] **Common Idioms Quick Reference** - Type conversions, subaccount computation, iterator compositions, debug patterns
