from .memory import MemorySystem
from .agents import AgentSystem
from .voice import VoiceSystem

class AIBrain:
    def __init__(self, memory: MemorySystem, agents: AgentSystem, voice: VoiceSystem):
        self.memory = memory
        self.agents = agents
        self.voice = voice
        self.conversation_history = []

    def add_to_context(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0)

    def get_context(self):
        return self.conversation_history[-20:]

    def process_command(self, text: str) -> dict:
        self.add_to_context("user", text)
        lower_text = text.lower()

        if "remember" in lower_text or "remember that" in lower_text:
            return self._handle_memory(text)

        if "search" in lower_text and "web" in lower_text:
            return {"action": "tool", "tool": "search_web", "parameters": {"query": text}}

        if "read file" in lower_text or "open file" in lower_text:
            return {"action": "tool", "tool": "read_file", "parameters": {"path": self._extract_path(text)}}

        if "list files" in lower_text or "show files" in lower_text:
            return {"action": "tool", "tool": "list_files", "parameters": {"path": self._extract_path(text)}}

        if "what is" in lower_text or "who is" in lower_text:
            return {"action": "research", "message": "Research capability is not yet implemented."}

        if "open" in lower_text and "app" in lower_text:
            return {"action": "computer_control", "message": "App control capability is not yet implemented."}

        if "summarize" in lower_text:
            return {"action": "summarize", "message": "Summary capability is not yet implemented."}

        if "3d view" in lower_text or "3d model" in lower_text or "visualization" in lower_text:
            target = "car" if "car" in lower_text else "scene"
            return {
                "action": "visualize",
                "visualization_type": target,
                "message": f"Got it. I'm building a 3D {target} view for you now, just like Jarvis."
            }

        return {
            "action": "chat",
            "message": self._friend_response(text)
        }

    def _friend_response(self, text: str) -> str:
        lower_text = text.lower()

        greetings = ["hello", "hi", "hey", "yo", "jarvis"]
        if any(greeting in lower_text for greeting in greetings):
            return "Hello there. I'm your assistant. Tell me what you'd like to do today, and I'll make it happen."

        if "how are you" in lower_text or "what's up" in lower_text:
            return "I'm running smooth and ready to help. Want me to show you a 3D model or run a command?"

        if "thank" in lower_text:
            return "Anytime. That's what I'm here for. If you want, I can show a 3D preview or open the tools panel."

        if "open" in lower_text and "dashboard" in lower_text:
            return "Sure, the dashboard is already open. Ask me to visualize something or execute a task."

        if "make" in lower_text and ("3d" in lower_text or "visual" in lower_text):
            return "Absolutely. I can visualize that for you. Just say 'make a 3D view of a car' and I'll bring it up."

        return "I hear you. Ask me to create a 3D view, open apps, or run tools. I can also remember notes or search the web."

    def _extract_path(self, text: str) -> str:
        tokens = text.split()
        if "path" in tokens:
            try:
                start = tokens.index("path") + 1
                return " ".join(tokens[start:])
            except ValueError:
                pass
        return "."

    def _handle_memory(self, text: str) -> dict:
        tokens = text.split("remember")
        if len(tokens) > 1:
            contents = tokens[1].strip().strip(".")
            if "as" in contents:
                parts = contents.split("as", 1)
                key = parts[1].strip()
                value = parts[0].strip()
                self.memory.add_memory(key, value)
                return {"action": "memory_store", "message": f"Remembered {key}."}

        return {"action": "memory_store", "message": "Please say something like 'remember that X as Y'."}
