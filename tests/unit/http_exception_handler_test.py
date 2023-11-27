from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request

from main import http_exception_handler
from utils import Logger


@pytest.mark.asyncio
async def test_http_exception_handler():
    scope = {
        'type': 'http',
    }

    mock_logger = Mock(spec=Logger)
    mock_logger.log.return_value = None

    mock_request = Request(scope=scope)
    mock_http_exception = HTTPException(detail="logger", status_code=500)

    with patch('main.Logger', return_value=mock_logger):
        response = await http_exception_handler(mock_request, mock_http_exception)

    assert response.status_code == 500
    assert response.body == b'{"message":"Internal server error"}'
    assert mock_logger.log.call_count == 1
