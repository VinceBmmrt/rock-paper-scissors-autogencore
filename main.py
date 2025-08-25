import asyncio
from dataclasses import dataclass
from typing_extensions import runtime
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core import SingleThreadedAgentRuntime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from autogen_ext.models.ollama import OllamaChatCompletionClient
load_dotenv(override=True)


@dataclass
class Message:
    content: str


class SimpleAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("Simple")
    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> Message:
        return Message(
            content=f"This is {self.id.type}-{self.id.key}. "
                    f"You said '{message.content}' and I disagree."
        )
    

class MyLLMAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("LLMAgent")
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
        self._delegate = AssistantAgent("LLMAgent", model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        print(f"{self.id.type} received message: {message.content}")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            reply = response.chat_message.content
            print(f"{self.id.type} responded: {reply}")
            return Message(content=reply)
        return Message(
    content=f"Got unexpected message type: {type(response.chat_message)}"
)
    
JUDGE = "You are judging a game of rock, paper, scissors. The players have made these choices:\n"    
    
class RockPaperScissorsAgent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        instruction = "You are playing rock, paper, scissors. Respond only with the one word, one of the following: rock, paper, or scissors."
        message = Message(content=instruction)
        inner_1 = AgentId("player1", "default")
        inner_2 = AgentId("player2", "default")
        response1 = await self.send_message(message, inner_1)
        response2 = await self.send_message(message, inner_2)
        result = f"Player 1: {response1.content}\nPlayer 2: {response2.content}\n"
        judgement = f"{JUDGE}{result}Who wins?"
        message = Message(content=judgement)
        response = await self._delegate.on_messages([message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return Message(content=result + response.chat_message.content)
        return Message(content="Unexpected response type")

class Player1Agent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return Message(content=response.chat_message.content)
        return Message(content="Unexpected response type")

class Player2Agent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OllamaChatCompletionClient(model="llama3.2", options={"temperature": 0.7},)
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        if isinstance(response.chat_message, TextMessage):
            return Message(content=response.chat_message.content)
        return Message(content="Unexpected response type")

async def main():
    runtime = SingleThreadedAgentRuntime()
    await Player1Agent.register(runtime, "player1", lambda: Player1Agent("player1"))
    await Player2Agent.register(runtime, "player2", lambda: Player2Agent("player2"))
    await RockPaperScissorsAgent.register(runtime, "rock_paper_scissors", lambda: RockPaperScissorsAgent("rock_paper_scissors"))
    runtime.start()
    


    agent_id = AgentId("simple_agent", "default")
    agent_id = AgentId("rock_paper_scissors", "default")
    message = Message(content="go")
    response = await runtime.send_message(message, agent_id)
    print(response.content)


    await runtime.stop()
    await runtime.close()

if __name__ == "__main__":
    asyncio.run(main())
