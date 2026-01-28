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
