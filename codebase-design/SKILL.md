---
name: codebase-design
description: >
  Vocabulary and principles for deep modules: much behaviour behind a small interface at a clean
  seam. Use when designing or reshaping a module's interface, deciding where a seam goes, making
  code more testable, or surveying a codebase for deepening opportunities.
---

# Codebase design

Agents accelerate entropy: they add code faster than design keeps up. The counter is **deep
modules** (Ousterhout, *A Philosophy of Software Design*): a lot of behaviour behind a small
interface, so callers learn little and changes stay local.

## Vocabulary

Use these terms exactly.

- **Module**: anything with an interface and an implementation, at any scale: a function, a class,
  a Python package, a Rust crate.
- **Interface**: everything a caller must know to use it correctly: signature, invariants, order
  of calls, errors raised, configuration, performance.
- **Depth**: behaviour available per unit of interface learnt. Deep: small interface, much
  behaviour. Shallow: the interface is nearly as complex as what it hides.
- **Seam** (Feathers): a place where behaviour can be changed without editing that place; where an
  interface lives.
- **Adapter**: a concrete thing that fills a seam (a Postgres repository, an in-memory fake).
- **Leverage**: what callers gain from depth. **Locality**: what maintainers gain: change, bugs
  and knowledge concentrated in one place.

## Principles

- **Depth is a property of the interface.** A deep module can contain small parts; they are not
  part of its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a
  pass-through. If it reappears in every caller, it was earning its place.
- **The interface is the test surface.** If a test needs to reach past it, the module is the wrong
  shape.
- **One adapter is a hypothetical seam; two make it real.** Add a seam (a `Protocol`, an ABC, a
  trait) only when something actually varies across it, such as production and test.
- **Accept dependencies; do not construct them.** Pass the clock, the client, the store in.

```python
class Payments(Protocol):
    def charge(self, amount: Decimal) -> Receipt: ...

def checkout(cart: Cart, payments: Payments) -> Order: ...
```

```rust
pub trait Payments { fn charge(&self, amount: Money) -> Result<Receipt, PaymentError>; }
pub fn checkout(cart: &Cart, payments: &impl Payments) -> Result<Order, CheckoutError> { .. }
```

## When designing an interface

Ask: can there be fewer functions? Simpler parameters? Can more be hidden inside? Then design it
twice: sketch two radically different interfaces for the same module, compare what each makes
callers learn, and pick or combine.

## Surveying a codebase

When asked to find deepening opportunities, read the code and list candidates, each with: the
modules involved, the symptom (pass-through layers, the same knowledge in several callers, tests
that mock internals, a bug that could not be locked down by a test), the proposed deeper module and
its interface, and what it would make easier. Rank by leverage. Take the one the user picks into
`/grill-docs`.
