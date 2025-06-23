from unittest.mock import AsyncMock

# import grpc
import pytest

from a2a import types
# from a2a.grpc import a2a_pb2
# from a2a.server.request_handlers import GrpcHandler, RequestHandler
from a2a.utils.errors import ServerError


# --- Fixtures ---


@pytest.fixture
def mock_request_handler() -> AsyncMock:
    return AsyncMock(spec=RequestHandler)


@pytest.fixture
def mock_grpc_context() -> AsyncMock:
    context = AsyncMock(spec=grpc.aio.ServicerContext)
    context.abort = AsyncMock()
    return context


@pytest.fixture
def sample_agent_card() -> types.AgentCard:
    return types.AgentCard(
        name='Test Agent',
        description='A test agent',
        url='http://localhost',
        version='1.0.0',
        capabilities=types.AgentCapabilities(
            streaming=True, pushNotifications=True
        ),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        skills=[],
    )


@pytest.fixture
def grpc_handler(
    mock_request_handler: AsyncMock, sample_agent_card: types.AgentCard
# ) -> GrpcHandler:
#     return GrpcHandler(
        agent_card=sample_agent_card, request_handler=mock_request_handler
    )


# --- Test Cases ---


@pytest.mark.asyncio
async def test_send_message_success(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test successful SendMessage call."""
#     request_proto = a2a_pb2.SendMessageRequest(
#         request=a2a_pb2.Message(message_id='msg-1')
    )
    response_model = types.Task(
        id='task-1',
        contextId='ctx-1',
        status=types.TaskStatus(state=types.TaskState.completed),
    )
    mock_request_handler.on_message_send.return_value = response_model

    response = await grpc_handler.SendMessage(request_proto, mock_grpc_context)

    mock_request_handler.on_message_send.assert_awaited_once()
#     assert isinstance(response, a2a_pb2.SendMessageResponse)
    assert response.HasField('task')
    assert response.task.id == 'task-1'


@pytest.mark.asyncio
async def test_send_message_server_error(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test SendMessage call when handler raises a ServerError."""
#     request_proto = a2a_pb2.SendMessageRequest()
    error = ServerError(error=types.InvalidParamsError(message='Bad params'))
    mock_request_handler.on_message_send.side_effect = error

    await grpc_handler.SendMessage(request_proto, mock_grpc_context)

    mock_grpc_context.abort.assert_awaited_once_with(
        grpc.StatusCode.INVALID_ARGUMENT, 'InvalidParamsError: Bad params'
    )


@pytest.mark.asyncio
async def test_get_task_success(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test successful GetTask call."""
#     request_proto = a2a_pb2.GetTaskRequest(name='tasks/task-1')
    response_model = types.Task(
        id='task-1',
        contextId='ctx-1',
        status=types.TaskStatus(state=types.TaskState.working),
    )
    mock_request_handler.on_get_task.return_value = response_model

    response = await grpc_handler.GetTask(request_proto, mock_grpc_context)

    mock_request_handler.on_get_task.assert_awaited_once()
#     assert isinstance(response, a2a_pb2.Task)
    assert response.id == 'task-1'


@pytest.mark.asyncio
async def test_get_task_not_found(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test GetTask call when task is not found."""
#     request_proto = a2a_pb2.GetTaskRequest(name='tasks/task-1')
    mock_request_handler.on_get_task.return_value = None

    await grpc_handler.GetTask(request_proto, mock_grpc_context)

    mock_grpc_context.abort.assert_awaited_once_with(
        grpc.StatusCode.NOT_FOUND, 'TaskNotFoundError: Task not found'
    )


@pytest.mark.asyncio
async def test_cancel_task_server_error(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test CancelTask call when handler raises ServerError."""
#     request_proto = a2a_pb2.CancelTaskRequest(name='tasks/task-1')
    error = ServerError(error=types.TaskNotCancelableError())
    mock_request_handler.on_cancel_task.side_effect = error

    await grpc_handler.CancelTask(request_proto, mock_grpc_context)

    mock_grpc_context.abort.assert_awaited_once_with(
        grpc.StatusCode.UNIMPLEMENTED,
        'TaskNotCancelableError: Task cannot be canceled',
    )


@pytest.mark.asyncio
async def test_send_streaming_message(
#     grpc_handler: GrpcHandler,
    mock_request_handler: AsyncMock,
    mock_grpc_context: AsyncMock,
):
    """Test successful SendStreamingMessage call."""

    async def mock_stream():
        yield types.Task(
            id='task-1',
            contextId='ctx-1',
            status=types.TaskStatus(state=types.TaskState.working),
        )

    mock_request_handler.on_message_send_stream.return_value = mock_stream()
#     request_proto = a2a_pb2.SendMessageRequest()

    results = [
        result
        async for result in grpc_handler.SendStreamingMessage(
            request_proto, mock_grpc_context
        )
    ]

    assert len(results) == 1
    assert results[0].HasField('task')
    assert results[0].task.id == 'task-1'


@pytest.mark.asyncio
async def test_get_agent_card(
#     grpc_handler: GrpcHandler,
    sample_agent_card: types.AgentCard,
    mock_grpc_context: AsyncMock,
):
    """Test GetAgentCard call."""
#     request_proto = a2a_pb2.GetAgentCardRequest()
    response = await grpc_handler.GetAgentCard(request_proto, mock_grpc_context)

    assert response.name == sample_agent_card.name
    assert response.version == sample_agent_card.version
