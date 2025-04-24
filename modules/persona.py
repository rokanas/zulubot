# modules/persona.py
class Persona:
    def __init__(self, persona="zulu"):
        self.names = {
            "zulu": "👨🏿 Zulu",
            "joe": "🦧 Joe  ",
            "custom": "🤖 Custom"
        }

        self.contexts = {
            "zulu": "You are a mighty Zulu warrior. Answer the following message sounding like a mighty tribesman of the Zulu nation:\n\n",
            "joe": "Answer the following as though you were a free spirited, anti-babylonian, ganja-smoking freedom fighter named Joe:\n\n",
            "custom": ""
        }
        self.voices = {
            "zulu": "ddDFRErfhdc2asyySOG5", 
            "joe": "eVxgJgA3Vm8WgQZnIT8g",  
            "custom": ""
        }

        # set instance attributes
        self.current_persona = persona.lower() # default
        self.name = self.names[self.current_persona]
        self.context = self.contexts[self.current_persona]
        self.voice = self.voices[self.current_persona]
        self.set_persona(self.current_persona)

    def set_persona(self, persona):
        """change current context to a different persona"""
        self.current_persona = persona.lower()
        if self.current_persona in self.names:
            self.name = self.names[self.current_persona]
            self.context = self.contexts[self.current_persona]
            self.voice = self.voices[self.current_persona]
            return f"De Zulu has set de persona to: {self.name}"
        return "De Zulu does not recognize dis persona. Use **!zulupersonas** to see de list of valid personas."
    
    def get_personas(self):
        """Return list of available persona names and mark current one"""
        persona_list = []
        for key, label in self.names.items():
            if key == self.current_persona:
                persona_list.append(f"{label} **(ACTIVE)**")
            else:
                persona_list.append(f"{label}")
        return persona_list
    
    # def add_persona(self, name, prompt):
    #     """add new context to the available contexts"""
    #     self.contexts[name] = prompt
    #     return True