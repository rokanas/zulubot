# modules/persona.py
class Persona:
    def __init__(self, context="zulu"):
        self.contexts = {
            "Zulu": "You are a mighty Zulu warrior. Answer the following message sounding like a mighty tribesman of the Zulu nation:\n\n",
            "Joe": "Answer the following as though you were a free spirited, anti-babylonian, gaja-smoking freedom fighter named Joe:\n\n"
        }
        self.current_context = context # default
        self.context = self.contexts[self.current_context]

    def set_context(self, context_name):
        """change current context to a different persona"""
        if context_name in self.contexts:
            self.current_context = context_name
            self.context = self.contexts[context_name]
            return True
        return False
    
    def get_contexts(self):
        """return list of available persona names"""
        return list(self.contexts.keys())
    
    def add_context(self, name, prompt):
        """add new context to the available contexts"""
        self.contexts[name] = prompt
        return True