# Flake candidates — 2026-07-09

Analyzed 3 run record(s) from run(s) 29035300912 · 261 test(s) tracked

## Quarantine candidates (3)

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[chromium]`

| browser | evidence |
|---|---|
| chromium | 3 flake incident(s) in last 3 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-08")
```

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[firefox]`

| browser | evidence |
|---|---|
| firefox | 3 flake incident(s) in last 3 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-08")
```

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[webkit]`

| browser | evidence |
|---|---|
| webkit | 3 flake incident(s) in last 3 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-08")
```
