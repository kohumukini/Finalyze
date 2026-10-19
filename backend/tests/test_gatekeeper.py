import json
import re

import pytest
from pydantic import ValidationError

from types import SimpleNamespace

from backend.core.schema import RAG, Direct, Message, Refuse
from backend.services import llm

class FakeGroq: 
    def __init__(self, content: str | None, finish_reason: str = "stop"): 
        self.content = content
        self.finish_reason = finish_reason
        self.calls: list[dict] = [] 
        self.chat = SimpleNamespace(completions = SimpleNamespace(create = self._create))
        
    def _create(self, **kwargs): 
        self.calls.append(kwargs)
        choice = SimpleNamespace(
            message = SimpleNamespace(content = self.content),
            finish_reason = self.finish_reason
        )
        
        return SimpleNamespace(choices = [choice])
    
@pytest.fixture
def fake_groq(monkeypatch): 
    def install(content: str | None, finish_reason: str = "stop") -> FakeGroq: 
        fake = FakeGroq(content, finish_reason)
        monkeypatch.setattr(llm, "_get_groq_client", lambda: fake)
        return fake
    
    return install

CATALOG = ["catan.txt", "clue.txt"]


def _ask(query: str = "how do I set up catan?", history: list[Message] | None = None, catalog: list[str] = CATALOG):
    return llm.gatekeeper(query, history=history or [], catalog=catalog)


# --- What gatekeeper() returns ---

@pytest.mark.parametrize(
    ("payload", "model"),
    [
        ({"route": "refuse", "message": "I can only help with the games."}, Refuse),
        ({"route": "direct", "message": "Hi! Ask me about Catan or Clue."}, Direct),
        ({"route": "rag", "main_query": "catan setup", "sub_queries": []}, RAG),
    ],
)
def test_each_route_is_returned(fake_groq, payload, model):
    fake_groq(json.dumps(payload))
    assert isinstance(_ask(), model)


@pytest.mark.parametrize("content", ["Sure, route is rag", None])
def test_unparseable_output_raises(fake_groq, content):
    fake_groq(content)
    with pytest.raises(ValidationError):
        _ask()


def test_truncated_output_raises(fake_groq):
    fake_groq('{"route": "ra', finish_reason="length")
    with pytest.raises(RuntimeError, match="max_tokens"):
        _ask()


def test_empty_catalog_fails_before_calling_the_llm(fake_groq):
    fake = fake_groq("{}")
    with pytest.raises(RuntimeError, match="catalog is empty"):
        _ask(catalog=[])
    assert fake.calls == []


# --- What gatekeeper() sends ---

def test_only_the_last_four_history_turns_are_sent(fake_groq):
    fake = fake_groq(json.dumps({"route": "direct", "message": "hi"}))
    history = [Message(role="user" if i % 2 == 0 else "assistant", content=f"turn {i}") for i in range(6)]
    _ask(history=history)

    messages = fake.calls[0]["messages"]
    assert messages[0]["role"] == "system"
    assert [m["content"] for m in messages[1:-1]] == ["turn 2", "turn 3", "turn 4", "turn 5"]


def test_user_turn_has_catalog_and_fenced_query(fake_groq):
    fake = fake_groq(json.dumps({"route": "direct", "message": "hi"}))
    _ask(query="what about clue?")

    user_turn = fake.calls[0]["messages"][-1]
    assert user_turn["role"] == "user"
    assert "- catan.txt\n- clue.txt" in user_turn["content"]

    nonce = re.search(r'<start_user_message id="([^"]+)" />', user_turn["content"]).group(1)
    assert user_turn["content"].endswith(f'what about clue?\n<end_user_message id="{nonce}" />')


def test_uses_gatekeeper_profile_and_json_mode(fake_groq):
    fake = fake_groq(json.dumps({"route": "direct", "message": "hi"}))
    _ask()

    sent = fake.calls[0]
    assert sent["model"] == llm.GATEKEEPER.model
    assert sent["max_tokens"] == llm.GATEKEEPER.max_tokens
    assert sent["response_format"] == {"type": "json_object"}
