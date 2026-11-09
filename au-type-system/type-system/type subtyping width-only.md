How a [[type-def]] subtype relates to its parent,
through [[type-def extends]].

# Properties

## Additions only
A subtype CAN add new fields the parent doesn't declare.

A subtype CANNOT:
- remove an inherited field.
- redeclare a field the parent already carries.
- tighten, relax, or reshape an inherited field.

A redeclaration is a load error:
- [[spec - diagnostic codes^field-redeclaration]].

## Single source
The parent's declaration is the single source for each field.

A leaf's contract therefore always implies its parent's.
This is read-direction Liskov.
The write direction is only operational, see [[type write model]].

## Sealed branches are subtypable
A non-sealed branch of a [[type-def sealed]] family is a normal type.
It may be subtyped further, like any other.
The subtype is a new leaf, reaching the sealed parent through its branch.

This is what keeps sealed dispatch sound.
- a consumer branches by closure membership in a listed branch.
- [[#Single source]] Liskov makes treating the subtype as its branch correct.
- see [[type-def sealed]].
