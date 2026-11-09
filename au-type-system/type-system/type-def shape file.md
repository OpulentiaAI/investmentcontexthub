The built-in whole-file reference target.
One of the [[type-def field shape]].

# Properties

## Whole file by existence
`file*` resolves to any repo file by existence.
No type-closure check.

It references the whole file, never a part of it.
- a `^block-id` is rejected, a file asset has no addressable sub-blocks.
- a `#head` anchor is rejected, the same reason.
- [[type reference]] carries the value form and the rejection.

Use for assets the type system doesn't model:
- PDFs
- images
- code
- binaries

## The narrowing of `any*`
[[type-def shape any]] `any*` references any node, a file or a typed block or an addressable inline record, with no closure check.
`file*` is its whole-file narrowing.
- `any*` accepts every `file*` value, plus the block-ids `file*` rejects.
- so `any*` subsumes `file*`, a `<file* | any*>` slot-union fires [[spec - diagnostic codes^subsumption-in-slot-union]].

## Reserved name
`file` is reserved.

A user [[type-def]] cannot claim it:
- [[spec - diagnostic codes^reserved-type-name]].

## Reference only
A file has no inline form, so only `file*` is meaningful.

Bare `file` and `file&` are a load error:
- [[spec - diagnostic codes^shape-syntax-error]].

Lists (`file*[]`, `file*[+]`) and compound operands are fine.

# Structure
```yaml
fields:
  myAsset: file*
  myAssets: file*[]
```
