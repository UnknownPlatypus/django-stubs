My hard requirements (any solution not supporting that is not viable) are:
- `Field()` should correctly understand `null=False` from the runtime default in `__init__`
- `CustomField()` should correctly understand `null=False` from the runtime default in `__init__`

My other requirements (best effort, should work easily in mypy with little to no changes, should work in other typechecker with code changes allowed):
- Bare `Field` annotation should be inferred as `Field[Any, Any, Any]` to avoid breakage in user code
- `Field[A, B]` should be `Field[A, B, Any]` to avoid breakage in user code
- Custom `Field` typing should work out of the box with minimal changes
