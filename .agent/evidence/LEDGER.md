# Production Readiness Ledger
## Functional Readiness
layer1: 1 (see layer1_cli: 0)
layer2: 1
layer3: 1
layer4: 1
layer5: 1
todos_fixed: 1 (empty grep = no TODOs)
layer1_cli: 0
layer2_cli: 0
layer3_cli: 0
layer4_cli: 0
layer5_cli: 0
todos_fixed: 1
## Test Readiness
ruff_check: 0
ruff_format: 0
mypy: 1 (see mypy_fixed6: 0)
pytest_unit: 2 (see pytest_unit_fixed: 0)
pytest_integration: 2 (see pytest_integration_fixed: 0)
pytest_property: 2 (see pytest_property_fixed: 0)
pytest_e2e: 2 (see pytest_e2e_fixed: 0)
pytest_interop: 0
pytest_perf: 4 (see pytest_perf_fixed: 0)
pytest_log_redaction: 2 (see pytest_log_redaction_fixed: 0)
pytest_unit_fixed: 0
pytest_integration_fixed: 0
pytest_property_fixed: 0
pytest_e2e_fixed: 0
pytest_interop_fixed: 0
pytest_perf_fixed: 0
pytest_log_redaction_fixed: 0
mypy_fixed: 1
mypy_fixed2: 1
mypy_fixed3: 1
mypy_fixed4: 1
mypy_fixed5: 1
mypy_fixed6: 0
## Security Readiness
security_check: 126
pip_audit: 1
dependency_audit: 126
smoke_placeholder_fail_expected: 1
smoke_liboqs: 0
security_check_fixed: 0
dependency_audit_fixed: 1
dependency_audit_fixed2: 0
pip_audit_fixed: 0
## Observability & Data Readiness
node_health: 0
dashboards: 0
promtool: NOT_RUNNABLE_ENV(promtool missing)
audit_db_migrate: 1
audit_db_migrate_fixed: 0
audit_db_migrate_fixed_check: 0
## Final Gates
verify_sh: 0
production_readiness_check: 1 (see production_readiness_check_fixed3: 1)
production_readiness_check_fixed: 1
production_readiness_check_fixed2: 1
production_readiness_check_fixed3: 1
