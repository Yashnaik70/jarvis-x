from .persistence import PersistenceLayer


class MemorySystem:
    def __init__(self, persistence: PersistenceLayer = None):
        self.working_memory = []
        self.episodic_memory = []
        self.semantic_memory = {}
        self.procedural_memory = {}
        self.persistence = persistence or PersistenceLayer()

    def add_memory(self, key: str, value: str):
        self.semantic_memory[key] = value
        self.persistence.store_memory(key, value)

    def retrieve_memory(self, query: str):
        persistent_value = self.persistence.retrieve_memory(query)
        if persistent_value is not None:
            return persistent_value
        return self.semantic_memory.get(query)

    def list_memory(self):
        return self.persistence.list_memory()

    def search_memory(self, query: str):
        results = []
        query_text = query.lower()
        for key, value, created_at in self.persistence.list_memory():
            if query_text in key.lower() or query_text in value.lower():
                results.append((key, value, created_at))
        return results

    def clear_memory(self):
        self.working_memory.clear()
        self.episodic_memory.clear()
        self.semantic_memory.clear()
        self.procedural_memory.clear()
