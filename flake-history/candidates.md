# Flake candidates — 2026-07-16

Analyzed 3 run record(s) from run(s) 29521565953 · 261 test(s) tracked

## Quarantine candidates (3)

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[chromium]`

| browser | evidence |
|---|---|
| chromium | 7 flake incident(s) in last 7 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912), [run 29094144216](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29094144216), [run 29097078182](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29097078182), [run 29204222187](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29204222187), [run 29521565953](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29521565953) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-15")
```

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[firefox]`

| browser | evidence |
|---|---|
| firefox | 7 flake incident(s) in last 7 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912), [run 29094144216](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29094144216), [run 29097078182](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29097078182), [run 29204222187](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29204222187), [run 29521565953](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29521565953) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-15")
```

### `tests/framework/test_flaky_demo.py::test_deterministic_flaky_demo[webkit]`

| browser | evidence |
|---|---|
| webkit | 7 flake incident(s) in last 7 runs: [run 29031207512](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29031207512), [run 29032674223](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29032674223), [run 29035300912](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29035300912), [run 29094144216](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29094144216), [run 29097078182](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29097078182), [run 29204222187](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29204222187), [run 29521565953](https://github.com/summerduck/fintech-playwright-quality/actions/runs/29521565953) |

Suggested marker (fill in the ticket):

```python
@pytest.mark.quarantine(reason="TICKET-???: <root cause>", expires="2026-08-15")
```
