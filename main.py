import asyncio
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from dotenv import load_dotenv

load_dotenv(override=True)


class SimpleAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("Simple")

    @message_handler
    async def on_my_message(self, message: TextMessage, ctx: MessageContext) -> TextMessage:
        return TextMessage(
            content=f"This is {self.id.type}-{self.id.key}. You said '{message.content}' and I disagree.",
            source="agent"
        )


class MyLLMAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("LLMAgent")
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
        self._delegate = AssistantAgent("LLMAgent", model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: TextMessage, ctx: MessageContext) -> TextMessage:
        print(f"{self.id.type} received message: {message.content}")
        response = await self._delegate.on_messages([message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            reply = response.chat_message.content
            print(f"{self.id.type} responded: {reply}")
            return TextMessage(content=reply, source="agent")
        return TextMessage(
            content=f"Got unexpected message type: {type(response.chat_message)}",
            source="agent"
        )


JUDGE = "You are judging a game of rock, paper, scissors. The players have made these choices:\n"


class RockPaperScissorsAgent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: TextMessage, ctx: MessageContext) -> TextMessage:
        instruction = "You are playing rock, paper, scissors. Respond only with rock, paper, or scissors."
        inner_1 = AgentId("player1", "default")
        inner_2 = AgentId("player2", "default")

        response1 = await self.send_message(TextMessage(content=instruction, source="user"), inner_1)
        response2 = await self.send_message(TextMessage(content=instruction, source="user"), inner_2)

        result = f"Player 1: {response1.content}\nPlayer 2: {response2.content}\n"
        judgement = f"{JUDGE}{result}Who wins?"

        response = await self._delegate.on_messages([TextMessage(content=judgement, source="user")], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return TextMessage(content=result + response.chat_message.content, source="agent")
        return TextMessage(content="Unexpected response type", source="agent")


class Player1Agent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: TextMessage, ctx: MessageContext) -> TextMessage:
        response = await self._delegate.on_messages([message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return TextMessage(content=response.chat_message.content, source="agent")
        return TextMessage(content="Unexpected response type", source="agent")


class Player2Agent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OllamaChatCompletionClient(model="llama3.2", options={"temperature": 0.7})
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: TextMessage, ctx: MessageContext) -> TextMessage:
        response = await self._delegate.on_messages([message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return TextMessage(content=response.chat_message.content, source="agent")
        return TextMessage(content="Unexpected response type", source="agent")


async def main():
    runtime = SingleThreadedAgentRuntime()
    await Player1Agent.register(runtime, "player1", lambda: Player1Agent("player1"))
    await Player2Agent.register(runtime, "player2", lambda: Player2Agent("player2"))
    await RockPaperScissorsAgent.register(runtime, "rock_paper_scissors", lambda: RockPaperScissorsAgent("rock_paper_scissors"))
    runtime.start()

    agent_id = AgentId("rock_paper_scissors", "default")
    message = TextMessage(content="go", source="user")
    response = await runtime.send_message(message, agent_id)
    print(response.content)

    await runtime.stop()
    await runtime.close()


if __name__ == "__main__":
    asyncio.run(main())
