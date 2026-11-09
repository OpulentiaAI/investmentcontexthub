---
type: guide.gotcha
goal: "Define a UI component contract and implement it through a component set."
rule: "Name the contract for its custom-element tag, and verify the implementation as well as the generated consumer types."
example:
---

# A component contract names its tag

Name a [[ui-component::component-contract:example]] subtype for its custom-element tag.
Its fields describe input properties.
Typed metadata describes:

- Events
- Slots
- States
- Parts

Inspect [[au-button::au-component-catalog:example]] for a concrete contract.

**Supply the implementation through a set**

A component set registers the element and implements its properties and interactions.
The type definition does not synthesize that behavior.
[[component-set::component-contract:example]] defines set discovery.

**Keep the interface portable**

Choose the contract independently of a rendering library when consumers should survive a set change.
Put framework elements in content slots instead of treating them as portable data properties.
Align event names and behavior with the declared interface.

**Check typed and bare consumers**

Generated types help consumers using them catch incompatible properties at compile time.
They do not validate arbitrary DOM changes.
They also do not establish:

- Accessibility
- Event behavior
- Implementation correctness

A bare element still needs sensible runtime behavior.

Compile a typed consumer and render a bare element.
Exercise the implementation:

- Properties and emitted events
- Keyboard behavior
- Slots

If several sets implement the contract, use the same consumer against each.
A resolving type and a registered tag establish different parts of the result.
