import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import io
import redis
from coaiapy.coaiacli import fetch_key_val

# Mock Redis fixture
@pytest.fixture
def mock_redis(monkeypatch):
    mock_redis_instance = MagicMock()
    monkeypatch.setattr('redis.Redis', lambda *args, **kwargs: mock_redis_instance)
    return mock_redis_instance

# Mock broken Redis fixture
@pytest.fixture
def mock_broken_redis(monkeypatch):
    mock_redis_instance = MagicMock()
    mock_redis_instance.get.side_effect = redis.ConnectionError
    monkeypatch.setattr('redis.Redis', lambda *args, **kwargs: mock_redis_instance)
    return mock_redis_instance

def test_fetch_stdout_key_found(mock_redis):
    mock_redis.get.return_value = b'This is a memory snippet.'
    with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
            patch('coaiapy.coaiamodule._newjtaler') as mock_newjtaler:
        mock_newjtaler.return_value = mock_redis
        fetch_key_val('mykey')
        assert mock_stdout.getvalue().strip() == 'This is a memory snippet.'

def test_fetch_output_file_key_found(mock_redis):
    mock_redis.get.return_value = b'This is a memory snippet.'
    output_file = 'memory.txt'
    fetch_key_val('mykey', output_file)
    with open(output_file, 'r') as file:
        assert file.read().strip() == 'This is a memory snippet.'
    os.remove(output_file)

def test_fetch_key_not_found_exits_1(mock_redis):
    mock_redis.get.return_value = None
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        fetch_key_val('mykey')
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

def test_fetch_redis_down_exits_2(mock_broken_redis):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        fetch_key_val('mykey')
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
