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
