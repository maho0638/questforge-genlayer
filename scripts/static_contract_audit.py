"""Auxiliary Python AST audit; NEVER claim this is the official genvm-lint."""
import ast
from pathlib import Path

paths = sorted(Path('contracts').glob('*.py'))
assert len(paths) == 1, f'Expected exactly one contract source, got {paths}'
for path in paths:
    t = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    contract_classes = [c for c in t.body if isinstance(c, ast.ClassDef)
                        and any(isinstance(b, ast.Attribute) and b.attr == 'Contract'
                        for b in c.bases)]
    assert len(contract_classes) == 1, 'Exactly one gl.Contract expected'
    methods = contract_classes[0].body
    public = [m for m in methods if isinstance(m, ast.FunctionDef)
              and any(isinstance(d, ast.Attribute) and isinstance(d.value, ast.Attribute)
                          and d.value.attr == 'public'
                          and d.attr in ('view', 'write') for d in m.decorator_list)]
    assert public, 'No public methods'
    assert all(m.returns is not None for m in public), 'Missing return annotation'
    assert all(a.annotation is not None for m in public for a in m.args.args[1:]), 'Missing parameter annotation'
    calls = [node for node in ast.walk(t) if isinstance(node, ast.Call)]
    assert any(isinstance(x.func, ast.Attribute) and x.func.attr == 'run_nondet_unsafe' for x in calls), 'No consensus block'
    for c in contract_classes:
        assert any(m.name == '__init__' for m in c.body if isinstance(m, ast.FunctionDef))
    print(f'PASS supplementary AST audit: {path} ({len(public)} public functions).')
