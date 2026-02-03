<!-- 
  ICP Development Skill: icp-backend-motoko
  Generated: 2026-01-29
  Source: https://github.com/sasa-tomic/icp-skills
  
  Install (per-project):
    curl -fsSL https://github.com/sasa-tomic/icp-skills/raw/main/dist/icp-backend-motoko.md -o <FILE>
  
  Per-project locations:
    Claude Code:   CLAUDE.md
    OpenCode:      AGENTS.md
    Copilot:       .github/copilot-instructions.md  
    Cursor:        .cursor/rules/icp-backend-motoko.mdc
    Windsurf:      .windsurfrules
    Aider:         CONVENTIONS.md
  
  Per-user (global) locations:
    Claude Code:   ~/.claude/CLAUDE.md
    OpenCode:      ~/.config/opencode/AGENTS.md
    Cursor:        ~/.cursor/rules/icp-backend-motoko.mdc
    Aider:         ~/.aider.conf.yml (read: path/to/file)
-->

## Contents

- [ICP Backend Development with Motoko](#icp-backend-development-with-motoko)
  - [Quick Reference](#quick-reference)
  - [Core Concepts](#core-concepts)
  - [Async and Inter-Canister Calls](#async-and-inter-canister-calls)
  - [Randomness](#randomness)
  - [Persistence and Upgrades](#persistence-and-upgrades)
  - [Access Control](#access-control)
  - [Error Handling](#error-handling)
  - [Common Patterns](#common-patterns)
  - [Optimization](#optimization)
  - [Debugging](#debugging)
  - [Best Practices](#best-practices)
  - [Additional Resources](#additional-resources)
- [Motoko Patterns Reference](#motoko-patterns-reference)
  - [Objects and Classes](#objects-and-classes)
  - [Data Structures](#data-structures)
  - [Pattern Matching](#pattern-matching)
  - [Inter-Canister Calls](#inter-canister-calls)
  - [Candid Types](#candid-types)
  - [ICRC Token Standards](#icrc-token-standards)
  - [Time and Timestamps](#time-and-timestamps)
  - [Float Operations](#float-operations)
  - [Hash Operations](#hash-operations)
  - [Cycles Management](#cycles-management)
  - [HTTP Outcalls (Experimental)](#http-outcalls-experimental)
  - [Testing Patterns](#testing-patterns)
  - [State Machine Pattern](#state-machine-pattern)
  - [Pagination Pattern](#pagination-pattern)
  - [Retry Pattern for Inter-Canister Calls](#retry-pattern-for-inter-canister-calls)
  - [Common Gotchas](#common-gotchas)
  - [Actor Class Instantiation](#actor-class-instantiation)
  - [Cycles Management](#cycles-management)
  - [Tooling](#tooling)
  - [Deduplication Patterns](#deduplication-patterns)
  - [HTTP Request Handling](#http-request-handling)
  - [Cryptography Packages](#cryptography-packages)
  - [Encoding and Serialization](#encoding-and-serialization)
  - [Utility Packages](#utility-packages)

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


---

# Motoko Patterns Reference

## Objects and Classes

Unlike actors (which are deployed as canisters), objects and classes are local constructs for encapsulating state and behavior within a canister.

### Object Declarations

Use `object` for singletons with encapsulated state:

```motoko
object Counter {
  var count = 0;

  public func inc() : Nat {
    count += 1;
    count
  };

  public func get() : Nat { count };

  // Private method - not accessible outside
  func reset() { count := 0 };
};

let x = Counter.inc();  // 1
let y = Counter.get();  // 1
```

### Class Declarations

Use `class` to create multiple objects with the same structure:

```motoko
class Account(initialBalance : Nat) = self {
  var balance = initialBalance;

  public func deposit(amount : Nat) : Nat {
    balance += amount;
    balance
  };

  public func withdraw(amount : Nat) : ?Nat {
    if (amount > balance) return null;
    balance -= amount;
    ?balance
  };

  public func getBalance() : Nat { balance };

  // self reference for returning the object itself
  public func getSelf() : Account { self };
};

let alice = Account(100);
let bob = Account(500);
ignore alice.deposit(50);  // Alice: 150, Bob: 500
```

### Object Subtyping

Objects with more fields are subtypes of objects with fewer fields:

```motoko
type HasBalance = { getBalance : () -> Nat };
type CanDeposit = { getBalance : () -> Nat; deposit : Nat -> Nat };

// Any Account can be used where HasBalance is expected
func printBalance(account : HasBalance) {
  Debug.print("Balance: " # Nat.toText(account.getBalance()));
};

printBalance(alice);  // Works - Account has getBalance
```

### When to Use Objects vs Modules

| Use Case | Recommendation |
|----------|----------------|
| Stateless utilities | Module |
| Encapsulated mutable state | Object/Class |
| Multiple instances needed | Class |
| Singleton with state | Object |
| Sharable data | Records (objects can't be sent across canisters) |

---

## Data Structures

### HashMap

```motoko
import HashMap "mo:base/HashMap";
import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Iter "mo:base/Iter";

actor {
  // Create HashMap (initial size, equality fn, hash fn)
  var users = HashMap.HashMap<Text, Nat>(10, Text.equal, Text.hash);

  public func addUser(name : Text, age : Nat) : async () {
    users.put(name, age);
  };

  public func getUser(name : Text) : async ?Nat {
    users.get(name)
  };

  public func removeUser(name : Text) : async () {
    users.delete(name);
  };

  public query func listUsers() : async [(Text, Nat)] {
    Iter.toArray(users.entries())
  };

  // Make stable for upgrades
  stable var stableUsers : [(Text, Nat)] = [];

  system func preupgrade() {
    stableUsers := Iter.toArray(users.entries());
  };

  system func postupgrade() {
    users := HashMap.fromIter(stableUsers.vals(), 10, Text.equal, Text.hash);
    stableUsers := [];
  };
}
```

### Buffer (Dynamic Array)

```motoko
import Buffer "mo:base/Buffer";

actor {
  let items = Buffer.Buffer<Text>(10);  // Initial capacity

  public func add(item : Text) : async () {
    items.add(item);
  };

  public func getAll() : async [Text] {
    Buffer.toArray(items)
  };

  public func size() : async Nat {
    items.size()
  };

  public func clear() : async () {
    items.clear();
  };
}
```

### TrieMap (Functional HashMap)

TrieMap has the same interface as HashMap but different performance characteristics. Like HashMap, it is **not stable** and requires pre/post-upgrade hooks:

```motoko
import TrieMap "mo:base/TrieMap";
import Text "mo:base/Text";
import Iter "mo:base/Iter";

actor {
  // TrieMap is NOT stable - use same pattern as HashMap
  // Note: TrieMap constructor takes (equalFn, hashFn) - no initial capacity
  var map = TrieMap.TrieMap<Text, Nat>(Text.equal, Text.hash);

  // Stable storage for upgrades
  stable var stableEntries : [(Text, Nat)] = [];

  public func set(key : Text, value : Nat) : async () {
    map.put(key, value);
  };

  system func preupgrade() {
    stableEntries := Iter.toArray(map.entries());
  };

  system func postupgrade() {
    map := TrieMap.fromIter(stableEntries.vals(), Text.equal, Text.hash);
    stableEntries := [];
  };
}
```

### List (Functional Linked List)

```motoko
import List "mo:base/List";

// List is a recursive type: ?(T, List<T>)
type MyList = List.List<Nat>;

let empty : MyList = List.nil();
let list1 = List.push(1, empty);        // ?(1, null)
let list2 = List.push(2, list1);        // ?(2, ?(1, null))

// Common operations
let size = List.size(list2);            // 2
let last = List.last(list2);            // ?1
let reversed = List.reverse(list2);     // ?(1, ?(2, null))
let arr = List.toArray(list2);          // [2, 1]

// Functional operations
let doubled = List.map<Nat, Nat>(list2, func(n) { n * 2 });
let evens = List.filter<Nat>(list2, func(n) { n % 2 == 0 });
```

### Deque (Double-Ended Queue)

```motoko
import Deque "mo:base/Deque";

actor {
  var queue = Deque.empty<Text>();

  // Add to front or back
  public func pushFront(item : Text) : async () {
    queue := Deque.pushFront(queue, item);
  };

  public func pushBack(item : Text) : async () {
    queue := Deque.pushBack(queue, item);
  };

  // Remove from front or back
  public func popFront() : async ?Text {
    switch (Deque.popFront(queue)) {
      case null { null };
      case (?(item, newQueue)) {
        queue := newQueue;
        ?item
      };
    }
  };

  public func popBack() : async ?Text {
    switch (Deque.popBack(queue)) {
      case null { null };
      case (?(newQueue, item)) {
        queue := newQueue;
        ?item
      };
    }
  };

  // Peek without removing
  public query func peekFront() : async ?Text {
    Deque.peekFront(queue)
  };
}
```

Use Deque for: sliding windows, BFS traversal, work queues with priority handling.

### OrderedMap (Sorted Key-Value)

```motoko
import OrderedMap "mo:base/OrderedMap";
import Nat "mo:base/Nat";

actor {
  var scores = OrderedMap.empty<Text, Nat>();
  let ops = OrderedMap.Make<Text>(Text.compare);

  public func addScore(name : Text, score : Nat) : async () {
    scores := ops.put(scores, name, score);
  };

  public query func getTopScores() : async [(Text, Nat)] {
    // Entries are in sorted order by key
    Iter.toArray(ops.entries(scores))
  };
}
```

### Stable Data Structures (mops packages)

For large-scale data, use stable-memory-backed structures:

```bash
mops add map              # Stable hash maps
mops add vector           # Memory-efficient arrays
mops add stableheapbtreemap  # Persistent B-trees
```

```motoko
// mo:map - Stable HashMap replacement
import Map "mo:map/Map";
import { thash } "mo:map/Map";

persistent actor {
  var users = Map.new<Text, Nat>();

  public func addUser(name : Text, age : Nat) : async () {
    Map.set(users, thash, name, age);
  };

  public query func getUser(name : Text) : async ?Nat {
    Map.get(users, thash, name)
  };
}
```

---

## Pattern Matching

### Switch on Variants

```motoko
type Status = {
  #pending;
  #active : { since : Int };
  #completed : { at : Int; result : Text };
  #failed : Text;
};

func describe(s : Status) : Text {
  switch (s) {
    case (#pending) { "Waiting to start" };
    case (#active({ since })) { "Active since " # Int.toText(since) };
    case (#completed({ at; result })) { "Done: " # result };
    case (#failed(reason)) { "Failed: " # reason };
  }
};
```

### Destructuring Records

```motoko
func fullName({ first : Text; middle : ?Text; last : Text }) : Text {
  switch (middle) {
    case null { first # " " # last };
    case (?m) { first # " " # m # " " # last };
  }
};

let name = fullName({ first = "John"; middle = ?"Q"; last = "Doe" });
```

### Tuple Patterns

```motoko
let pair = (42, "hello");
let (num, str) = pair;  // Destructure

switch ((maybeA, maybeB)) {
  case (null, null) { "both missing" };
  case (?a, null) { "only a: " # a };
  case (null, ?b) { "only b: " # b };
  case (?a, ?b) { "both: " # a # ", " # b };
};
```

---

## Inter-Canister Calls

### Define Remote Actor Type

```motoko
// Call another canister by its interface
actor {
  // Define the interface of the canister you want to call
  type RemoteActor = actor {
    getValue : () -> async Nat;
    setValue : (Nat) -> async ();
  };

  public func callRemote(canisterId : Principal) : async Nat {
    let remote : RemoteActor = actor(Principal.toText(canisterId));
    await remote.getValue()
  };
}
```

### Import Canister Interface

```motoko
// If you have the .did file, use Candid import
import RemoteCanister "canister:remote_canister";

actor {
  public func callIt() : async Text {
    await RemoteCanister.greet("World")
  };
}
```

---

## Candid Types

### Custom Types with Candid Annotations

```motoko
// These types are exposed in the Candid interface

public type UserId = Nat;

public type User = {
  id : UserId;
  name : Text;
  email : ?Text;
  roles : [Role];
};

public type Role = {
  #admin;
  #moderator;
  #user;
};

public type CreateUserRequest = {
  name : Text;
  email : ?Text;
};

public type CreateUserResponse = {
  #ok : User;
  #err : CreateUserError;
};

public type CreateUserError = {
  #nameTaken;
  #invalidEmail;
  #unauthorized;
};
```

---

## ICRC Token Standards

ICRC (Internet Computer Request for Comments) standards define token interfaces. The main standards are:

| Standard | Purpose |
|----------|---------|
| ICRC-1 | Fungible token base (like ERC-20) |
| ICRC-2 | Approve/transfer-from extension |
| ICRC-7 | Non-fungible tokens (like ERC-721) |

### Calling ICRC-1 Tokens

```motoko
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";

actor {
  // ICRC-1 ledger interface (subset)
  type ICRC1 = actor {
    icrc1_balance_of : shared query { owner : Principal; subaccount : ?Blob } -> async Nat;
    icrc1_transfer : shared {
      from_subaccount : ?Blob;
      to : { owner : Principal; subaccount : ?Blob };
      amount : Nat;
      fee : ?Nat;
      memo : ?Blob;
      created_at_time : ?Nat64;
    } -> async { #Ok : Nat; #Err : TransferError };
    icrc1_decimals : shared query () -> async Nat8;
    icrc1_symbol : shared query () -> async Text;
  };

  type TransferError = {
    #BadFee : { expected_fee : Nat };
    #BadBurn : { min_burn_amount : Nat };
    #InsufficientFunds : { balance : Nat };
    #TooOld;
    #CreatedInFuture : { ledger_time : Nat64 };
    #Duplicate : { duplicate_of : Nat };
    #TemporarilyUnavailable;
    #GenericError : { error_code : Nat; message : Text };
  };

  public func getBalance(ledger : Principal, owner : Principal) : async Nat {
    let token : ICRC1 = actor(Principal.toText(ledger));
    await token.icrc1_balance_of({ owner; subaccount = null })
  };

  public func transfer(ledger : Principal, to : Principal, amount : Nat) : async Result.Result<Nat, TransferError> {
    let token : ICRC1 = actor(Principal.toText(ledger));
    let result = await token.icrc1_transfer({
      from_subaccount = null;
      to = { owner = to; subaccount = null };
      amount;
      fee = null;  // Use default fee
      memo = null;
      created_at_time = null;
    });
    switch result {
      case (#Ok(blockIndex)) { #ok(blockIndex) };
      case (#Err(e)) { #err(e) };
    }
  };
}
```

### Using ICRC-2 Approve/TransferFrom

```motoko
type ICRC2 = actor {
  icrc2_approve : shared {
    from_subaccount : ?Blob;
    spender : { owner : Principal; subaccount : ?Blob };
    amount : Nat;
    expected_allowance : ?Nat;
    expires_at : ?Nat64;
    fee : ?Nat;
    memo : ?Blob;
    created_at_time : ?Nat64;
  } -> async { #Ok : Nat; #Err : ApproveError };

  icrc2_transfer_from : shared {
    spender_subaccount : ?Blob;
    from : { owner : Principal; subaccount : ?Blob };
    to : { owner : Principal; subaccount : ?Blob };
    amount : Nat;
    fee : ?Nat;
    memo : ?Blob;
    created_at_time : ?Nat64;
  } -> async { #Ok : Nat; #Err : TransferFromError };
};

// Pattern: User approves canister, then canister pulls funds
public shared(msg) func depositTokens(ledger : Principal, amount : Nat) : async Result<(), Text> {
  let token : ICRC2 = actor(Principal.toText(ledger));

  // Pull tokens from caller (requires prior approval)
  let result = await token.icrc2_transfer_from({
    spender_subaccount = null;
    from = { owner = msg.caller; subaccount = null };
    to = { owner = Principal.fromActor(this); subaccount = null };
    amount;
    fee = null;
    memo = null;
    created_at_time = null;
  });

  switch result {
    case (#Ok(_)) { #ok() };
    case (#Err(e)) { #err(debug_show(e)) };
  }
};
```

### Mops Packages for ICRC

```bash
mops add icrc1-types    # Type definitions
mops add icrc-ledger    # Full client implementation
```

```motoko
import ICRC1 "mo:icrc1-types";

// Use standardized types
let account : ICRC1.Account = { owner = principal; subaccount = null };
```

---

## Time and Timestamps

```motoko
import Time "mo:base/Time";
import Int "mo:base/Int";

actor {
  public func now() : async Int {
    Time.now()  // Nanoseconds since epoch
  };

  public func secondsSinceEpoch() : async Int {
    Time.now() / 1_000_000_000
  };

  stable var lastUpdate : Int = 0;

  public func updateIfStale() : async Bool {
    let current = Time.now();
    let oneHour = 3_600_000_000_000;  // 1 hour in nanoseconds

    if (current - lastUpdate > oneHour) {
      lastUpdate := current;
      true
    } else {
      false
    }
  };
}
```

---

## Float Operations

Motoko supports IEEE 754 double-precision floating-point numbers:

```motoko
import Float "mo:base/Float";
import Int "mo:base/Int";

actor {
  // Basic arithmetic
  public func calculate() : async Float {
    let a : Float = 3.14159;
    let b : Float = 2.71828;
    a + b * 2.0 - 1.5 / 0.5
  };

  // Math functions
  public func mathOps(x : Float) : async {
    sqrt : Float;
    sin : Float;
    log : Float;
    abs : Float;
  } {
    {
      sqrt = Float.sqrt(x);
      sin = Float.sin(x);
      log = Float.log(x);      // Natural log
      abs = Float.abs(x);
    }
  };

  // Comparisons (beware of floating-point precision)
  public func almostEqual(a : Float, b : Float, epsilon : Float) : async Bool {
    Float.abs(a - b) < epsilon
  };

  // Conversions
  public func conversions(n : Nat, i : Int) : async (Float, Float) {
    (Float.fromInt(Int.abs(i)), Float.fromInt(n))  // Nat -> Int -> Float
  };

  // Special values
  public func specialValues() : async { nan : Bool; inf : Bool } {
    let x = 0.0 / 0.0;   // NaN
    let y = 1.0 / 0.0;   // Infinity
    { nan = Float.isNaN(x); inf = not Float.isFinite(y) }
  };
}
```

| Function | Description |
|----------|-------------|
| `Float.sqrt(x)` | Square root |
| `Float.sin(x)`, `cos(x)`, `tan(x)` | Trigonometry |
| `Float.log(x)` | Natural logarithm |
| `Float.exp(x)` | e^x |
| `Float.pow(base, exp)` | Exponentiation |
| `Float.floor(x)`, `ceil(x)` | Rounding |
| `Float.abs(x)` | Absolute value |
| `Float.toInt(x)` | Truncate to Int |
| `Float.fromInt(i)` | Convert from Int |

**Warning**: Avoid storing Float in stable variables if exact precision matters (use scaled Nat instead for currency).

---

## Hash Operations

The Hash module provides utilities for building hash functions:

```motoko
import Hash "mo:base/Hash";
import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Blob "mo:base/Blob";

// Hash is just a Nat32
type Hash = Hash.Hash;

// Combine multiple hashes
func hashPair(a : Hash, b : Hash) : Hash {
  // XOR is NOT a good combiner - use this pattern instead
  let combined = a +% (b *% 31);  // Simple but effective
  combined
};

// Custom type hashing
type User = { id : Nat; name : Text };

func hashUser(u : User) : Hash {
  let idHash = Hash.hash(u.id);
  let nameHash = Text.hash(u.name);
  hashPair(idHash, nameHash)
};

// Using with HashMap
import HashMap "mo:base/HashMap";

let users = HashMap.HashMap<User, Nat>(
  10,
  func(a : User, b : User) : Bool { a.id == b.id and a.name == b.name },
  hashUser
);
```

### Built-in Hash Functions

| Type | Hash Function |
|------|---------------|
| `Nat` | `Hash.hash(n)` |
| `Text` | `Text.hash(t)` |
| `Blob` | `Blob.hash(b)` |
| `Principal` | `Principal.hash(p)` |
| `Int` | `Int.hash(i)` (returns Nat32) |

---

## Cycles Management

```motoko
import Cycles "mo:base/ExperimentalCycles";

actor {
  public func availableCycles() : async Nat {
    Cycles.balance()
  };

  // Accept cycles sent to this canister
  public func deposit() : async Nat {
    Cycles.accept<system>(Cycles.available())
  };

  // Send cycles when calling another canister
  public func callWithCycles(target : Principal) : async () {
    let remote = actor(Principal.toText(target)) : actor {
      deposit : () -> async Nat;
    };
    Cycles.add<system>(1_000_000);  // Attach 1M cycles
    ignore await remote.deposit();
  };
}
```

---

## HTTP Outcalls (Experimental)

```motoko
import Blob "mo:base/Blob";
import Cycles "mo:base/ExperimentalCycles";
import Text "mo:base/Text";

actor {
  // Requires cycles and is subject to rate limiting
  public func httpGet(url : Text) : async Text {
    let ic : actor {
      http_request : {
        url : Text;
        max_response_bytes : ?Nat64;
        method : { #get };
        headers : [{ name : Text; value : Text }];
        body : ?Blob;
        transform : ?{ function : shared query ({ response : { status : Nat; headers : [{ name : Text; value : Text }]; body : Blob }; context : Blob }) -> async { status : Nat; headers : [{ name : Text; value : Text }]; body : Blob }; context : Blob };
      } -> async {
        status : Nat;
        headers : [{ name : Text; value : Text }];
        body : Blob;
      };
    } = actor("aaaaa-aa");

    Cycles.add<system>(230_850_258_000);

    let response = await ic.http_request({
      url = url;
      max_response_bytes = ?10_000;
      method = #get;
      headers = [];
      body = null;
      transform = null;
    });

    switch (Text.decodeUtf8(response.body)) {
      case null { "Failed to decode response" };
      case (?text) { text };
    }
  };
}
```

---

## Testing Patterns

### Assert-Based Testing

```motoko
import Debug "mo:base/Debug";

actor {
  public func runTests() : async () {
    // Test 1
    let result = 2 + 2;
    assert(result == 4);

    // Test 2
    let text = "hello" # " " # "world";
    assert(text == "hello world");

    Debug.print("All tests passed!");
  };
}
```

### Test Module Pattern

```motoko
// tests.mo
module {
  public func testAddition() : Bool {
    2 + 2 == 4
  };

  public func testConcat() : Bool {
    "a" # "b" == "ab"
  };

  public func runAll() : Bool {
    testAddition() and testConcat()
  };
}
```

---

## State Machine Pattern

Use variants to model explicit state machines. The compiler ensures all states are handled:

```motoko
import Time "mo:base/Time";
import Result "mo:base/Result";

persistent actor OrderProcessor {
  public type OrderState = {
    #pending : { createdAt : Int };
    #processing : { startedAt : Int };
    #shipped : { shippedAt : Int; trackingId : Text };
    #delivered : { deliveredAt : Int };
    #cancelled : { reason : Text };
  };

  public type Order = {
    id : Nat;
    var state : OrderState;
  };

  var orders : [var Order] = [var];

  // State transition functions
  public func startProcessing(orderId : Nat) : async Result.Result<(), Text> {
    let ?order = findOrder(orderId) else return #err("Order not found");

    switch (order.state) {
      case (#pending(_)) {
        order.state := #processing({ startedAt = Time.now() });
        #ok()
      };
      case (#processing(_)) { #err("Already processing") };
      case (#shipped(_)) { #err("Already shipped") };
      case (#delivered(_)) { #err("Already delivered") };
      case (#cancelled(_)) { #err("Order was cancelled") };
    }
  };

  public func ship(orderId : Nat, trackingId : Text) : async Result.Result<(), Text> {
    let ?order = findOrder(orderId) else return #err("Order not found");

    switch (order.state) {
      case (#processing(_)) {
        order.state := #shipped({
          shippedAt = Time.now();
          trackingId;
        });
        #ok()
      };
      case (#pending(_)) { #err("Not yet processing") };
      case (_) { #err("Invalid state for shipping") };
    }
  };

  // Query current state
  public query func getState(orderId : Nat) : async ?OrderState {
    switch (findOrder(orderId)) {
      case (?order) { ?order.state };
      case null { null };
    }
  };

  func findOrder(id : Nat) : ?Order {
    for (order in orders.vals()) {
      if (order.id == id) return ?order;
    };
    null
  };
}
```

**Benefits of this pattern:**
- Compiler catches missing state transitions
- States carry their own data (e.g., timestamps)
- Invalid transitions return explicit errors
- Easy to add new states

---

## Pagination Pattern

Pagination is essential for any canister that stores lists of items.

### Cursor-Based Pagination

```motoko
import Array "mo:base/Array";
import Iter "mo:base/Iter";
import Order "mo:base/Order";

persistent actor {
  public type Item = { id : Nat; name : Text; createdAt : Int };

  var items : [Item] = [];

  // Cursor is the last item ID seen (exclusive)
  // Returns items with id > cursor, limited by pageSize
  public query func listItems(cursor : ?Nat, pageSize : Nat) : async {
    items : [Item];
    nextCursor : ?Nat;
  } {
    // Find start position
    let startIdx = switch (cursor) {
      case null { 0 };
      case (?lastId) {
        var idx = 0;
        label search for (item in items.vals()) {
          if (item.id == lastId) { break search };
          idx += 1;
        };
        idx + 1  // Start after the cursor item
      };
    };

    // Slice the page
    let pageItems = if (startIdx >= items.size()) {
      []
    } else {
      let endIdx = Nat.min(startIdx + pageSize, items.size());
      Array.subArray(items, startIdx, endIdx - startIdx)
    };

    // Next cursor is the last item's ID (if there are more items)
    let nextCursor = if (startIdx + pageSize < items.size()) {
      ?pageItems[pageItems.size() - 1].id
    } else {
      null  // No more pages
    };

    { items = pageItems; nextCursor }
  };
}
```

### Offset-Based Pagination (Simpler but Less Stable)

```motoko
public query func listItemsOffset(offset : Nat, limit : Nat) : async {
  items : [Item];
  total : Nat;
  hasMore : Bool;
} {
  let total = items.size();
  let pageItems = if (offset >= total) {
    []
  } else {
    let endIdx = Nat.min(offset + limit, total);
    Array.subArray(items, offset, endIdx - offset)
  };

  { items = pageItems; total; hasMore = offset + limit < total }
};
```

**When to use each:**

| Approach | Pros | Cons |
|----------|------|------|
| Cursor-based | Stable across insertions/deletions | Harder to "jump to page 5" |
| Offset-based | Simple, easy page jumps | Breaks if items added/removed during pagination |

---

## Retry Pattern for Inter-Canister Calls

Inter-canister calls can fail transiently. Use retry with exponential backoff for reliability.

### Basic Retry with Backoff

```motoko
import Error "mo:base/Error";
import Timer "mo:base/Timer";
import Result "mo:base/Result";

actor {
  type RetryConfig = {
    maxAttempts : Nat;
    initialDelayNs : Nat;  // Nanoseconds
    maxDelayNs : Nat;
    backoffMultiplier : Nat;  // e.g., 2 for exponential
  };

  let defaultConfig : RetryConfig = {
    maxAttempts = 3;
    initialDelayNs = 1_000_000_000;  // 1 second
    maxDelayNs = 30_000_000_000;     // 30 seconds
    backoffMultiplier = 2;
  };

  // Retry an async operation with exponential backoff
  func retry<T>(
    config : RetryConfig,
    operation : () -> async Result.Result<T, Text>
  ) : async* Result.Result<T, Text> {
    var attempt = 0;
    var delay = config.initialDelayNs;

    loop {
      attempt += 1;

      try {
        let result = await operation();
        switch (result) {
          case (#ok(value)) { return #ok(value) };
          case (#err(e)) {
            if (attempt >= config.maxAttempts) {
              return #err("Max retries reached: " # e);
            };
            // Fall through to retry
          };
        };
      } catch (e) {
        if (attempt >= config.maxAttempts) {
          return #err("Max retries reached: " # Error.message(e));
        };
      };

      // Wait before retrying (using timer for non-blocking delay)
      // Note: In practice, you'd schedule a callback rather than blocking
      delay := Nat.min(delay * config.backoffMultiplier, config.maxDelayNs);
    };
  };

  // Usage example
  public func callExternalWithRetry(target : Principal) : async Result.Result<Text, Text> {
    let remote = actor(Principal.toText(target)) : actor {
      getData : () -> async Text;
    };

    await* retry<Text>(defaultConfig, func() : async Result.Result<Text, Text> {
      try {
        #ok(await remote.getData())
      } catch (e) {
        #err(Error.message(e))
      }
    })
  };
}
```

### Scheduled Retry Pattern

For operations that should retry in the background:

```motoko
import Timer "mo:base/Timer";
import Buffer "mo:base/Buffer";

actor {
  type PendingTask = {
    id : Nat;
    target : Principal;
    data : Text;
    attempts : Nat;
    nextRetryNs : Int;
  };

  stable var pendingTasks : [PendingTask] = [];
  var taskBuffer = Buffer.fromArray<PendingTask>(pendingTasks);
  stable var nextTaskId : Nat = 0;

  let MAX_ATTEMPTS = 5;
  let BASE_DELAY_NS = 5_000_000_000;  // 5 seconds

  // Schedule a task for execution
  public func scheduleTask(target : Principal, data : Text) : async Nat {
    let task : PendingTask = {
      id = nextTaskId;
      target;
      data;
      attempts = 0;
      nextRetryNs = Time.now();
    };
    nextTaskId += 1;
    taskBuffer.add(task);
    task.id
  };

  // Process pending tasks (called by timer)
  func processPendingTasks() : async () {
    let now = Time.now();
    let remaining = Buffer.Buffer<PendingTask>(0);

    for (task in taskBuffer.vals()) {
      if (task.nextRetryNs > now) {
        remaining.add(task);  // Not ready yet
      } else {
        // Try to execute
        let success = await tryExecuteTask(task);
        if (not success and task.attempts + 1 < MAX_ATTEMPTS) {
          // Schedule retry with exponential backoff
          let delay = BASE_DELAY_NS * (2 ** task.attempts);
          remaining.add({
            task with
            attempts = task.attempts + 1;
            nextRetryNs = now + delay;
          });
        };
        // If success or max attempts reached, task is dropped
      };
    };

    taskBuffer := remaining;
  };

  func tryExecuteTask(task : PendingTask) : async Bool {
    try {
      let remote = actor(Principal.toText(task.target)) : actor {
        process : (Text) -> async ();
      };
      await remote.process(task.data);
      true
    } catch (e) {
      false
    }
  };

  // Timer to process tasks every 10 seconds
  ignore Timer.recurringTimer<system>(#seconds 10, processPendingTasks);

  system func preupgrade() {
    pendingTasks := Buffer.toArray(taskBuffer);
  };

  system func postupgrade() {
    taskBuffer := Buffer.fromArray(pendingTasks);
  };
}
```

**Retry Best Practices:**

| Practice | Rationale |
|----------|-----------|
| Use exponential backoff | Avoid thundering herd, give system time to recover |
| Cap maximum delay | Don't wait forever |
| Limit max attempts | Fail fast if permanently broken |
| Make operations idempotent | Safe to retry without side effects |
| Log failures | Debug transient vs permanent failures |

---

## Common Gotchas

### Mutable vs Immutable

```motoko
// WRONG: Can't modify let-bound variable
let x = 5;
x := 6;  // Error!

// RIGHT: Use var for mutable
var x = 5;
x := 6;  // OK
```

### Array Subtyping

```motoko
// WRONG: Mutable arrays are NOT subtypes of immutable
let mutable : [var Nat] = [var 1, 2, 3];
let immutable : [Nat] = mutable;  // Error!

// RIGHT: Convert explicitly
let immutable : [Nat] = Array.freeze(mutable);
```

### Async Context Required

```motoko
// WRONG: Can't throw outside async context
func sync() { throw Error.reject("nope") };  // Error!

// RIGHT: Must be in async function
public func async_() : async () {
  throw Error.reject("nope");
};
```

### Stable Types Limitations

Only first-order types can be stable:
- `Nat`, `Int`, `Bool`, `Text`, `Blob`, `Principal`
- `?T`, `[T]`, `(T1, T2, ...)`, `{field: T}`
- Variants

NOT stable:
- `HashMap`, `Buffer` (use pre/postupgrade hooks)
- Functions
- Actors

---

## Actor Class Instantiation

Create new canisters programmatically from Motoko code.

### Define an Actor Class

```motoko
// Bucket.mo
import Cycles "mo:base/ExperimentalCycles";

actor class Bucket(owner : Principal) = self {
  stable var data : [Text] = [];

  public shared(msg) func add(item : Text) : async () {
    assert(msg.caller == owner);
    data := Array.append(data, [item]);
  };

  public query func getAll() : async [Text] { data };

  public func getCanisterId() : async Principal {
    Principal.fromActor(self)
  };
}
```

### Spawn New Canisters

```motoko
// Main.mo
import Bucket "Bucket";
import Cycles "mo:base/ExperimentalCycles";
import Principal "mo:base/Principal";

actor Main {
  stable var buckets : [Principal] = [];

  public func createBucket() : async Principal {
    // Attach cycles for new canister (required!)
    Cycles.add<system>(1_000_000_000_000);  // 1T cycles

    // Create new canister with actor class
    let newBucket = await Bucket.Bucket(Principal.fromActor(Main));
    let bucketId = await newBucket.getCanisterId();

    buckets := Array.append(buckets, [bucketId]);
    bucketId
  };

  public query func listBuckets() : async [Principal] { buckets };
}
```

### dfx.json for Actor Classes

```json
{
  "canisters": {
    "main": {
      "type": "motoko",
      "main": "src/main/Main.mo"
    },
    "bucket": {
      "type": "motoko",
      "main": "src/bucket/Bucket.mo"
    }
  }
}
```

### Actor Class Considerations

| Aspect | Details |
|--------|---------|
| Cycles | Must attach cycles to create canister |
| Controllers | New canister is controlled by creating canister by default |
| Upgrades | Actor classes can be upgraded independently |
| Limits | Subnet has canister count limits |

---

## Cycles Management

Monitor and manage canister cycles.

### Check Cycle Balance

```motoko
import Cycles "mo:base/ExperimentalCycles";

actor {
  public query func balance() : async Nat {
    Cycles.balance()
  };

  public func balanceWithWarning() : async { balance : Nat; warning : ?Text } {
    let bal = Cycles.balance();
    let warning = if (bal < 1_000_000_000_000) {  // < 1T
      ?"Low cycles warning!"
    } else { null };
    { balance = bal; warning }
  };
}
```

### Accept Incoming Cycles

```motoko
actor {
  // Accept cycles sent with a call
  public func deposit() : async Nat {
    let available = Cycles.available();
    let accepted = Cycles.accept<system>(available);
    accepted
  };

  // Accept with limit
  public func depositWithLimit(max : Nat) : async Nat {
    let available = Cycles.available();
    let toAccept = if (available > max) { max } else { available };
    Cycles.accept<system>(toAccept)
  };
}
```

### Send Cycles with Calls

```motoko
actor {
  public func transferCycles(target : Principal, amount : Nat) : async () {
    let wallet = actor(Principal.toText(target)) : actor {
      deposit : () -> async Nat;
    };

    Cycles.add<system>(amount);
    ignore await wallet.deposit();
  };
}
```

### Cycles Reserve Pattern

```motoko
actor {
  let RESERVE : Nat = 100_000_000_000;  // 100B cycles reserve

  public func availableForWork() : async Nat {
    let bal = Cycles.balance();
    if (bal > RESERVE) { bal - RESERVE } else { 0 }
  };

  public func doExpensiveWork() : async Result<(), Text> {
    if (Cycles.balance() < RESERVE + 10_000_000_000) {
      return #err("Insufficient cycles for operation");
    };
    // ... do work
    #ok()
  };
}
```

### Low Cycles Alert (Timer-based)

```motoko
import Timer "mo:base/Timer";
import Debug "mo:base/Debug";

actor {
  let THRESHOLD : Nat = 500_000_000_000;  // 500B

  ignore Timer.recurringTimer<system>(#seconds 3600, func() : async () {
    if (Cycles.balance() < THRESHOLD) {
      Debug.print("WARNING: Low cycles! Balance: " # Nat.toText(Cycles.balance()));
      // Could also call an external monitoring service
    };
  });
}
```

---

## Tooling

### VS Code Motoko Extension

Install from the VS Marketplace: search for "Motoko" by DFINITY Foundation.

**Key Features:**

| Feature | Shortcut | Description |
|---------|----------|-------------|
| Format code | Shift+Alt+F | Auto-format Motoko files |
| Go to definition | F12 | Jump to function/type definition |
| Autocompletion | Ctrl+Space | IntelliSense for types and functions |
| Quick fix imports | Ctrl+. | Add missing imports |
| Organize imports | Shift+Alt+O | Sort and clean imports |
| Hover info | Hover | Show type signatures and docs |

**Code Snippets:**

Type these prefixes and press Tab:
- `actor` - Actor template
- `func` - Function template
- `array-2-buffer` - Array to Buffer conversion
- `principal-2-text` - Principal to Text conversion

**Configuration in settings.json:**

```json
{
  "motoko.dfx": "/usr/local/bin/dfx",
  "motoko.formatter": "prettier"
}
```

### Motoko Compiler (moc) Flags

Configure in `dfx.json` under `args`:

```json
{
  "canisters": {
    "my_canister": {
      "type": "motoko",
      "main": "src/main.mo",
      "args": "--incremental-gc --force-gc"
    }
  }
}
```

**Common Flags:**

| Flag | Description |
|------|-------------|
| `--incremental-gc` | Use incremental garbage collector (recommended for large heaps) |
| `--force-gc` | Force GC after each message |
| `--max-stable-pages N` | Limit stable memory pages |
| `--experimental-stable-memory N` | Set stable memory mode (0, 1, or 2) |
| `--sanity-checks` | Enable runtime sanity checks (debug only) |
| `--debug` | Include debug info in Wasm |
| `--release` | Optimize for release (omit debug info) |

### candid-extractor

Extract Candid interface from compiled Wasm:

```bash
# Install
cargo install candid-extractor

# Extract interface
candid-extractor target/wasm32-unknown-unknown/release/my_canister.wasm > my_canister.did
```

For Motoko, dfx generates the `.did` file automatically during build.

---

## Deduplication Patterns

Handle duplicate messages safely (idempotency).

### Request ID Pattern

```motoko
import HashMap "mo:base/HashMap";
import Time "mo:base/Time";

actor {
  type RequestId = Nat;

  // Track processed requests with timestamps
  var processed = HashMap.HashMap<RequestId, Int>(100, Nat.equal, Hash.hash);

  public shared func processOnce(requestId : RequestId, data : Text) : async Result<Text, Text> {
    // Already processed?
    switch (processed.get(requestId)) {
      case (?_) { return #err("Duplicate request") };
      case null {};
    };

    // Mark as processing (before any await!)
    processed.put(requestId, Time.now());

    // Do the actual work
    let result = await doWork(data);

    #ok(result)
  };

  // Cleanup old requests periodically
  public func cleanupOldRequests() : async Nat {
    let oneHour = 3_600_000_000_000;
    let cutoff = Time.now() - oneHour;
    var removed = 0;

    for ((id, timestamp) in processed.entries()) {
      if (timestamp < cutoff) {
        processed.delete(id);
        removed += 1;
      };
    };
    removed
  };
}
```

### Nonce-Based Deduplication

```motoko
actor {
  // Per-user nonces (must be strictly increasing)
  stable var nonces : [(Principal, Nat)] = [];
  var nonceMap = HashMap.fromIter<Principal, Nat>(nonces.vals(), 100, Principal.equal, Principal.hash);

  public shared(msg) func action(nonce : Nat, data : Text) : async Result<(), Text> {
    let caller = msg.caller;
    let lastNonce = Option.get(nonceMap.get(caller), 0);

    if (nonce <= lastNonce) {
      return #err("Nonce too low - possible replay");
    };

    // Update nonce BEFORE processing
    nonceMap.put(caller, nonce);

    // Process
    await doAction(data);
    #ok()
  };

  system func preupgrade() {
    nonces := Iter.toArray(nonceMap.entries());
  };

  system func postupgrade() {
    nonceMap := HashMap.fromIter(nonces.vals(), 100, Principal.equal, Principal.hash);
  };
}
```

---

## HTTP Request Handling

Canisters can serve HTTP requests directly using the `http_request` interface.

### Basic HTTP Handler

```motoko
import Text "mo:base/Text";
import Blob "mo:base/Blob";

actor {
  public type HttpRequest = {
    url : Text;
    method : Text;
    body : Blob;
    headers : [(Text, Text)];
  };

  public type HttpResponse = {
    status_code : Nat16;
    headers : [(Text, Text)];
    body : Blob;
  };

  public query func http_request(req : HttpRequest) : async HttpResponse {
    if (req.url == "/health") {
      return {
        status_code = 200;
        headers = [("content-type", "application/json")];
        body = Text.encodeUtf8("{\"status\": \"ok\"}");
      };
    };

    {
      status_code = 404;
      headers = [];
      body = Text.encodeUtf8("Not Found");
    }
  };
}
```

### HTTP Packages (mops)

```bash
mops add http-types        # Standard HTTP types
mops add http-parser       # URL and request parsing
mops add server            # Express-like framework
mops add certified-http    # Certified responses
```

```motoko
// Using the server package
import Server "mo:server";

persistent actor {
  transient let server = Server.Server();

  server.get("/api/users", func(req, res) {
    res.json({ users = ["Alice", "Bob"] });
  });

  public query func http_request(req : Server.HttpRequest) : async Server.HttpResponse {
    server.http_request(req)
  };
}
```

---

## Cryptography Packages

Common cryptography packages from mops:

```bash
mops add sha2              # SHA-256, SHA-512
mops add sha3              # SHA-3, Keccak
mops add ed25519           # Ed25519 signatures
mops add ic-certification  # Canister signatures
```

```motoko
import SHA256 "mo:sha2/Sha256";
import Blob "mo:base/Blob";

actor {
  public func hashData(data : Blob) : async Blob {
    let hash = SHA256.fromBlob(#sha256, data);
    Blob.fromArray(SHA256.toArray(hash))
  };
}
```

---

## Encoding and Serialization

```bash
mops add serde    # JSON/CBOR serialization
mops add candid   # Candid encoding
mops add cbor     # CBOR format
```

```motoko
import JSON "mo:serde/JSON";

actor {
  public type User = { name : Text; age : Nat };

  public func toJson(user : User) : async Text {
    JSON.toText(#Object([
      ("name", #String(user.name)),
      ("age", #Number(user.age))
    ]))
  };
}
```

---

## Utility Packages

Common utility packages from mops:

| Package | Purpose |
|---------|---------|
| [`datetime`](https://mops.one/datetime) | Date/time parsing and formatting |
| [`uuid`](https://mops.one/uuid) | UUID generation |
| [`itertools`](https://mops.one/itertools) | Iterator utilities |
| [`time-consts`](https://mops.one/time-consts) | Time constants (SECOND, MINUTE, etc.) |
| [`bench`](https://mops.one/bench) | Benchmarking |

```motoko
import DateTime "mo:datetime/DateTime";

actor {
  public func formatTimestamp(nanos : Int) : async Text {
    DateTime.fromTime(nanos).toText()
  };
}


---

# Idiomatic Motoko Style Guide

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions | camelCase | `getUserById`, `processPayment` |
| Variables | camelCase | `userCount`, `isActive` |
| Types | PascalCase | `UserId`, `PaymentResult` |
| Modules | PascalCase | `import Utils "./utils"` |
| Variant tags | camelCase with `#` | `#ok`, `#notFound`, `#invalidInput` |
| Constants | camelCase (no special convention) | `maxRetries`, `defaultTimeout` |

```motoko
// Good
public type UserProfile = { id : Nat; displayName : Text };
public func getUserProfile(userId : Nat) : async ?UserProfile { ... };

// Avoid
public type user_profile = { ID : Nat; DisplayName : Text };
public func get_user_profile(user_id : Nat) : async ?user_profile { ... };
```

---

## Functional Patterns

Motoko has a functional flavor. Prefer combinators over imperative loops when processing collections.

### Iterator Combinators

```motoko
import Iter "mo:base/Iter";
import Array "mo:base/Array";

// Idiomatic: use Iter combinators
let numbers = [1, 2, 3, 4, 5];
let doubled = Iter.toArray(Iter.map(numbers.vals(), func(n : Nat) : Nat { n * 2 }));
let evens = Iter.toArray(Iter.filter(numbers.vals(), func(n : Nat) : Bool { n % 2 == 0 }));

// Less idiomatic: imperative loop
let buf = Buffer.Buffer<Nat>(0);
for (n in numbers.vals()) {
  if (n % 2 == 0) { buf.add(n) };
};
let evens = Buffer.toArray(buf);
```

### Array Combinators

```motoko
import Array "mo:base/Array";

let users = [{ name = "Alice"; age = 30 }, { name = "Bob"; age = 25 }];

// Map: transform each element
let names = Array.map<User, Text>(users, func(u) { u.name });

// Filter: keep matching elements
let adults = Array.filter<User>(users, func(u) { u.age >= 18 });

// Find: get first match
let bob = Array.find<User>(users, func(u) { u.name == "Bob" });

// Fold: reduce to single value
let totalAge = Array.foldLeft<User, Nat>(users, 0, func(acc, u) { acc + u.age });
```

### Option Combinators

```motoko
import Option "mo:base/Option";

let maybeUser : ?User = findUser(id);

// Idiomatic: chain operations on Options
let maybeName : ?Text = Option.map(maybeUser, func(u : User) : Text { u.name });
let maybeUpper : ?Text = Option.chain(maybeName, func(n : Text) : ?Text {
  if (n.size() > 0) { ?Text.toUppercase(n) } else { null }
});

// Get with default
let name = Option.get(maybeName, "Anonymous");

// Check if Some
if (Option.isSome(maybeUser)) { ... };
```

### Result Combinators

```motoko
import Result "mo:base/Result";

type MyResult = Result.Result<User, Error>;

// Map success value
let nameResult = Result.mapOk<User, Text, Error>(userResult, func(u) { u.name });

// Map error value
let mapped = Result.mapErr<User, OldError, NewError>(result, convertError);

// Chain results
let chainedResult = Result.chain<User, Profile, Error>(userResult, getProfile);
```

---

## Module Organization

### Typical Project Structure

```
my_canister/
├── dfx.json
└── src/
    └── my_canister/
        ├── main.mo          # Actor definition, public API
        ├── types.mo         # Shared type definitions
        ├── utils.mo         # Helper functions
        ├── state.mo         # State management (optional)
        └── lib/             # Sub-modules (for larger projects)
            ├── auth.mo
            └── storage.mo
```

### Type Module Pattern

Centralize shared types in `types.mo`:

```motoko
// types.mo
module {
  public type UserId = Nat;
  public type User = {
    id : UserId;
    name : Text;
    email : ?Text;
    createdAt : Int;
  };

  public type Error = {
    #notFound;
    #unauthorized;
    #invalidInput : Text;
  };

  public type UserResult = Result.Result<User, Error>;
}
```

```motoko
// main.mo
import Types "./types";

actor {
  public func getUser(id : Types.UserId) : async Types.UserResult { ... };
}
```

### Utils Module Pattern

```motoko
// utils.mo
import Time "mo:base/Time";
import Int "mo:base/Int";

module {
  public func nowSeconds() : Int {
    Time.now() / 1_000_000_000
  };

  public func validateEmail(email : Text) : Bool {
    Text.contains(email, #char '@')
  };
}
```

---

## Documentation Conventions

Use `///` for doc comments (triple slash):

```motoko
/// A user in the system.
///
/// Users are identified by their unique ID and can have
/// an optional email address for notifications.
public type User = {
  /// Unique identifier, assigned on creation
  id : Nat;
  /// Display name (1-100 characters)
  name : Text;
  /// Optional email for notifications
  email : ?Text;
};

/// Retrieves a user by their ID.
///
/// Returns `null` if no user exists with the given ID.
/// This is a query call and does not modify state.
public query func getUser(id : Nat) : async ?User {
  users.get(id)
};
```

### What to Document

| Element | Document? | What to include |
|---------|-----------|-----------------|
| Public types | Yes | Purpose, field meanings, constraints |
| Public functions | Yes | What it does, parameters, return value, errors |
| Private functions | If complex | Intent, non-obvious behavior |
| Modules | Yes (at top) | Module purpose, usage example |

---

## Common Idioms

### Early Return with let-else

```motoko
// Idiomatic: use let-else for early return on null
public func processUser(id : Nat) : async Result<Text, Error> {
  let ?user = users.get(id) else return #err(#notFound);
  let ?email = user.email else return #err(#noEmail);
  // continue with user and email
  #ok("Processed " # email)
};
```

### Option Blocks with `do ?`

The `do ?` block provides clean option chaining - the entire block returns `null` if any `!` unwrap fails:

```motoko
// Idiomatic: do ? for clean option chaining
func getActiveUserEmail(id : Nat) : ?Text {
  do ? {
    let user = users.get(id)!;      // Unwrap, exit with null if none
    let profile = user.profile!;     // Chain continues
    if (not profile.active) return null;  // Explicit null return
    profile.email!                   // Final unwrap
  }
};

// Equivalent verbose version (avoid)
func getActiveUserEmailVerbose(id : Nat) : ?Text {
  switch (users.get(id)) {
    case null { null };
    case (?user) {
      switch (user.profile) {
        case null { null };
        case (?profile) {
          if (not profile.active) { null }
          else { profile.email }
        };
      };
    };
  }
};
```

Use `do ?` when:
- Chaining multiple nullable operations
- Transforming nested options
- Building optional values with multiple conditions

### Record Punning (Field Shorthand)

When a variable name matches the field name, use shorthand:

```motoko
// Idiomatic: field punning
func createUser(name : Text, email : Text, age : Nat) : User {
  { name; email; age; createdAt = Time.now() }  // name = name, email = email, age = age
};

// Verbose (avoid when variable names match)
func createUserVerbose(name : Text, email : Text, age : Nat) : User {
  { name = name; email = email; age = age; createdAt = Time.now() }
};

// Punning in function parameters
func formatUser({ name; email } : User) : Text {
  name # " <" # email # ">"
};
```

### Labeled Expressions and Break

Use labeled expressions for complex control flow with early exit:

```motoko
// Labeled block with break - returns a value
func findFirstMatch(items : [Item], pred : Item -> Bool) : ?Item {
  label result : ?Item {
    for (item in items.vals()) {
      if (pred(item)) {
        break result (?item);  // Exit block with value
      };
    };
    null  // Default if no break
  }
};

// Labeled loop for nested break
func findInMatrix(matrix : [[Nat]], target : Nat) : ?(Nat, Nat) {
  label search : ?(Nat, Nat) {
    var row = 0;
    for (rowData in matrix.vals()) {
      var col = 0;
      for (val in rowData.vals()) {
        if (val == target) {
          break search (?(row, col));
        };
        col += 1;
      };
      row += 1;
    };
    null
  }
};
```

Use labeled expressions when:
- Breaking out of nested loops
- Returning early from a block with a computed value
- Implementing search with early termination

### Record Update with `and`

Create a modified copy of a record, changing only specific fields:

```motoko
type Config = { host : Text; port : Nat; timeout : Nat; debug : Bool };

let defaultConfig : Config = { host = "localhost"; port = 8080; timeout = 30; debug = false };

// Idiomatic: spread base record, override specific fields
let prodConfig : Config = { defaultConfig and host = "api.example.com"; debug = false };
let devConfig : Config = { defaultConfig and debug = true; timeout = 60 };

// Works with function parameters
func withTimeout(config : Config, t : Nat) : Config {
  { config and timeout = t }
};
```

### Builder Pattern for Complex Types

```motoko
public func createUser(
  name : Text,
  email : ?Text,
  role : ?Role,
) : User {
  {
    id = nextId();
    name;
    email;
    role = Option.get(role, #user);
    createdAt = Time.now();
  }
};
```

### Ignore Pattern in Switch

Use `_` to match and discard values you don't need:

```motoko
// Ignore specific fields
func getUserName(user : { name : Text; age : Nat; email : ?Text }) : Text {
  let { name; _ } = user;  // Extract name, ignore rest
  name
};

// Ignore variant payloads
func isError<T, E>(result : Result.Result<T, E>) : Bool {
  switch result {
    case (#ok(_)) false;   // Ignore success value
    case (#err(_)) true;   // Ignore error value
  }
};

// Ignore tuple elements
let (first, _, third) = (1, 2, 3);  // Ignore middle element
```

### Consistent Error Types

Define a single error type per module/actor:

```motoko
public type Error = {
  #notFound : { id : Nat };
  #unauthorized : { caller : Principal; required : Role };
  #invalidInput : { field : Text; reason : Text };
  #internal : Text;
};

// Usage gives rich error context
#err(#invalidInput({ field = "email"; reason = "must contain @" }))
```

### Loop with Index

Motoko's `for` doesn't provide an index directly. Use these patterns:

```motoko
import Iter "mo:base/Iter";
import Array "mo:base/Array";

// Pattern 1: Manual counter
var idx = 0;
for (item in items.vals()) {
  Debug.print(Nat.toText(idx) # ": " # item);
  idx += 1;
};

// Pattern 2: Enumerate with Array.mapEntries
let indexed = Array.mapEntries<Text, (Nat, Text)>(items, func(item, i) { (i, item) });

// Pattern 3: Iter.range for index-based iteration
for (i in Iter.range(0, items.size() - 1)) {
  let item = items[i];
  // ...
};
```

### Async in Loops

Handle async calls in loops carefully due to commit points:

```motoko
// Sequential async (safe, but slow)
for (id in ids.vals()) {
  let result = await processItem(id);  // Each await is a commit point
  results.add(result);
};

// Parallel async (faster, but complex error handling)
let futures = Array.map<Nat, async Result<(), Error>>(ids, func(id) {
  processItem(id)  // Start all at once
});
var errors = Buffer.Buffer<Error>(0);
for (future in futures.vals()) {
  switch (await future) {
    case (#err(e)) { errors.add(e) };
    case (#ok) {};
  };
};
```

### Type Aliases for Readability

Use type aliases to make complex types more readable:

```motoko
// Without aliases - hard to read
public func process(data : [(Principal, { balance : Nat; lastUpdate : Int })]) : async Result.Result<[{ id : Principal; change : Int }], { #notFound; #unauthorized }> { ... };

// With aliases - self-documenting
public type UserId = Principal;
public type UserBalance = { balance : Nat; lastUpdate : Int };
public type BalanceChange = { id : UserId; change : Int };
public type UpdateError = { #notFound; #unauthorized };

public func process(data : [(UserId, UserBalance)]) : async Result.Result<[BalanceChange], UpdateError> { ... };
```

### Variant Exhaustiveness

Always handle all variant cases explicitly - let the compiler catch missing cases:

```motoko
type Status = { #pending; #active; #completed; #failed : Text };

// Good: exhaustive match - compiler warns if you add a new variant
func describe(s : Status) : Text {
  switch (s) {
    case (#pending) "Waiting";
    case (#active) "In progress";
    case (#completed) "Done";
    case (#failed(reason)) "Failed: " # reason;
  }
};

// Avoid: catch-all hides missing cases
func describeBad(s : Status) : Text {
  switch (s) {
    case (#pending) "Waiting";
    case (_) "Other";  // Bad - won't catch new variants
  }
};
```

---

## Authorization Patterns

### Caller Validation Module

Extract common authorization checks into a reusable module:

```motoko
// auth.mo
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Array "mo:base/Array";

module {
  public type AuthError = {
    #anonymous;
    #unauthorized;
    #notController;
  };

  public func requireNotAnonymous(caller : Principal) : Result.Result<(), AuthError> {
    if (Principal.isAnonymous(caller)) { #err(#anonymous) }
    else { #ok() }
  };

  public func requirePrincipal(caller : Principal, allowed : Principal) : Result.Result<(), AuthError> {
    if (caller == allowed) { #ok() }
    else { #err(#unauthorized) }
  };

  public func requireOneOf(caller : Principal, allowed : [Principal]) : Result.Result<(), AuthError> {
    for (p in allowed.vals()) {
      if (caller == p) return #ok();
    };
    #err(#unauthorized)
  };

  // For use with actor classes where controller is stored
  public func requireController(caller : Principal, controllers : [Principal]) : Result.Result<(), AuthError> {
    for (c in controllers.vals()) {
      if (caller == c) return #ok();
    };
    #err(#notController)
  };
}
```

### Using Authorization in Actors

```motoko
import Auth "./auth";
import Result "mo:base/Result";

shared(msg) actor class SecureActor() {
  let deployer = msg.caller;
  stable var admins : [Principal] = [deployer];

  // Pattern: Early return on auth failure
  public shared(msg) func adminAction() : async Result.Result<Text, Auth.AuthError> {
    switch (Auth.requireOneOf(msg.caller, admins)) {
      case (#err(e)) { return #err(e) };
      case (#ok()) {};
    };
    // ... admin logic
    #ok("Admin action completed")
  };

  // Pattern: Using let-else for concise auth
  public shared(msg) func anotherAdminAction() : async Result.Result<Text, Auth.AuthError> {
    let #ok() = Auth.requireOneOf(msg.caller, admins) else return #err(#unauthorized);
    // ... proceed with action
    #ok("Done")
  };

  // Pattern: Assert for internal invariants (traps on failure)
  public shared(msg) func deployerOnly() : async () {
    assert(msg.caller == deployer);  // Traps if not deployer
    // ... sensitive logic
  };
}
```

### When to Use Each Pattern

| Pattern | Use When |
|---------|----------|
| `Result` return | Caller should handle auth errors gracefully |
| `assert` | Internal invariant, failure is a bug |
| `switch` | Need to perform cleanup or logging on auth failure |
| `let-else` | Concise early return, no special handling needed |

---

## Anti-Patterns to Avoid

### Overusing Exceptions

```motoko
// Avoid: exceptions for expected cases
public func getUser(id : Nat) : async User {
  switch (users.get(id)) {
    case null { throw Error.reject("not found") };  // Bad
    case (?u) { u };
  }
};

// Prefer: Result for expected errors
public func getUser(id : Nat) : async Result<User, Error> {
  switch (users.get(id)) {
    case null { #err(#notFound) };  // Good
    case (?u) { #ok(u) };
  }
};
```

### Ignoring Return Values Silently

```motoko
// Bad: silently ignore potential errors
ignore await riskyOperation();

// Better: handle or explicitly acknowledge
let _ = await riskyOperation();  // Intentionally unused

// Best: actually handle the result
switch (await riskyOperation()) {
  case (#err(e)) { Debug.print("Failed: " # debug_show(e)) };
  case (#ok(_)) {};
};
```

### Mutable State Where Immutable Works

```motoko
// Avoid: unnecessary mutability
var total = 0;
for (n in numbers.vals()) { total += n };

// Prefer: functional approach
let total = Array.foldLeft<Nat, Nat>(numbers, 0, func(a, b) { a + b });
```

### Magic Numbers

```motoko
// Avoid
if (arg.size() > 1048576) { return false };

// Prefer
let MAX_PAYLOAD_BYTES = 1_048_576;  // 1 MB
if (arg.size() > MAX_PAYLOAD_BYTES) { return false };
```

### Unnecessary async Overhead

```motoko
// Avoid: async wrapper adds message overhead
func maybeLog(msg : Text) : async () {
  if (logging) { await Logger.log(msg) };
};

public func work() : async () {
  await maybeLog("step 1");  // Extra message to self
  await maybeLog("step 2");  // Extra message to self
};

// Prefer: async* for zero-cost abstraction
func maybeLog(msg : Text) : async* () {
  if (logging) { await Logger.log(msg) };
};

public func work() : async () {
  await* maybeLog("step 1");  // Inline execution
  await* maybeLog("step 2");  // Inline execution
};
```

---

## Pipe Operator Idioms

Use the pipe operator `|>` to chain transformations naturally:

```motoko
// Avoid: deeply nested, reads inside-out
let result = Option.get(Option.map(users.get(id), func(u : User) : Text { u.name }), "Anonymous");

// Prefer: pipe for left-to-right reading
let result = users.get(id)
  |> Option.map(_, func(u : User) : Text { u.name })
  |> Option.get(_, "Anonymous");
```

### When to Use Pipes

| Use Pipes | Avoid Pipes |
|-----------|-------------|
| 3+ chained transformations | Simple 1-2 step operations |
| Complex data processing | Single function calls |
| When readability improves | When it adds no clarity |

```motoko
// Good use: complex transformation chain
let activeUserNames = users.vals()
  |> Iter.filter(_, func(u : User) : Bool { u.active })
  |> Iter.map(_, func(u : User) : Text { u.name })
  |> Iter.toArray(_);

// Overkill: simple operation
let doubled = n |> _ * 2;  // Just use: let doubled = n * 2;
```

---

## Common Idioms Quick Reference

### Type Conversions

```motoko
import Nat "mo:base/Nat";
import Int "mo:base/Int";
import Text "mo:base/Text";
import Blob "mo:base/Blob";
import Principal "mo:base/Principal";
import Nat8 "mo:base/Nat8";
import Nat32 "mo:base/Nat32";
import Nat64 "mo:base/Nat64";

// Nat <-> Text
let n : Nat = 42;
let t : Text = Nat.toText(n);              // "42"
let back : ?Nat = Nat.fromText(t);         // ?42

// Int <-> Text
let i : Int = -5;
let it : Text = Int.toText(i);             // "-5"

// Int <-> Nat (careful with negatives!)
let positive : Nat = Int.abs(i);           // Traps if i < 0!
let widened : Int = n;                     // Nat to Int is implicit

// Principal <-> Text
let p : Principal = Principal.fromText("aaaaa-aa");
let pt : Text = Principal.toText(p);       // "aaaaa-aa"

// Principal <-> Blob
let pb : Blob = Principal.toBlob(p);
let backP : Principal = Principal.fromBlob(pb);

// Text <-> Blob (UTF-8)
let tb : Blob = Text.encodeUtf8("hello");
let backT : ?Text = Text.decodeUtf8(tb);   // ?Text (can fail on invalid UTF-8)

// Blob <-> [Nat8]
let bytes : [Nat8] = Blob.toArray(tb);
let backB : Blob = Blob.fromArray(bytes);

// Bounded number conversions
let n64 : Nat64 = Nat64.fromNat(n);        // Traps if n > max Nat64
let backN : Nat = Nat64.toNat(n64);        // Always safe
```

### Canister Self-Reference

```motoko
import Principal "mo:base/Principal";

actor MyCanister {
  // Get own canister ID
  public query func whoAmI() : async Principal {
    Principal.fromActor(MyCanister)
  };

  // Use in ICRC transfers (send to self)
  public func depositToSelf(ledger : Principal, amount : Nat) : async () {
    let token = actor(Principal.toText(ledger)) : actor {
      icrc1_transfer : shared {...} -> async {...};
    };
    ignore await token.icrc1_transfer({
      to = { owner = Principal.fromActor(MyCanister); subaccount = null };
      // ...
    });
  };
}
```

### Subaccount Computation (ICRC-1)

```motoko
import Blob "mo:base/Blob";
import Array "mo:base/Array";
import Nat8 "mo:base/Nat8";
import Nat32 "mo:base/Nat32";
import Principal "mo:base/Principal";

// Subaccounts are 32-byte blobs
type Subaccount = Blob;

// Create subaccount from a Nat32 index (big-endian in last 4 bytes)
func subaccountFromIndex(index : Nat32) : Subaccount {
  let bytes = Array.tabulate<Nat8>(32, func(i : Nat) : Nat8 {
    if (i < 28) { 0 }
    else {
      let shift = 8 * (31 - i);  // 24, 16, 8, 0
      Nat8.fromNat(Nat32.toNat((index >> Nat32.fromNat(shift)) & 0xFF))
    }
  });
  Blob.fromArray(bytes)
};

// Create subaccount from Principal (for user-specific accounts)
func subaccountFromPrincipal(p : Principal) : Subaccount {
  let bytes = Blob.toArray(Principal.toBlob(p));
  let padded = Array.tabulate<Nat8>(32, func(i : Nat) : Nat8 {
    if (i < 32 - bytes.size()) { 0 }
    else { bytes[i - (32 - bytes.size())] }
  });
  Blob.fromArray(padded)
};

// Zero subaccount (default)
let nullSubaccount : Subaccount = Blob.fromArray(Array.freeze(Array.init<Nat8>(32, 0)));
```

### Iterator Compositions

```motoko
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import Option "mo:base/Option";

let items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Filter + map + collect
let result = Iter.toArray(
  Iter.map(
    Iter.filter(items.vals(), func(n : Nat) : Bool { n % 2 == 0 }),
    func(n : Nat) : Nat { n * 10 }
  )
);  // [20, 40, 60, 80, 100]

// Same with pipes (more readable)
let result2 = items.vals()
  |> Iter.filter(_, func(n : Nat) : Bool { n % 2 == 0 })
  |> Iter.map(_, func(n : Nat) : Nat { n * 10 })
  |> Iter.toArray(_);

// Take first N
let firstThree = Iter.toArray(Iter.take(items.vals(), 3));  // [1, 2, 3]

// Skip first N
let afterThree = Iter.toArray(Iter.drop(items.vals(), 3));  // [4, 5, 6, 7, 8, 9, 10]

// Find first match
let firstEven = Iter.find(items.vals(), func(n : Nat) : Bool { n % 2 == 0 });  // ?2

// Fold (reduce) - sum all elements
let sum = Iter.fold<Nat, Nat>(items.vals(), 0, func(acc, n) { acc + n });  // 55

// Concatenate iterators
let combined = Iter.toArray(Iter.concat([1, 2].vals(), [3, 4].vals()));  // [1, 2, 3, 4]

// Generate range
let range = Iter.toArray(Iter.range(0, 4));  // [0, 1, 2, 3, 4]

// Replicate value
let fives = Iter.toArray(Iter.replicate(3, 5));  // [5, 5, 5]
```

### Debug Printing

```motoko
import Debug "mo:base/Debug";

// Simple message
Debug.print("Processing started");

// Show any value with debug_show
let user = { name = "Alice"; age = 30; active = true };
Debug.print("User: " # debug_show(user));
// Output: User: {age = 30; active = true; name = "Alice"}

// Show complex structures
let data = [?1, null, ?3];
Debug.print("Data: " # debug_show(data));
// Output: Data: [?1, null, ?3]

// Conditional logging pattern
let DEBUG = true;
func log(msg : Text) { if (DEBUG) Debug.print(msg) };

// Trap with context
func mustFind(id : Nat) : User {
  switch (users.get(id)) {
    case (?u) { u };
    case null { Debug.trap("User not found: " # Nat.toText(id)) };
  }
};
```

### Null-Safe Chaining

```motoko
import Option "mo:base/Option";

// Chain optional operations
let result = do ? {
  let user = users.get(id)!;
  let profile = user.profile!;
  let email = profile.email!;
  email
};  // ?Text or null

// With transformation
let upperEmail = do ? {
  let user = users.get(id)!;
  Text.toUppercase(user.email!)
};

// Option combinators
let name = Option.get(
  Option.map(users.get(id), func(u : User) : Text { u.name }),
  "Unknown"
);

// Chain with default at end
let email = users.get(id)
  |> Option.chain(_, func(u : User) : ?Text { u.email })
  |> Option.get(_, "no-email@example.com");
```


---

# Motoko Testing Guide

## Testing with mops test

[mops](https://mops.one) includes a built-in test runner for Motoko unit tests.

### Setup

```bash
# Initialize mops if not already done
mops init

# Add the test library as a dev dependency
mops add test --dev
```

### Writing Tests

Place tests in `test/*.test.mo` files:

```motoko
// test/example.test.mo
import { test; suite; expect } "mo:test";

suite("Math operations", func() {
  test("addition works", func() {
    assert 2 + 2 == 4;
  });

  test("multiplication works", func() {
    assert 3 * 4 == 12;
  });
});
```

### Using the Test Library

```motoko
import { test; suite; expect; skip } "mo:test";

// Simple test
test("simple assertion", func() {
  assert true;
});

// Test suite for grouping
suite("User validation", func() {
  test("rejects empty name", func() {
    let result = validateName("");
    assert result == #err(#empty);
  });

  test("accepts valid name", func() {
    let result = validateName("Alice");
    assert result == #ok;
  });

  // Skip a test
  skip("pending feature", func() {
    // Not run
  });
});

// Async tests (for testing async functions)
test("async operation", func() : async () {
  let result = await someAsyncFunction();
  assert result == expected;
});
```

### Running Tests

```bash
# Run all tests
mops test

# Watch mode (re-run on file changes)
mops test --watch

# Verbose output
mops test --reporter verbose

# Run in WASI mode (faster, but no IC APIs)
mops test --mode wasi

# Run with replica (for tests using IC APIs like cycles, timers)
mops test --replica pocket-ic
```

### Replica Tests

For testing code that uses IC-specific APIs (cycles, timers, canister calls):

```motoko
// test/replica.test.mo
import { test } "mo:test/async";
import Cycles "mo:base/ExperimentalCycles";

test("canister has cycles", func() : async () {
  let balance = Cycles.balance();
  assert balance > 0;
});
```

Run with:

```bash
mops test --replica pocket-ic
```

### Test Reporter Options

| Reporter | Description |
|----------|-------------|
| `verbose` | Full test output with details |
| `files` | Show file-level results |
| `compact` | Minimal output |
| `silent` | No output (for CI) |

---

## Integration Testing with PocketIC

PocketIC provides local canister testing with deterministic behavior. `dfx start` uses PocketIC by default (since v0.26.0).

### Python Setup

```bash
pip3 install pocket-ic
```

### Python Test Example

```python
# tests/integration_tests.py
import unittest
from pocket_ic import PocketIC

class CounterTests(unittest.TestCase):
    def setUp(self):
        self.pic = PocketIC()
        self.canister_id = self.pic.create_canister()
        self.pic.add_cycles(self.canister_id, 2_000_000_000_000)

        # Load and install the Wasm
        with open(".dfx/local/canisters/counter/counter.wasm", "rb") as f:
            wasm = f.read()
        self.pic.install_code(self.canister_id, wasm, [])

    def test_initial_count_is_zero(self):
        response = self.pic.query_call(
            self.canister_id,
            "get",
            encode([])
        )
        assert decode(response) == 0

    def test_increment_increases_count(self):
        self.pic.update_call(self.canister_id, "inc", encode([]))
        response = self.pic.query_call(self.canister_id, "get", encode([]))
        assert decode(response) == 1

if __name__ == "__main__":
    unittest.main()
```

### Running PocketIC Tests

```bash
# Ensure canister is built first
dfx build

# Set the PocketIC binary path (dfx includes it)
export POCKET_IC_BIN="$(dfx cache show)/pocket-ic"

# Run tests
python3 tests/integration_tests.py
```

### Rust PocketIC Setup

```bash
cargo add pocket-ic --dev
```

### Rust Test Example

```rust
// tests/integration_tests.rs
use candid::{encode_one, decode_one, Principal};
use pocket_ic::PocketIc;

const INIT_CYCLES: u128 = 2_000_000_000_000;

#[test]
fn test_counter() {
    let pic = PocketIc::new();

    // Create and fund canister
    let canister_id = pic.create_canister();
    pic.add_cycles(canister_id, INIT_CYCLES);

    // Install Wasm
    let wasm = std::fs::read(".dfx/local/canisters/counter/counter.wasm")
        .expect("Wasm file not found");
    pic.install_canister(canister_id, wasm, vec![], None);

    // Test initial value
    let result = pic.query_call(
        canister_id,
        Principal::anonymous(),
        "get",
        encode_one(()).unwrap(),
    ).unwrap();
    let count: u64 = decode_one(&result).unwrap();
    assert_eq!(count, 0);

    // Test increment
    pic.update_call(
        canister_id,
        Principal::anonymous(),
        "inc",
        encode_one(()).unwrap(),
    ).unwrap();

    let result = pic.query_call(
        canister_id,
        Principal::anonymous(),
        "get",
        encode_one(()).unwrap(),
    ).unwrap();
    let count: u64 = decode_one(&result).unwrap();
    assert_eq!(count, 1);
}
```

### Multi-Subnet Testing

```rust
use pocket_ic::PocketIcBuilder;

let pic = PocketIcBuilder::new()
    .with_nns_subnet()
    .with_application_subnet()
    .with_application_subnet()
    .build();

// Create canister on specific subnet
let nns_subnet = pic.topology().get_nns_subnet().unwrap();
let canister_id = pic.create_canister_on_subnet(None, None, nns_subnet);
```

### Time Manipulation

```rust
use pocket_ic::PocketIc;
use std::time::Duration;

let pic = PocketIc::new();

// Advance time by 1 hour
pic.advance_time(Duration::from_secs(3600));

// Tick to process timers
pic.tick();
```

---

## End-to-End Testing with JavaScript

For frontend integration testing:

### Setup

```bash
npm install --save-dev vitest isomorphic-fetch
```

### Test File

```typescript
// tests/e2e.test.ts
import { describe, it, expect } from 'vitest';
import { Actor, HttpAgent } from '@dfinity/agent';
import { idlFactory } from '../src/declarations/backend';

describe('Backend canister', () => {
  const agent = new HttpAgent({ host: 'http://localhost:4943' });
  agent.fetchRootKey(); // Only for local testing!

  const backend = Actor.createActor(idlFactory, {
    agent,
    canisterId: process.env.CANISTER_ID_BACKEND!,
  });

  it('should greet correctly', async () => {
    const result = await backend.greet('World');
    expect(result).toBe('Hello, World!');
  });
});
```

### Running E2E Tests

```bash
# Deploy first
dfx deploy

# Run tests
npm test
```

---

## Testing Patterns

### Test Fixtures

```motoko
import { test; suite } "mo:test";

// Shared setup
func createTestUser() : User {
  { id = 1; name = "Test"; email = ?"test@example.com" }
};

suite("User operations", func() {
  test("can update name", func() {
    let user = createTestUser();
    let updated = updateName(user, "NewName");
    assert updated.name == "NewName";
  });
});
```

### Testing Error Cases

```motoko
import { test } "mo:test";
import Result "mo:base/Result";

test("rejects invalid input", func() {
  let result = validateEmail("not-an-email");
  switch (result) {
    case (#err(#invalidFormat)) { /* expected */ };
    case _ { assert false };
  };
});
```

### Testing Async Code

```motoko
import { test } "mo:test/async";

test("async operation completes", func() : async () {
  let result = await processData("input");
  assert Result.isOk(result);
});
```

### Property-Based Testing Pattern

```motoko
import { test } "mo:test";
import Random "mo:base/Random";

// Test with multiple random inputs
test("reverse twice is identity", func() {
  let inputs = [[1,2,3], [4,5,6,7], [], [42]];
  for (arr in inputs.vals()) {
    let reversed = Array.reverse(Array.reverse(arr));
    assert arr == reversed;
  };
});
```

---

## CI Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dfx
        uses: dfinity/setup-dfx@main

      - name: Install mops
        run: npm i -g ic-mops

      - name: Install dependencies
        run: mops install

      - name: Run unit tests
        run: mops test

      - name: Build canisters
        run: dfx build

      - name: Run integration tests
        run: |
          dfx start --background
          dfx deploy
          npm test
```

---

## Benchmarking

Use the `bench` package to measure performance:

```bash
mops add bench --dev
```

### Writing Benchmarks

```motoko
// bench/example.bench.mo
import Bench "mo:bench";
import Array "mo:base/Array";

module {
  public func init() : Bench.Bench {
    let bench = Bench.Bench();

    bench.name("Array operations");
    bench.description("Comparing array methods");

    bench.rows(["size 100", "size 1000", "size 10000"]);
    bench.cols(["append", "map", "filter"]);

    bench.runner(func(row, col) {
      let size = switch row {
        case "size 100" 100;
        case "size 1000" 1000;
        case _ 10000;
      };

      let arr = Array.tabulate<Nat>(size, func(i) { i });

      switch col {
        case "append" { ignore Array.append(arr, arr) };
        case "map" { ignore Array.map<Nat, Nat>(arr, func(n) { n * 2 }) };
        case "filter" { ignore Array.filter<Nat>(arr, func(n) { n % 2 == 0 }) };
        case _ {};
      };
    });

    bench
  };
}
```

### Running Benchmarks

```bash
mops bench
```

### Inline Performance Measurement

```motoko
import IC "mo:base/ExperimentalInternetComputer";

actor {
  public func measureWork() : async { instructions : Nat64 } {
    let start = IC.countInstructions();
    // ... work to measure ...
    let end = IC.countInstructions();
    { instructions = end - start }
  };
}
```

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Use `mops test` for unit tests | Fast, no replica needed |
| Use PocketIC for integration tests | Deterministic, simulates mainnet |
| Test error paths explicitly | Ensure proper error handling |
| Keep unit tests fast | Run frequently during development |
| Use fixtures for common setup | DRY, consistent test data |
| Test upgrade scenarios | Catch data migration issues early |
| Run tests in CI | Catch regressions automatically |
| Benchmark critical paths | Catch performance regressions |


---

# Advanced Motoko Concepts

## Modules

Modules are Motoko's unit of code organization. Every `.mo` file is implicitly a module.

### Defining a Module

```motoko
// utils.mo
module {
  // Private - not exported
  let secret = "hidden";

  // Public - exported to importers
  public func double(n : Nat) : Nat { n * 2 };

  // Public type
  public type Result<T> = { #ok : T; #err : Text };

  // Public nested module
  public module Math {
    public func square(n : Nat) : Nat { n * n };
  };
}
```

### Importing Modules

```motoko
// main.mo
import Utils "./utils";           // Local module (relative path)
import Array "mo:base/Array";     // Base library
import Pkg "mo:mypackage/Lib";    // External package (via mops)

actor {
  public func test() : async Nat {
    Utils.double(21)  // 42
  };
}
```

### Module vs Actor

| Aspect | Module | Actor |
|--------|--------|-------|
| State | Stateless (no `var` at top level) | Stateful |
| Instantiation | Imported, not instantiated | Deployed as canister |
| Functions | Synchronous | Async (`async T`) |
| Use case | Libraries, utilities, types | Services, smart contracts |

### Named Imports

```motoko
// Import specific items
import { double; Result } "./utils";

// Rename on import
import { double = dbl } "./utils";
let x = dbl(5);
```

### Module Visibility Rules

```motoko
module {
  // Private by default - only visible within this module
  let privateVar = 0;
  func privateFunc() {};
  type PrivateType = Nat;

  // Public - visible to importers
  public let publicVar = 1;
  public func publicFunc() {};
  public type PublicType = Text;

  // Private types can be used in public signatures if they're aliases
  type Id = Nat;  // Private alias
  public func getId() : Id { 0 };  // OK - Id expands to Nat
}
```

---

## Shared Types

Only **shared types** can cross async boundaries (function arguments, return values, stable variables). The compiler enforces this.

### What IS Shared

| Type | Shared? | Notes |
|------|---------|-------|
| `Nat`, `Int`, `Nat8`, `Int32`, etc. | ✅ | All number types |
| `Bool`, `Text`, `Blob`, `Principal` | ✅ | Primitives |
| `?T` (where T is shared) | ✅ | Options |
| `[T]` (immutable, T shared) | ✅ | Immutable arrays |
| `(T1, T2, ...)` (all shared) | ✅ | Tuples |
| `{field : T; ...}` (all T shared) | ✅ | Records |
| `{#tag1 : T1; #tag2; ...}` | ✅ | Variants |
| `shared ... -> async T` | ✅ | Shared functions |
| `actor { ... }` | ✅ | Actor references |

### What is NOT Shared

| Type | Shared? | Why |
|------|---------|-----|
| `[var T]` | ❌ | Mutable arrays can't be shared |
| `var` fields in records | ❌ | Mutable fields can't be shared |
| Local functions | ❌ | Capture mutable state |
| Objects with methods | ❌ | Methods are local functions |
| `Error` | ❌ | Can only be thrown/caught, not passed |

```motoko
// This compiles - all shared types
public func process(data : { id : Nat; name : Text }) : async [Text] { ... };

// This FAILS - mutable array not shared
public func bad(data : [var Nat]) : async () { ... };  // Error!

// This FAILS - record has mutable field
public type BadRecord = { var count : Nat };
public func bad2(r : BadRecord) : async () { ... };  // Error!
```

### Workaround: Convert at Boundaries

```motoko
import Array "mo:base/Array";

actor {
  // Internal mutable state
  var items : [var Text] = [var];

  // Public API uses immutable (shared) types
  public func getItems() : async [Text] {
    Array.freeze(items)  // Convert mutable -> immutable
  };

  public func setItems(newItems : [Text]) : async () {
    items := Array.thaw(newItems);  // Convert immutable -> mutable
  };
}
```

---

## Commit Points and Atomicity

Understanding when state is committed is **critical** for correctness.

### The Rule

State changes are committed at **await points**. If code traps after an await, previous changes persist.

```motoko
actor {
  var balance : Nat = 100;

  public func riskyTransfer() : async () {
    balance -= 50;                    // State changed
    await otherCanister.notify();     // COMMIT POINT - balance=50 is saved
    balance -= 50;                    // More changes
    assert(false);                    // TRAP! But balance is already 50, not 100
  };
}
```

### Safe Pattern: Check-Then-Act

```motoko
public func safeTransfer(amount : Nat) : async Result<(), Error> {
  // 1. Validate BEFORE any state changes
  if (balance < amount) { return #err(#insufficientFunds) };

  // 2. Make external call BEFORE modifying local state
  let result = await recipient.receive(amount);

  // 3. Only modify state after successful external call
  switch (result) {
    case (#ok) {
      balance -= amount;  // Safe - we know transfer succeeded
      #ok()
    };
    case (#err(e)) { #err(e) };
  };
}
```

### Trap Rollback Rules

| Scenario | State Changes | Rolled Back? |
|----------|---------------|--------------|
| Trap before any await | All changes | ✅ Yes |
| Trap after await | Changes before await | ❌ No (committed) |
| Trap after await | Changes after await | ✅ Yes |
| Called canister traps | Caller's state | ❌ No effect on caller |

### Two-Phase Commit Pattern

For complex operations, use a two-phase approach:

```motoko
public type TransferStatus = { #pending; #completed; #failed };

stable var pendingTransfers : [(Nat, TransferStatus)] = [];

public func initiateTransfer(id : Nat, amount : Nat) : async Result<(), Error> {
  // Phase 1: Reserve funds, mark pending
  if (balance < amount) { return #err(#insufficientFunds) };
  balance -= amount;
  pendingTransfers := Array.append(pendingTransfers, [(id, #pending)]);

  // Commit point
  try {
    await recipient.receive(amount);
    // Phase 2: Mark completed
    updateTransferStatus(id, #completed);
    #ok()
  } catch (e) {
    // Rollback: restore funds, mark failed
    balance += amount;
    updateTransferStatus(id, #failed);
    #err(#transferFailed)
  };
}
```

---

## Bounded Number Types

Motoko has unbounded (`Nat`, `Int`) and bounded number types.

### Available Types

| Type | Range | Bytes |
|------|-------|-------|
| `Nat8` | 0 to 255 | 1 |
| `Nat16` | 0 to 65,535 | 2 |
| `Nat32` | 0 to 4,294,967,295 | 4 |
| `Nat64` | 0 to 18,446,744,073,709,551,615 | 8 |
| `Int8` | -128 to 127 | 1 |
| `Int16` | -32,768 to 32,767 | 2 |
| `Int32` | -2,147,483,648 to 2,147,483,647 | 4 |
| `Int64` | -9,223,372,036,854,775,808 to ... | 8 |

### Overflow Behavior

Bounded types **trap on overflow** (no silent wraparound):

```motoko
let x : Nat8 = 255;
let y : Nat8 = x + 1;  // TRAP! Overflow

let a : Int8 = 127;
let b : Int8 = a + 1;  // TRAP! Overflow
```

### Wrapping Arithmetic

Use wrapping operators for intentional wraparound:

```motoko
import Nat8 "mo:base/Nat8";

let x : Nat8 = 255;
let y : Nat8 = x +% 1;  // y = 0 (wraps around)

// Available wrapping operators: +% -% *% **%
```

### Conversions

```motoko
import Nat "mo:base/Nat";
import Nat64 "mo:base/Nat64";
import Int "mo:base/Int";

// Unbounded to bounded (can trap if too large)
let n : Nat = 1000;
let n64 : Nat64 = Nat64.fromNat(n);  // Safe, 1000 fits in Nat64

// Bounded to unbounded (always safe)
let back : Nat = Nat64.toNat(n64);

// Between bounded types
let n32 : Nat32 = Nat32.fromNat(Nat64.toNat(n64));

// Int to Nat (traps if negative)
let i : Int = 42;
let asNat : Nat = Int.abs(i);  // Safe for positive
```

### When to Use Bounded Types

| Use Case | Recommendation |
|----------|----------------|
| General arithmetic | `Nat`, `Int` (unbounded, safe) |
| Candid compatibility | Match interface types |
| Memory efficiency | Bounded when storing many values |
| Bitwise operations | `Nat8`, `Nat32`, `Nat64` |
| Timestamps | `Int` (nanoseconds from Time.now()) |
| Cycles | `Nat` (unbounded) |

---

## Text Operations

```motoko
import Text "mo:base/Text";
import Iter "mo:base/Iter";
import Char "mo:base/Char";
```

### Common Operations

```motoko
// Concatenation
let full = "Hello" # " " # "World";  // "Hello World"

// Length (characters, not bytes)
let len = Text.size("Hello");  // 5

// Comparison
Text.equal("a", "a");  // true
Text.compare("a", "b");  // #less

// Contains
Text.contains("Hello World", #text "World");  // true
Text.contains("Hello", #char 'e');  // true

// Starts/ends with
Text.startsWith("Hello", #text "He");  // true
Text.endsWith("Hello", #text "lo");  // true
```

### Pattern Types

```motoko
// #text - literal substring
Text.contains("abc", #text "bc");  // true

// #char - single character
Text.contains("abc", #char 'b');  // true

// #predicate - custom function
Text.contains("abc123", #predicate (func(c : Char) : Bool { Char.isDigit(c) }));  // true
```

### Split and Join

```motoko
// Split by pattern
let parts = Iter.toArray(Text.split("a,b,c", #char ','));  // ["a", "b", "c"]

// Join with separator
let joined = Text.join(", ", ["a", "b", "c"].vals());  // "a, b, c"

// Split into characters
let chars = Iter.toArray(Text.toIter("Hello"));  // ['H', 'e', 'l', 'l', 'o']
```

### Search and Replace

```motoko
// Replace all occurrences
let replaced = Text.replace("hello world", #char 'o', "0");  // "hell0 w0rld"

// Trim whitespace
let trimmed = Text.trim("  hello  ", #predicate Char.isWhitespace);  // "hello"

// Extract substring (via iterator)
func substring(t : Text, start : Nat, len : Nat) : Text {
  let chars = Iter.toArray(Text.toIter(t));
  Text.fromIter(Array.slice(chars, start, start + len).vals())
};
```

### Encoding

```motoko
// Text to UTF-8 bytes
let blob : Blob = Text.encodeUtf8("Hello");

// UTF-8 bytes to Text (can fail)
let maybeText : ?Text = Text.decodeUtf8(blob);  // ?"Hello"
```

---

## Blob Operations

```motoko
import Blob "mo:base/Blob";
import Array "mo:base/Array";
```

### Creating Blobs

```motoko
// From literal (hex escape sequences)
let b1 : Blob = "\00\01\02\ff";

// From byte array
let bytes : [Nat8] = [0, 1, 2, 255];
let b2 : Blob = Blob.fromArray(bytes);

// From Text (UTF-8 encoded)
let b3 : Blob = Text.encodeUtf8("Hello");
```

### Blob Operations

```motoko
// Size in bytes
let size = Blob.size(myBlob);  // Nat

// To byte array
let bytes : [Nat8] = Blob.toArray(myBlob);

// Comparison
Blob.equal(b1, b2);  // Bool
Blob.compare(b1, b2);  // Order

// Hash (for HashMap keys)
let hash = Blob.hash(myBlob);  // Nat32
```

### Common Conversions

```motoko
// Principal <-> Blob
import Principal "mo:base/Principal";
let p : Principal = Principal.fromBlob(myBlob);
let b : Blob = Principal.toBlob(p);

// Text <-> Blob (UTF-8)
let blob = Text.encodeUtf8("Hello");
let text = Text.decodeUtf8(blob);  // ?Text (can fail)

// Nat <-> Blob (for hashing, encoding)
import Nat64 "mo:base/Nat64";

// Manual encoding for Nat64 to big-endian bytes
func nat64ToBlob(n : Nat64) : Blob {
  let bytes : [var Nat8] = [var 0, 0, 0, 0, 0, 0, 0, 0];
  var remaining = n;
  for (i in Iter.range(7, 0)) {
    bytes[i] := Nat8.fromNat(Nat64.toNat(remaining % 256));
    remaining := remaining / 256;
  };
  Blob.fromArray(Array.freeze(bytes))
};
```

---

## Certified Variables

Certified variables allow query responses to be verified without consensus.

### How It Works

1. Canister stores data in a certified data structure
2. ICP signs a hash of certified data during updates
3. Query responses include the data + certificate
4. Clients verify the certificate against ICP's public key

### Basic Setup

```motoko
import CertifiedData "mo:base/CertifiedData";
import Blob "mo:base/Blob";
import Text "mo:base/Text";

actor {
  stable var certifiedValue : Text = "";

  // Update function: set value AND certify it
  public func setValue(newValue : Text) : async () {
    certifiedValue := newValue;
    // Certify the hash of the value
    CertifiedData.set(Text.encodeUtf8(newValue));
  };

  // Query function: return value with certificate
  public query func getValue() : async { value : Text; certificate : ?Blob } {
    {
      value = certifiedValue;
      certificate = CertifiedData.getCertificate();
    }
  };
}
```

### Certified Asset Pattern

For multiple values, use a Merkle tree (hash tree):

```motoko
import CertTree "mo:cert/CertTree";  // Third-party library

actor {
  var tree = CertTree.empty();

  public func setAsset(path : Text, content : Blob) : async () {
    tree := CertTree.insert(tree, path, content);
    CertifiedData.set(CertTree.root(tree));
  };

  public query func getAsset(path : Text) : async {
    content : ?Blob;
    certificate : ?Blob;
    witness : Blob;
  } {
    {
      content = CertTree.lookup(tree, path);
      certificate = CertifiedData.getCertificate();
      witness = CertTree.witness(tree, path);
    }
  };
}
```

### When to Use Certified Variables

| Use Case | Certified? | Why |
|----------|------------|-----|
| Asset canister (HTML, JS, CSS) | ✅ Yes | Browsers verify authenticity |
| Public data queries | ✅ Yes | Clients can verify without trust |
| Internal data | ❌ No | Overhead not worth it |
| Frequently changing data | ⚠️ Maybe | Must re-certify on each update |

---

## Generics (Type Parameters)

Write reusable functions and types with type parameters.

```motoko
// Generic function
func findFirst<T>(arr : [T], pred : T -> Bool) : ?T {
  for (item in arr.vals()) {
    if (pred(item)) return ?item;
  };
  null
};
let result = findFirst<Nat>([1, 2, 3], func(n) { n > 1 });  // ?2

// Generic type
type Box<T> = { value : T; createdAt : Int };

// Generic class
class Stack<T>() {
  var items : List.List<T> = List.nil();
  public func push(item : T) { items := List.push(item, items) };
  public func pop() : ?T { List.pop(items) };
};
```

### Generic Function Patterns

```motoko
import Array "mo:base/Array";
import Result "mo:base/Result";
import Option "mo:base/Option";

// Constrained generics - require specific operations
func sortBy<T>(arr : [T], compare : (T, T) -> Order.Order) : [T] {
  Array.sort(arr, compare)
};

// Multiple type parameters
func mapResult<A, B, E>(r : Result.Result<A, E>, f : A -> B) : Result.Result<B, E> {
  switch (r) {
    case (#ok(a)) { #ok(f(a)) };
    case (#err(e)) { #err(e) };
  }
};

// Generic with default
func getOrDefault<T>(opt : ?T, default : T) : T {
  Option.get(opt, default)
};

// Type inference - often don't need explicit types
let nums = [1, 2, 3];
let doubled = Array.map(nums, func(n) { n * 2 });  // Type inferred as [Nat]

// When explicit types are needed (ambiguous cases)
let empty : [Nat] = [];  // Must specify - [] could be any type
let result = Array.find<Nat>(nums, func(n) { n > 5 });  // Explicit for clarity
```

### When to Use Type Parameters

| Use Case | Example |
|----------|---------|
| Container types | `Buffer<T>`, `HashMap<K, V>` |
| Utility functions | `map`, `filter`, `fold` |
| Error handling | `Result<T, E>` |
| Avoid code duplication | Same logic for different types |

---

## Recursive Types

Recursive types reference themselves, enabling tree structures and linked data:

```motoko
import List "mo:base/List";

// Simple recursive type (linked list pattern)
type LinkedList<T> = ?(T, LinkedList<T>);

// Binary tree
type Tree<T> = {
  #leaf;
  #node : { value : T; left : Tree<T>; right : Tree<T> };
};

// Build a tree
func leaf<T>() : Tree<T> = #leaf;
func node<T>(v : T, l : Tree<T>, r : Tree<T>) : Tree<T> {
  #node({ value = v; left = l; right = r })
};

let tree : Tree<Nat> = node(
  5,
  node(3, leaf(), leaf()),
  node(8, leaf(), leaf())
);

// Recursive function to traverse
func sum(t : Tree<Nat>) : Nat {
  switch (t) {
    case (#leaf) { 0 };
    case (#node({ value; left; right })) {
      value + sum(left) + sum(right)
    };
  }
};

// JSON-like structure
type Json = {
  #null_;
  #bool_ : Bool;
  #number : Float;
  #string_ : Text;
  #array : [Json];
  #object_ : [(Text, Json)];
};

// Recursive processing
func countNodes(json : Json) : Nat {
  switch (json) {
    case (#null_ or #bool_(_) or #number(_) or #string_(_)) { 1 };
    case (#array(items)) {
      var count = 1;
      for (item in items.vals()) { count += countNodes(item) };
      count
    };
    case (#object_(fields)) {
      var count = 1;
      for ((_, value) in fields.vals()) { count += countNodes(value) };
      count
    };
  }
};
```

### Mutual Recursion

Types that reference each other:

```motoko
// Expression and Statement reference each other
type Expr = {
  #literal : Int;
  #variable : Text;
  #binOp : { op : Text; left : Expr; right : Expr };
  #block : [Stmt];  // Expr contains Stmt
};

type Stmt = {
  #assign : { name : Text; value : Expr };  // Stmt contains Expr
  #if_ : { cond : Expr; then_ : [Stmt]; else_ : [Stmt] };
  #return_ : Expr;
};
```

---

## Regions (Scalable Stable Memory)

Regions provide direct access to stable memory for storing large amounts of data that don't fit in the Motoko heap.

### Why Use Regions

| Approach | Heap Limit | Use Case |
|----------|------------|----------|
| `stable var` | ~4GB (heap) | Small to medium data |
| `Region` | 64GB+ (stable memory) | Large data, custom layouts |

### Basic Region Usage

```motoko
import Region "mo:base/Region";
import Nat64 "mo:base/Nat64";

actor {
  stable var dataRegion : Region.Region = Region.new();
  stable var size : Nat64 = 0;

  public func writeBytes(data : Blob) : async Nat64 {
    let offset = size;
    let dataSize = Nat64.fromNat(data.size());

    // Grow region if needed (pages are 64KB)
    let requiredPages = (size + dataSize + 65535) / 65536;
    let currentPages = Region.size(dataRegion);
    if (requiredPages > currentPages) {
      ignore Region.grow(dataRegion, requiredPages - currentPages);
    };

    // Write data
    Region.storeBlob(dataRegion, offset, data);
    size += dataSize;
    offset
  };

  public query func readBytes(offset : Nat64, len : Nat) : async Blob {
    Region.loadBlob(dataRegion, offset, len)
  };
}
```

### Region API

```motoko
import Region "mo:base/Region";

// Create a new region
let r = Region.new();

// Get current size in 64KB pages
let pages : Nat64 = Region.size(r);

// Grow by n pages (returns old size, or traps if out of memory)
let oldSize = Region.grow(r, 10);  // Add 10 pages (640KB)

// Store/load primitives
Region.storeNat8(r, offset, value);
Region.storeNat16(r, offset, value);
Region.storeNat32(r, offset, value);
Region.storeNat64(r, offset, value);
Region.storeBlob(r, offset, blob);

let n8 : Nat8 = Region.loadNat8(r, offset);
let n64 : Nat64 = Region.loadNat64(r, offset);
let blob : Blob = Region.loadBlob(r, offset, size);
```

### Region vs ExperimentalStableMemory

| Feature | `Region` | `ExperimentalStableMemory` |
|---------|----------|---------------------------|
| Multiple regions | Yes | No (single global) |
| Isolation | Each region independent | Shared space |
| Recommended | Yes | Legacy, avoid in new code |

---

## Canister Lifecycle Hooks

System functions that run at specific points in a canister's lifecycle.

### All System Functions

```motoko
actor {
  // Called before upgrade (serialize state)
  system func preupgrade() {
    // Save non-stable data to stable vars
  };

  // Called after upgrade (deserialize state)
  system func postupgrade() {
    // Restore non-stable data from stable vars
  };

  // Called when main memory is running low
  system func lowmemory() : async* () {
    Debug.print("Low memory warning!");
  };

  // Called periodically (legacy - prefer Timer)
  system func heartbeat() : async () {
    // Periodic work, runs every ~1 second
    // Costs cycles even if empty!
  };

  // Called to validate incoming messages (DoS protection)
  system func inspect({
    caller : Principal;
    arg : Blob;
    msg : { #update : Text; #query : Text }
  }) : Bool {
    // Return false to reject the call
    true
  };

  // Timer callback (modern approach)
  system func timer(setGlobalTimer : Nat64 -> ()) : async () {
    // Handle timer expiry
    setGlobalTimer(Nat64.fromIntWrap(Time.now()) + 60_000_000_000);  // Reschedule in 60s
  };
}
```

### Upgrade Lifecycle

```
1. preupgrade() runs on OLD code
2. Stable vars serialized
3. NEW code installed
4. Stable vars deserialized
5. postupgrade() runs on NEW code
```

### Heartbeat vs Timer

| Feature | `heartbeat` | `Timer` |
|---------|-------------|---------|
| Frequency | ~1 second | Configurable |
| Cost | Always costs cycles | Only when scheduled |
| Control | Always running | Start/stop/cancel |
| Recommendation | Avoid | Prefer |

```motoko
// Prefer Timer over heartbeat
import Timer "mo:base/Timer";

actor {
  let timerId = Timer.recurringTimer<system>(#seconds 60, func() : async () {
    // Runs every 60 seconds
  });
}
```

---

## Composite Queries (Experimental)

Call other canisters from query functions. Responses are NOT certified.

```motoko
import IC "mo:base/ExperimentalInternetComputer";

actor {
  // Regular query - can't call other canisters
  public query func localQuery() : async Nat { 42 };

  // Composite query - CAN call other canisters
  public composite query func compositeQuery(target : Principal) : async Text {
    let remote = actor(Principal.toText(target)) : actor {
      getName : query () -> async Text;
    };
    await remote.getName()  // Query call to another canister
  };
}
```

### Limitations

- Results are NOT certified (can't trust for security-critical data)
- Can only call `query` and `composite query` functions on other canisters (no update calls)
- More expensive than local queries
- Still faster than update calls

---

## Reentrancy and Concurrency

Motoko actors process messages sequentially, but await points can interleave execution.

### The Problem

```motoko
actor {
  var balance : Nat = 100;

  public func withdraw(amount : Nat) : async () {
    // Check
    assert(balance >= amount);

    // Await - OTHER MESSAGES CAN RUN HERE
    await notifyWithdrawal(amount);

    // Act - balance might have changed!
    balance -= amount;  // Could underflow if another withdraw ran
  };
}
```

### Safe Patterns

**Pattern 1: Modify state before await**

```motoko
public func withdraw(amount : Nat) : async Result<(), Error> {
  if (balance < amount) { return #err(#insufficientFunds) };

  balance -= amount;  // Deduct BEFORE await

  try {
    await externalCall();
    #ok()
  } catch (e) {
    balance += amount;  // Rollback on failure
    #err(#externalError)
  };
};
```

**Pattern 2: Locks**

```motoko
var locked : Bool = false;

public func criticalSection() : async Result<(), Error> {
  if (locked) { return #err(#busy) };

  locked := true;
  try {
    await doWork();
    locked := false;
    #ok()
  } catch (e) {
    locked := false;
    #err(#failed)
  };
};
```

**Pattern 3: Request IDs for deduplication**

```motoko
stable var processedRequests : [Nat] = [];

public func idempotentAction(requestId : Nat) : async Result<(), Error> {
  // Check if already processed
  for (id in processedRequests.vals()) {
    if (id == requestId) { return #ok() };  // Already done
  };

  // Process
  await doAction();

  // Mark as processed
  processedRequests := Array.append(processedRequests, [requestId]);
  #ok()
};
```

---

## Management Canister

The management canister (`aaaaa-aa`) is a virtual system canister that provides programmatic control over canisters.

### Importing the Management Canister

```motoko
// Define the management canister interface
module IC {
  public type canister_id = Principal;
  public type wasm_module = Blob;

  public type canister_settings = {
    controllers : ?[Principal];
    compute_allocation : ?Nat;
    memory_allocation : ?Nat;
    freezing_threshold : ?Nat;
  };

  public type Self = actor {
    create_canister : shared { settings : ?canister_settings } -> async { canister_id : canister_id };
    install_code : shared {
      arg : Blob;
      wasm_module : wasm_module;
      mode : { #reinstall; #upgrade; #install };
      canister_id : canister_id;
    } -> async ();
    update_settings : shared {
      canister_id : canister_id;
      settings : canister_settings;
    } -> async ();
    start_canister : shared { canister_id : canister_id } -> async ();
    stop_canister : shared { canister_id : canister_id } -> async ();
    delete_canister : shared { canister_id : canister_id } -> async ();
    canister_status : shared { canister_id : canister_id } -> async {
      status : { #running; #stopping; #stopped };
      memory_size : Nat;
      cycles : Nat;
      settings : canister_settings;
      module_hash : ?Blob;
    };
    deposit_cycles : shared { canister_id : canister_id } -> async ();
  };
};
```

### Creating Canisters Programmatically

```motoko
import Cycles "mo:base/ExperimentalCycles";
import Principal "mo:base/Principal";

actor Factory {
  let ic : IC.Self = actor "aaaaa-aa";

  public func createCanister() : async Principal {
    // Attach cycles for canister creation
    Cycles.add<system>(1_000_000_000_000);  // 1T cycles

    let result = await ic.create_canister({ settings = null });
    result.canister_id
  };

  public func createWithSettings(controllers : [Principal]) : async Principal {
    Cycles.add<system>(1_000_000_000_000);

    let settings : IC.canister_settings = {
      controllers = ?controllers;
      compute_allocation = null;
      memory_allocation = null;
      freezing_threshold = null;
    };

    let result = await ic.create_canister({ settings = ?settings });
    result.canister_id
  };
};
```

### Installing Code

```motoko
public func installCode(canisterId : Principal, wasmModule : Blob, arg : Blob) : async () {
  await ic.install_code({
    canister_id = canisterId;
    wasm_module = wasmModule;
    mode = #install;
    arg = arg;
  });
};

public func upgradeCode(canisterId : Principal, wasmModule : Blob, arg : Blob) : async () {
  await ic.install_code({
    canister_id = canisterId;
    wasm_module = wasmModule;
    mode = #upgrade;
    arg = arg;
  });
};
```

### Canister Lifecycle Management

```motoko
public func stopCanister(canisterId : Principal) : async () {
  await ic.stop_canister({ canister_id = canisterId });
};

public func startCanister(canisterId : Principal) : async () {
  await ic.start_canister({ canister_id = canisterId });
};

public func deleteCanister(canisterId : Principal) : async () {
  // Must be stopped first
  await ic.stop_canister({ canister_id = canisterId });
  await ic.delete_canister({ canister_id = canisterId });
};

public func getStatus(canisterId : Principal) : async {
  status : { #running; #stopping; #stopped };
  cycles : Nat;
} {
  let status = await ic.canister_status({ canister_id = canisterId });
  { status = status.status; cycles = status.cycles }
};
```

### Depositing Cycles

```motoko
public func topUpCanister(canisterId : Principal, amount : Nat) : async () {
  Cycles.add<system>(amount);
  await ic.deposit_cycles({ canister_id = canisterId });
};
```

### Using the mops `ic` Package

For convenience, use the [ic package](https://mops.one/ic):

```bash
mops add ic
```

```motoko
import IC "mo:ic";

actor {
  public func createCanister() : async Principal {
    Cycles.add<system>(1_000_000_000_000);
    let result = await IC.management.create_canister({ settings = null });
    result.canister_id
  };
};
```

---

## Upgrade Migrations (Schema Changes)

When stable variable types change between versions, use migration functions to transform the data.

### Basic Migration Syntax

```motoko
// version2.mo - renaming a field
import Prim "mo:prim";

(with migration = func(old : { var count : Nat }) : { var total : Nat } {
  { var total = old.count }
})
actor {
  stable var total : Nat = 0;

  public func get() : async Nat { total };
};
```

### Migration Module Pattern

For complex migrations, use a separate module:

```motoko
// Migration.mo
module {
  public func run(old : {
    var users : [(Text, Nat)];
  }) : {
    var users : [(Text, { age : Nat; active : Bool })];
  } {
    let newUsers = Array.map<(Text, Nat), (Text, { age : Nat; active : Bool })>(
      old.users,
      func((name, age)) { (name, { age; active = true }) }
    );
    { var users = newUsers }
  };
};
```

```motoko
// main.mo
import Migration "Migration";

(with migration = Migration.run)
actor {
  stable var users : [(Text, { age : Nat; active : Bool })] = [];
};
```

### Common Migration Scenarios

**Adding a field with default value:**

```motoko
(with migration = func(old : { var name : Text }) : { var name : Text; var email : ?Text } {
  { var name = old.name; var email = null }
})
```

**Removing a field:**

```motoko
(with migration = func(old : { var name : Text; var deprecated : Nat }) : { var name : Text } {
  { var name = old.name }
})
```

**Changing field type:**

```motoko
(with migration = func(old : { var count : Nat }) : { var count : Int } {
  { var count = old.count }  // Nat widened to Int automatically
})
```

**Renaming multiple fields:**

```motoko
(with migration = func(old : {
  var firstName : Text;
  var lastName : Text;
}) : {
  var fullName : Text;
} {
  { var fullName = old.firstName # " " # old.lastName }
})
```

### Migration Best Practices

| Practice | Rationale |
|----------|-----------|
| Keep migrations simple | Complex logic can fail during upgrade |
| Test migrations locally | Use `dfx deploy --mode upgrade` |
| Version your migrations | Track schema changes in code |
| Make migrations idempotent | Safe to re-run if upgrade fails |
| Preserve data, not structure | Focus on what data means, not how stored |

---

## Large-Scale Stable Storage

For data that exceeds heap limits, use Regions for direct stable memory access.

### Indexed Region Storage

```motoko
import Region "mo:base/Region";
import Nat64 "mo:base/Nat64";
import Blob "mo:base/Blob";

actor BlobStore {
  // Index: maps blob ID to (offset, length) in data region
  stable var indexRegion : Region.Region = Region.new();
  stable var dataRegion : Region.Region = Region.new();
  stable var nextId : Nat64 = 0;
  stable var dataOffset : Nat64 = 0;

  let INDEX_ENTRY_SIZE : Nat64 = 16; // 8 bytes offset + 8 bytes length

  public func store(data : Blob) : async Nat64 {
    let id = nextId;
    let offset = dataOffset;
    let len = Nat64.fromNat(data.size());

    // Grow data region if needed
    growRegionIfNeeded(dataRegion, offset + len);

    // Store data
    Region.storeBlob(dataRegion, offset, data);

    // Grow index region if needed
    let indexOffset = id * INDEX_ENTRY_SIZE;
    growRegionIfNeeded(indexRegion, indexOffset + INDEX_ENTRY_SIZE);

    // Store index entry
    Region.storeNat64(indexRegion, indexOffset, offset);
    Region.storeNat64(indexRegion, indexOffset + 8, len);

    nextId += 1;
    dataOffset += len;
    id
  };

  public query func load(id : Nat64) : async ?Blob {
    if (id >= nextId) return null;

    let indexOffset = id * INDEX_ENTRY_SIZE;
    let offset = Region.loadNat64(indexRegion, indexOffset);
    let len = Region.loadNat64(indexRegion, indexOffset + 8);

    ?Region.loadBlob(dataRegion, offset, Nat64.toNat(len))
  };

  func growRegionIfNeeded(region : Region.Region, requiredBytes : Nat64) {
    let requiredPages = (requiredBytes + 65535) / 65536;
    let currentPages = Region.size(region);
    if (requiredPages > currentPages) {
      ignore Region.grow(region, requiredPages - currentPages);
    };
  };
};
```

### Stable B-Tree Pattern

For key-value storage at scale, consider community libraries:

```bash
mops add stableheapbtreemap
```

```motoko
import BTree "mo:stableheapbtreemap/BTree";
import Text "mo:base/Text";

actor {
  stable var tree = BTree.init<Text, Blob>(?32);  // Order 32

  public func put(key : Text, value : Blob) : async () {
    ignore BTree.insert(tree, Text.compare, key, value);
  };

  public func get(key : Text) : async ?Blob {
    BTree.get(tree, Text.compare, key)
  };
};
```

### Memory Layout Considerations

| Approach | Heap Limit | Stable Memory | Use Case |
|----------|------------|---------------|----------|
| `stable var` | ~4GB | Auto-managed | Small-medium data |
| `Region` | N/A | 64GB+ per region | Large blobs, custom layout |
| Stable BTree | N/A | 64GB+ | Large key-value stores |
| Multiple regions | N/A | Isolated spaces | Separate data domains |

---

## Canister Snapshots

Snapshots allow backing up and restoring canister state via the management canister.

### Taking a Snapshot

```motoko
import IC "mo:ic";
import Cycles "mo:base/ExperimentalCycles";

actor {
  let ic : IC.Self = actor "aaaaa-aa";

  public func takeSnapshot() : async Blob {
    // Requires controller permissions
    let result = await ic.take_canister_snapshot({
      canister_id = Principal.fromActor(this);
      replace_snapshot = null;
    });
    result.id
  };
};
```

### Using dfx for Snapshots

```bash
# Take a snapshot
dfx canister snapshot create my_canister

# List snapshots
dfx canister snapshot list my_canister

# Restore from snapshot
dfx canister snapshot load my_canister <snapshot-id>

# Delete a snapshot
dfx canister snapshot delete my_canister <snapshot-id>
```

### Snapshot Considerations

| Aspect | Details |
|--------|---------|
| Storage | Snapshots consume stable memory quota |
| Controllers | Only controllers can take/restore snapshots |
| State | Captures all stable and heap memory |
| Limit | One snapshot per canister at a time |
| Use cases | Pre-upgrade backup, disaster recovery |

---

## Troubleshooting

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `type error: cannot infer type` | Missing type annotation | Add explicit type: `let x : Nat = ...` |
| `type error: shared function has non-shared type` | Passing non-shared type across async | Use only shared types (no mutable arrays, no local functions) |
| `M0038: cannot use X in stable var` | Non-stable type in stable var | Use pre/postupgrade hooks to convert |
| `trap: assertion failed` | `assert(false)` or condition failed | Check preconditions, add error handling |
| `trap: out of cycles` | Canister ran out of cycles | Top up cycles, optimize cycle usage |
| `trap: call_perform failed` | Inter-canister call failed | Wrap in try/catch, check target exists |
| `error: import not found` | Wrong import path | Check path, ensure file exists |

### Debugging Techniques

```motoko
import Debug "mo:base/Debug";

// Print to dfx logs
Debug.print("Value: " # debug_show(myValue));

// Show any value (for debugging only)
let s = debug_show({ complex = [1,2,3]; data = ?#ok });

// Intentional trap with message
Debug.trap("This should never happen: " # debug_show(state));

// Assert with implicit trap
assert(condition);  // Traps with location info if false
```

### Viewing Logs

```bash
# Local replica logs
dfx canister logs my_canister

# Follow logs
dfx canister logs my_canister -f

# On mainnet
dfx canister logs my_canister --network ic
```

### Common Gotchas

**1. Stable variable initialization order**

```motoko
// WRONG - stableB depends on stableA but order not guaranteed
stable var stableA : Nat = 0;
stable var stableB : Nat = stableA + 1;  // Might not work!

// RIGHT - use postupgrade for dependent initialization
stable var stableA : Nat = 0;
stable var stableB : Nat = 0;

system func postupgrade() {
  stableB := stableA + 1;
};
```

**2. Forgot to handle Option/Result**

```motoko
// WRONG - ignores null case
let value = map.get(key);
doSomething(value);  // value is ?T, not T!

// RIGHT - handle the option
switch (map.get(key)) {
  case null { /* handle missing */ };
  case (?v) { doSomething(v) };
};
```

**3. Comparing Principals**

```motoko
// WRONG - using == on Principal doesn't work as expected sometimes
if (caller == admin) { ... }

// RIGHT - use Principal.equal for clarity
import Principal "mo:base/Principal";
if (Principal.equal(caller, admin)) { ... }
```

---

## Enhanced Orthogonal Persistence (EOP) Migration

### Migrating from Legacy to EOP

When upgrading a canister from legacy (classical) persistence to EOP:

1. The old stable data is deserialized from stable memory one last time
2. Data is placed into the new persistent heap layout
3. Future upgrades use fast memory retention (no serialization)

**Important**: Once on EOP, you cannot downgrade to legacy persistence.

### Graph-Copy Stabilization

For large heaps that exceed upgrade instruction limits, use explicit graph-copy stabilization:

```bash
# Step 1: Stabilize before upgrade (can be repeated if timeout)
dfx canister call CANISTER_ID __motoko_stabilize_before_upgrade "()"

# Step 2: Perform the upgrade
dfx deploy CANISTER_ID

# Step 3: Destabilize after upgrade (can be repeated if timeout)
dfx canister call CANISTER_ID __motoko_destabilize_after_upgrade "()"
```

This is only needed when Motoko's internal memory layout changes, which is rare.

### Upgrade Options

The IC provides `wasm_memory_persistence` upgrade option:

| Option | Behavior |
|--------|----------|
| `keep` | Retain Wasm memory (required for EOP) |
| `null` | Classical persistence (replace memory) |
| `replace` | Force memory replacement (data loss risk!) |

dfx handles this automatically, but you can override:

```bash
dfx canister install my_canister --mode upgrade --wasm-memory-persistence keep
```

---

## ExperimentalInternetComputer Module

Access low-level IC features:

```motoko
import IC "mo:base/ExperimentalInternetComputer";

actor {
  // Get instruction count (useful for benchmarking)
  public func countInstructions() : async Nat64 {
    let start = IC.countInstructions();
    // ... do work ...
    IC.countInstructions() - start
  };

  // Performance counter
  public func perfCounter() : async Nat64 {
    IC.performanceCounter(0)  // 0 = instruction counter
  };
}
```

---

## Threshold ECDSA (Cross-Chain Signing)

ICP canisters can sign transactions for Bitcoin, Ethereum, and other chains using threshold ECDSA without exposing private keys.

### Basic Signing

```motoko
import Cycles "mo:base/ExperimentalCycles";
import Blob "mo:base/Blob";

actor {
  // Management canister interface for ECDSA
  type ECDSAPublicKeyReply = { public_key : Blob; chain_code : Blob };
  type SignWithECDSAReply = { signature : Blob };
  type EcdsaKeyId = { curve : { #secp256k1 }; name : Text };

  let ic : actor {
    ecdsa_public_key : {
      canister_id : ?Principal;
      derivation_path : [Blob];
      key_id : EcdsaKeyId;
    } -> async ECDSAPublicKeyReply;

    sign_with_ecdsa : {
      message_hash : Blob;
      derivation_path : [Blob];
      key_id : EcdsaKeyId;
    } -> async SignWithECDSAReply;
  } = actor "aaaaa-aa";

  // Key ID for mainnet: "key_1", for testnets: "dfx_test_key" or "test_key_1"
  let keyId : EcdsaKeyId = { curve = #secp256k1; name = "key_1" };

  // Get public key for this canister
  public func getPublicKey() : async Blob {
    Cycles.add<system>(25_000_000_000);  // Required cycles

    let { public_key } = await ic.ecdsa_public_key({
      canister_id = null;  // Use this canister's ID
      derivation_path = [];
      key_id = keyId;
    });
    public_key
  };

  // Sign a message hash (must be 32 bytes)
  public func signHash(messageHash : Blob) : async Blob {
    assert(messageHash.size() == 32);

    Cycles.add<system>(26_000_000_000);  // Required cycles

    let { signature } = await ic.sign_with_ecdsa({
      message_hash = messageHash;
      derivation_path = [];
      key_id = keyId;
    });
    signature
  };
};
```

### Derivation Paths for Multiple Keys

```motoko
// Use derivation paths to generate multiple keys from one root
public func getAddressKey(userId : Nat) : async Blob {
  Cycles.add<system>(25_000_000_000);

  let userIdBlob = Text.encodeUtf8(Nat.toText(userId));

  let { public_key } = await ic.ecdsa_public_key({
    canister_id = null;
    derivation_path = [userIdBlob];  // Different path = different key
    key_id = keyId;
  });
  public_key
};
```

### Key IDs by Environment

| Environment | Key ID |
|-------------|--------|
| Local (dfx) | `"dfx_test_key"` |
| Mainnet | `"key_1"` |
| Test subnets | `"test_key_1"` |

### Use Cases

| Use Case | How |
|----------|-----|
| Bitcoin transactions | Sign tx hash, broadcast via HTTP outcall |
| Ethereum transactions | Sign tx hash, use with eth_sendRawTransaction |
| Multi-sig wallets | Multiple canisters each sign |
| User-specific keys | Derivation path per user |

For full Bitcoin/Ethereum integration, see the [ckBTC](https://github.com/dfinity/ic/tree/master/rs/bitcoin/ckbtc/minter) and [ckETH](https://github.com/dfinity/ic/tree/master/rs/ethereum/cketh/minter) reference implementations.
