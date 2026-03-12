import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from server.core.server import Server
from server.network.websocket_server import ClientConnection

@pytest.fixture
def server():
    # Setup test server without opening actual ports
    server = Server(host="127.0.0.1", port=0, db_path=":memory:")
    server.db.connect()

    # We need an AuthManager
    from server.auth.auth import AuthManager
    server._auth = AuthManager(server.db)

    return server

@pytest.fixture
def mock_client():
    client = MagicMock(spec=ClientConnection)
    client.ip_address = "127.0.0.1"
    client.send = AsyncMock()
    client.close = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_request_password_reset_no_smtp(server, mock_client):
    """Test that requesting a password reset fails cleanly if SMTP is not configured."""
    packet = {
        "type": "request_password_reset",
        "email": "test@example.com",
        "locale": "en"
    }

    await server._handle_request_password_reset(mock_client, packet)

    # Verify the client got the right error message
    mock_client.send.assert_called_once()
    sent_packet = mock_client.send.call_args[0][0]

    assert sent_packet["type"] == "request_password_reset_response"
    assert sent_packet["status"] == "error"
    assert sent_packet["error"] == "smtp_not_configured"

@pytest.mark.asyncio
async def test_request_password_reset_user_not_found(server, mock_client):
    """Test that requesting a password reset returns a generic success if the email doesn't exist to prevent enumeration."""
    # First configure SMTP so it doesn't fail early
    server.db.update_smtp_config("smtp.test.com", 587, "user", "pass", "test@test.com", "Test", "tls")

    packet = {
        "type": "request_password_reset",
        "email": "doesntexist@example.com",
        "locale": "en"
    }

    await server._handle_request_password_reset(mock_client, packet)

    mock_client.send.assert_called_once()
    sent_packet = mock_client.send.call_args[0][0]

    assert sent_packet["type"] == "request_password_reset_response"
    assert sent_packet["status"] == "success"


@pytest.mark.asyncio
async def test_request_password_reset_success_flow(server, mock_client):
    """Test the full success flow of generating a token and sending an email."""
    # Configure SMTP
    server.db.update_smtp_config("smtp.test.com", 587, "user", "pass", "test@test.com", "Test", "tls")

    # Create a user
    server._auth.register("testuser", "Password123", email="test@example.com")
    user = server.db.get_user("testuser")

    packet = {
        "type": "request_password_reset",
        "email": "test@example.com",
        "locale": "en"
    }

    # Mock the mailer to avoid actual network requests during testing
    with patch('server.core.smtp_mailer.SmtpMailer.send_email', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = (True, "")

        await server._handle_request_password_reset(mock_client, packet)

        # Verify email was "sent"
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        assert args[1] == "test@example.com" # to_email

    # Verify client got success response
    mock_client.send.assert_called_once()
    sent_packet = mock_client.send.call_args[0][0]
    assert sent_packet["type"] == "request_password_reset_response"
    assert sent_packet["status"] == "success"

    # Verify token exists in database
    token_record = server.db.get_password_reset_token(user.uuid)
    assert token_record is not None


@pytest.mark.asyncio
async def test_submit_reset_code_success(server, mock_client):
    """Test submitting a valid code successfully resets the password."""
    # Create user
    server._auth.register("testuser", "OldPassword123", email="test@example.com")
    user = server.db.get_user("testuser")

    # Generate token
    token = server._auth.generate_reset_token(user.uuid)

    packet = {
        "type": "submit_reset_code",
        "email": "test@example.com",
        "code": token,
        "new_password": "NewPassword456",
        "locale": "en"
    }

    await server._handle_submit_reset_code(mock_client, packet)

    # Verify client success message
    mock_client.send.assert_called_once()
    sent_packet = mock_client.send.call_args[0][0]
    assert sent_packet["type"] == "submit_reset_code_response"
    assert sent_packet["status"] == "success"

    # Verify password was updated
    assert server._auth.authenticate("testuser", "NewPassword456") is True
    assert server._auth.authenticate("testuser", "OldPassword123") is False

    # Verify token was cleared
    token_record = server.db.get_password_reset_token(user.uuid)
    assert token_record is None
