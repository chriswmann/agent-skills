---
name: tdd
description: >
  Test-driven development with a red-green loop, one vertical slice at a time. Use when building
  a feature or fixing a bug test-first, when the user mentions red-green-refactor, or when
  writing or judging tests.
---

# Test-driven development

Red, then green, one slice at a time, with tests worth keeping. Read `GLOSSARY.md` if it exists so
test names use the project's language.

## Agree the seams first

A **seam** is the public interface a test exercises without reaching inside. Before writing any
test, list the seams you intend to test, each with a line on what it catches and what it misses,
and confirm them with the user (or take them from the spec). Test only at agreed seams. If the
shape of the interface is itself in question, consult `codebase-design`.

## The loop

1. **Red.** Write one test for the next behaviour. Run it and watch it fail for the reason you
   expect: an assertion, not an import error.
2. **Green.** Write the least code that makes it pass. Nothing for tests you have not written.
3. **Repeat.** Each test is a **tracer bullet**: let what the last cycle taught you choose the
   next test.

Refactoring happens after the loop, under green tests, or in review. Writing every test first and
every implementation after is horizontal slicing: the tests end up checking an imagined shape
rather than behaviour.

## What a good test is

A good test states a behaviour a caller cares about, through the public interface, and survives a
rewrite of the internals.

```python
# Good: behaviour through the interface
def test_checkout_confirms_order_for_valid_cart():
    cart = Cart()
    cart.add(Product("book", price=Decimal("12.50")))
    assert checkout(cart, FakePayments()).status is Status.CONFIRMED

# Bad: verifies through a side channel
def test_create_user_inserts_row(db):
    create_user("alice")
    assert db.execute("SELECT 1 FROM users WHERE name = 'alice'").fetchone()

# Good: the same behaviour through the interface
def test_created_user_can_be_fetched():
    user = create_user("alice")
    assert get_user(user.id).name == "alice"
```

```rust
// Good: expected value is an independent literal
#[test]
fn total_sums_line_items() {
    assert_eq!(total(&[item(10), item(5)]), 15);
}
```

Warning signs:

- **Coupled to implementation**: mocks your own modules, tests private functions, asserts call
  counts or order. The test breaks on a refactor that did not change behaviour.
- **Tautological**: the expected value is computed the same way the code computes it
  (`assert total(xs) == sum(x.price for x in xs)`), so it can never disagree. Use a known literal,
  a worked example or the spec.
- **Named for how, not what**: `test_calls_process` instead of `test_rejects_expired_card`.

## Mocking

Replace only what you do not control: external APIs, the clock, randomness, sometimes the network
or file system. Use real collaborators for everything you own.

- Pass boundaries in rather than constructing them inside (`checkout(cart, payments)`, not
  `StripeClient()` inside `checkout`). In Rust, a trait or generic parameter at the boundary.
- Prefer a small fake with one method per operation (`get_user`, `create_order`) to a generic
  `request(method, path)` mock full of conditionals.
- Python: prefer a hand-written fake or `pytest`'s `monkeypatch` at the boundary to
  `unittest.mock.patch` of internals. Freeze time by injecting a clock.
