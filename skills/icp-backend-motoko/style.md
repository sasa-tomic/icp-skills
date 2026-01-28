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
