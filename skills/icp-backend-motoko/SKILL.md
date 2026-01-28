---
name: icp-backend-motoko
description: Develop ICP canister backends using Motoko. Covers actors, types, async patterns, stable memory, upgrades, access control, and error handling. Use when writing Motoko code, creating canisters, working with actors, or asking about Motoko syntax and patterns.
---

# ICP Backend Development with Motoko

Motoko is a programming language designed specifically for the Internet Computer Protocol (ICP). It makes writing canister smart contracts intuitive with built-in support for actors, async messaging, and stable memory.

## Quick Reference

### Project Structure

```
my_canister/
├── dfx.json              # Project config
└── src/
    └── my_canister/
        └── main.mo       # Main actor file
```

### Minimal Actor

```motoko
actor {
  public func greet(name : Text) : async Text {
    "Hello, " # name # "!"
  };
}
```

### Create & Deploy

```bash
dfx new my_project --type motoko --no-frontend
cd my_project
dfx start --background
dfx deploy
dfx canister call my_project_backend greet '("World")'
```

---

## Core Concepts

### Actors

Every Motoko canister is an **actor** - an isolated unit with private state that communicates via async messages.

```motoko
actor Counter {
  var count : Nat = 0;  // Private mutable state

  public func inc() : async Nat {
    count += 1;
    count
  };

  public query func get() : async Nat {
    count
  };
}
```

Key points:
- `actor { }` defines a canister
- State (`var`) is private by default
- `public` functions are callable externally
- `query` functions are fast reads (no state changes)
- All public functions return `async T`

### Variables and Declarations

```motoko
let x : Nat = 42;        // Immutable
var y : Nat = 0;         // Mutable
y := y + 1;              // Assignment uses :=

// Block expressions with do { }
let result = do {
  let a = 1;
  let b = 2;
  a + b  // Last expression is the result
};

// Discard return values with ignore
ignore await someCanister.fire();
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `Nat` | Natural numbers (0, 1, 2, ...) | `let n : Nat = 42` |
| `Int` | Integers (..., -1, 0, 1, ...) | `let i : Int = -5` |
| `Text` | Unicode strings | `"hello"` |
| `Bool` | Boolean | `true`, `false` |
| `Blob` | Binary data | `"\00\01\02"` |
| `Principal` | Identity/canister ID | `Principal.fromText("...")` |
| `?T` | Optional (null or value) | `?Nat`, `null`, `?42` |
| `[T]` | Immutable array | `[1, 2, 3]` |
| `[var T]` | Mutable array | `[var 1, 2, 3]` |
| `(T1, T2)` | Tuple | `(42, "hello")` |
| `{a: T1; b: T2}` | Record/object | `{name = "Bob"; age = 30}` |
| `#tag1 \| #tag2` | Variant | `#ok(42)`, `#err("fail")` |

### Imports

```motoko
import Debug "mo:base/Debug";       // Base library
import Array "mo:base/Array";
import Principal "mo:base/Principal";
import Time "mo:base/Time";
import Result "mo:base/Result";
import Types "./types";             // Local module (relative path)
```

Common base library modules: `Array`, `Blob`, `Buffer`, `Debug`, `Error`, `Float`, `Hash`, `HashMap`, `Int`, `Iter`, `List`, `Nat`, `Option`, `OrderedMap`, `OrderedSet`, `Principal`, `Random`, `Region`, `Result`, `Text`, `Time`, `Timer`, `TrieMap`.

> **Note:** A new `mo:core` standard library is being developed with improved data structures that are natively stable (no pre/post-upgrade hooks needed). For new projects, consider using `mo:core/Map`, `mo:core/Set` instead of `HashMap`/`TrieMap`. See the [base-to-core migration guide](https://internetcomputer.org/docs/motoko/main/base-core-migration) for details.

### Package Management with mops

[mops](https://mops.one) is the Motoko package manager.

```bash
# Install mops (requires Node.js)
npm i -g ic-mops

# Initialize in project
mops init

# Add a package
mops add base          # Base library
mops add map           # Third-party package
mops add github-user/repo  # GitHub package

# Install dependencies
mops install

# Update packages
mops update
```

**mops.toml configuration:**

```toml
[package]
name = "my_canister"
version = "0.1.0"

[dependencies]
base = "0.11.1"
map = "9.0.1"
```

**Using packages:**

```motoko
import Map "mo:map/Map";           // From mops package
import { phash } "mo:map/Map";     // Named import
import Base "mo:base/Array";       // Base library (also via mops)
```

**dfx.json configuration for mops:**

```json
{
  "defaults": {
    "build": {
      "packtool": "mops sources"
    }
  }
}
```

### Pipe Operator

The pipe operator `|>` makes nested function calls more readable by flowing data left-to-right:

```motoko
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import List "mo:base/List";

// Without pipes - hard to read
let result1 = { data = Array.filter(List.toArray(List.fromArray(Iter.toArray(Iter.range(0, 10)))), func(n : Nat) : Bool { n % 3 == 0 }) };

// With pipes - reads naturally
let result2 = Iter.range(0, 10)
  |> Iter.toArray(_)
  |> List.fromArray(_)
  |> List.toArray(_)
  |> Array.filter(_, func(n : Nat) : Bool { n % 3 == 0 })
  |> { data = _ };
```

Use `_` as the placeholder for the piped value. Multiple `_` references in the same pipe step refer to the same value.

---

## Async and Inter-Canister Calls

### Shared Functions

Shared functions are callable remotely and return futures:

```motoko
public shared func process(data : Text) : async Text {
  // Can call other canisters here
  "processed: " # data
}
```

### Await

Use `await` to get the result of an async call:

```motoko
let result : Text = await someCanister.process("input");
```

### Caller Identification

```motoko
shared(msg) actor class MyActor() {
  let owner = msg.caller;  // Principal who deployed

  public shared(msg) func whoami() : async Principal {
    msg.caller  // Principal of current caller
  };
}
```

### Computation Types (async*/await*)

Use `async*` for efficient async abstraction without the overhead of full futures:

```motoko
actor {
  var logging = true;

  // async* - no message overhead, runs inline
  func maybeLog(msg : Text) : async* () {
    if (logging) { await Logger.log(msg) };
  };

  public func doStuff() : async () {
    await* maybeLog("step 1");  // Runs inline, no extra message
    await* maybeLog("step 2");
  };
}
```

| Feature | `async` / `await` | `async*` / `await*` |
|---------|-------------------|---------------------|
| Message cost | Sends message to self | None (inline execution) |
| Execution | Eager - schedules immediately | Lazy - runs when awaited |
| Repeatable | No - same future, same result | Yes - each await* re-runs |
| Commit point | Yes - state committed at await | No - not a commit point |

**Warning**: `await*` is NOT a commit point. Traps may roll back to the last `await`, not to the `await*`.

---

## Randomness

ICP provides cryptographic randomness via the management canister's VRF:

```motoko
import Random "mo:base/Random";

actor {
  // Get 32 bytes of cryptographic randomness
  public func getRandomBytes() : async Blob {
    await Random.blob()
  };

  // Use Random.Finite for structured random values
  public func flipCoin() : async ?Bool {
    let entropy = await Random.blob();
    let random = Random.Finite(entropy);
    random.coin()  // ?true or ?false
  };

  // Generate random number in range [0, 2^p - 1]
  public func randomInRange(bits : Nat8) : async ?Nat {
    let random = Random.Finite(await Random.blob());
    random.range(bits)
  };
}
```

| Method | Security | Use Case |
|--------|----------|----------|
| `Random.blob()` | Cryptographic | Secure keys, fairness-critical |
| `Random.Finite` | Cryptographic | Structured random values |
| [`fuzz`](https://mops.one/fuzz) package | Seed-dependent | Testing, procedural generation |
| [`idempotency-keys`](https://mops.one/idempotency-keys) | Seed-dependent | UUID v4 generation |

---

## Persistence and Upgrades

Motoko provides **orthogonal persistence** - your program state automatically persists across calls without explicit database operations.

### Enhanced Orthogonal Persistence (Default)

Enhanced orthogonal persistence (EOP) is the default mode. It uses a **stable heap** that persists main memory across upgrades with 64-bit addressing:

```motoko
// Use 'persistent actor' for EOP (recommended)
persistent actor Counter {
  var count = 0;  // Automatically persists across upgrades!

  public func inc() : async Nat {
    count += 1;
    count
  };
}
```

| Feature | Enhanced (EOP) | Classical |
|---------|----------------|-----------|
| Heap limit | 64-bit (large) | 4GB (32-bit) |
| Upgrade speed | Fast (no serialization) | Slow (Candid serialization) |
| Stable keyword | Optional (all vars stable) | Required for persistence |
| Default since | moc 0.13+ | Legacy |

**Compatible upgrade changes** (EOP automatically handles):
- Adding/removing actor fields
- Changing `let` to `var` and vice-versa
- Removing object fields, adding variant fields
- Changing `Nat` to `Int`

### Classical Persistence (Legacy)

Use `stable` keyword to persist specific variables (legacy mode):

```motoko
actor {
  stable var counter : Nat = 0;  // Survives upgrades
  var cache : Text = "";          // Lost on upgrade
}
```

Enable legacy mode with compiler flag `--legacy-persistence`.

### Stable Variables

Use `stable` to persist data across upgrades:

```motoko
actor {
  stable var counter : Nat = 0;  // Survives upgrades
  var cache : Text = "";          // Lost on upgrade

  public func inc() : async Nat {
    counter += 1;
    counter
  };
}
```

### Transient Variables

In a `persistent actor`, all fields are stable by default. Use `transient` for fields that should reset on upgrade:

```motoko
persistent actor {
  var count = 0;                      // Implicitly stable, survives upgrades

  transient var cache : [Text] = [];  // Reset to [] on every upgrade
  transient let rng = Random.crypto(); // Objects with methods must be transient
}
```

**When to use `transient`:**
- Caches that can be rebuilt
- Iterators (can't be serialized)
- Objects with methods (not stable types)
- Session state that shouldn't persist

### Pre/Post Upgrade Hooks

For complex data structures that aren't directly stable:

```motoko
import Array "mo:base/Array";

actor {
  stable var stableEntries : [(Text, Nat)] = [];
  var map = HashMap.HashMap<Text, Nat>(10, Text.equal, Text.hash);

  system func preupgrade() {
    stableEntries := Iter.toArray(map.entries());
  };

  system func postupgrade() {
    map := HashMap.fromIter(stableEntries.vals(), 10, Text.equal, Text.hash);
    stableEntries := [];
  };
}
```

### Upgrade Command

```bash
dfx canister install my_canister --mode upgrade
```

---

## Access Control

### Basic Principal Check

```motoko
import Principal "mo:base/Principal";

shared(msg) actor class SecureActor() {
  let owner = msg.caller;

  public shared(msg) func adminOnly() : async () {
    assert(msg.caller == owner);
    // admin action
  };

  public shared(msg) func rejectAnonymous() : async () {
    assert(not Principal.isAnonymous(msg.caller));
  };
}
```

### Role-Based Access

```motoko
public type Role = { #owner; #admin; #user };

stable var roles : [(Principal, Role)] = [];

func getRole(p : Principal) : ?Role {
  for ((principal, role) in roles.vals()) {
    if (principal == p) return ?role;
  };
  null
};

func requireRole(caller : Principal, required : Role) {
  switch (getRole(caller)) {
    case (?#owner) {};  // Owner can do anything
    case (?role) { assert(role == required) };
    case null { assert(false) };
  };
};
```

---

## Error Handling

### Option Types

```motoko
func find(id : Nat) : ?Text {
  if (id == 1) { ?"found" } else { null }
};

switch (find(1)) {
  case null { Debug.print("not found") };
  case (?value) { Debug.print(value) };
};
```

### Result Types

```motoko
import Result "mo:base/Result";

type MyError = { #notFound; #unauthorized; #invalid : Text };

func process(id : Nat) : Result.Result<Text, MyError> {
  if (id == 0) { #err(#invalid("id cannot be 0")) }
  else if (id > 100) { #err(#notFound) }
  else { #ok("success") }
};
```

### Throwing Errors (Async Context Only)

```motoko
import Error "mo:base/Error";

public func riskyOperation() : async () {
  throw Error.reject("Something went wrong");
};

public func safeCall() : async Text {
  try {
    await riskyOperation();
    "success"
  } catch (e) {
    "failed: " # Error.message(e)
  }
};
```

### Try-Finally for Cleanup

Use `finally` to run cleanup code regardless of success or failure:

```motoko
public func withCleanup() : async () {
  var resource = acquireResource();
  try {
    await processResource(resource);
  } finally {
    releaseResource(resource);  // Always runs
  }
};
```

**Best Practice**: Prefer `Result` over exceptions for expected errors. Use exceptions for truly exceptional conditions.

---

## Common Patterns

### Actor Classes (Multiple Instances)

```motoko
// Bucket.mo
actor class Bucket(n : Nat, i : Nat) {
  var data : [var ?Text] = Array.init(n, null);

  public func put(key : Nat, value : Text) : async () {
    assert((key % n) == i);
    data[key] := ?value;
  };
};
```

### Timers

```motoko
import Timer "mo:base/Timer";

actor {
  stable var count = 0;

  let timerId = Timer.recurringTimer<system>(#seconds 60, func() : async () {
    count += 1;
    Debug.print("Tick: " # Nat.toText(count));
  });

  public func cancelTimer() : async () {
    Timer.cancelTimer(timerId);
  };
}
```

### Message Inspection (DoS Protection)

```motoko
import Principal "mo:base/Principal";

actor {
  system func inspect({ caller : Principal; arg : Blob }) : Bool {
    // Reject anonymous callers
    if (Principal.isAnonymous(caller)) return false;
    // Reject large payloads
    if (arg.size() > 1024) return false;
    true
  };
}
```

---

## Optimization

### Enable wasm-opt in dfx.json

```json
{
  "canisters": {
    "my_canister": {
      "type": "motoko",
      "main": "src/my_canister/main.mo",
      "optimize": "cycles"
    }
  }
}
```

Options:
- `"cycles"` - Optimize for cycle usage (~10% reduction)
- `"size"` - Optimize for binary size (~16% reduction)

### Incremental Garbage Collection

```json
{
  "canisters": {
    "my_canister": {
      "type": "motoko",
      "main": "src/my_canister/main.mo",
      "args": "--incremental-gc"
    }
  }
}
```

---

## Debugging

```motoko
import Debug "mo:base/Debug";

Debug.print("Simple message");
Debug.print(debug_show(myComplexValue));  // Show any value

// Trap with message
assert(condition);  // Traps if false
Debug.trap("Error message");
```

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Use `persistent actor` (EOP) | All state survives upgrades automatically |
| Use `query` for read-only functions | 100x faster, no consensus needed |
| Prefer `Result` over exceptions | Forces callers to handle errors explicitly |
| Validate `msg.caller` for sensitive ops | Prevents unauthorized access |
| Use `inspect` for DoS protection | Reject bad requests before execution |
| Use `async*` for helper functions | Avoids message overhead of `async` |
| Use pipe operator for chains | Improves readability of transformations |
| Initialize vars with defaults | Ensures valid state on first deploy |
| Use `assert` for invariants | Fail fast on invalid state |
| Test upgrades locally | Catch compatibility issues early |

---

## Additional Resources

**In this skill:**
- [patterns.md](patterns.md) - Data structures (List, OrderedMap, stable maps), HTTP handling, cryptography, encoding, mops packages, inter-canister calls, cycles management, deduplication
- [style.md](style.md) - Idiomatic style guide, naming conventions, functional patterns, pipe operator idioms, async* patterns
- [advanced.md](advanced.md) - Modules, shared types, atomicity, regions, management canister, upgrade migrations, EOP migration, graph-copy stabilization, canister snapshots, troubleshooting
- [testing.md](testing.md) - mops test framework, benchmarking with `mops bench`, PocketIC integration testing, e2e testing, CI setup

**External documentation:**
- [Motoko Language Manual](https://internetcomputer.org/docs/motoko/main/reference/language-manual)
- [Base Library Reference](https://internetcomputer.org/docs/motoko/main/base/)
- [Motoko Playground](https://m7sm4-2iaaa-aaaab-qabra-cai.raw.ic0.app/)
- [mops Package Registry](https://mops.one/) - Community packages
