import pytest
from omnisight.safety import validate_action

def test_valid_navigation():
    validate_action({"action":"navigate","url":"https://example.com"})

def test_reject_invalid_scheme():
    with pytest.raises(ValueError):
        validate_action({"action":"navigate","url":"file:///etc/passwd"})

def test_reject_unknown_action():
    with pytest.raises(ValueError):
        validate_action({"action":"execute_python","code":"print(1)"})

def test_fill_requires_value():
    with pytest.raises(ValueError):
        validate_action({"action":"fill","target":"Name"})
