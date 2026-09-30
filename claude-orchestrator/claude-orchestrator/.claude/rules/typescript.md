# TypeScript rules (all three repos)

- `strict` on, plus `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` where the repo allows. Do not loosen `tsconfig` to make something compile.
- No `any`, no `@ts-ignore`/`@ts-expect-error` without a one-line reason and ticket. Use `unknown` and narrow; never cast (`as`) across a trust boundary. Validate with the schema instead.
- Types for data that crosses a boundary come from the generated contracts, not from hand-written interfaces.
- Prefer discriminated unions and exhaustive `switch` with a `never` check over flags and optional fields.
- Errors: throw typed errors (domain error classes or Temporal `ApplicationFailure`), never strings. Do not swallow errors; do not catch just to log and continue unless the failure is genuinely non-critical and stated.
- Async: no floating promises (`@typescript-eslint/no-floating-promises`), explicit timeouts on I/O, no `await` in unbounded loops over large sets.
- Dates: store and transmit UTC ISO-8601; convert at the UI edge. Money uses integer minor units or a decimal type, never floats.
- IDs: opaque strings (UUID v7 preferred) with branded types when mixing several ID kinds.
- Modules: small, single-purpose, no circular imports, no barrel files that hide cycles. Named exports.
- Comments explain why, not what. Delete dead code instead of commenting it out.
- Tests sit next to code or in the repo's test folder per `testing.md`; naming is behaviour-based ("rejects expired token").
