A built-in scalar [[type-def field shape]].

# Properties

## Reserved names
The primitive names cannot be claimed by a user [[type-def]].
See [[type-def legal names]].

## No reference
A primitive is not a file.

The `*` and `&` reference suffixes are a load error:
- [[spec - diagnostic codes^shape-syntax-error]].

# Lists
A list suffix `[]` or `[+]` is fine.

## Url disambiguation
`Url` matches `^https?://`.

That prefix doubles as the discriminator in a union like `<String | Url>`.

# Structure
The built-in primitives:
- `String`
  - UTF-8 text.
- `Number`
  - integer or float.
- `Boolean`
  - `true` or `false`.
- `Date`
  - ISO 8601 date, `YYYY-MM-DD`.
- `DateTime`
  - UTC-only, colon-free, `YYYY-MM-DDThhmmssZ`.
  - one strict form, always `Z`, no offsets, no fractional seconds.
- `Url`
  - HTTP/HTTPS, matches `^https?://`.

```yaml
fields:
  myText: String
  myCount: Number
  myFlag: Boolean
  myDay: Date
  myMoment: DateTime
  myLink: Url
```
