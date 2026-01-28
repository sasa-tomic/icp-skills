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
