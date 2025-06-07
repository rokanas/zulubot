# modules/persona.py
import os
import json

class Persona:
    def __init__(self):
        # init instance variables
        self.persona_data = {}
        self.current_persona = None
        self.name = ""
        self.context = ""
        self.voice_id = ""
        
        # load personas from json file
        try:
            json_path = os.path.join(os.path.dirname(__file__), '..', 'personas.json')
            print(f"Looking for personas file at: {json_path}")
            # check if json file existss
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.persona_data = data.get('personas', {})
                    print(f"Loaded personas: {list(self.persona_data.keys())}")

                # if personas exist, set first one as default (normally "zulu")
                if self.persona_data:
                    first_persona = next(iter(self.persona_data))
                    self.set_persona(first_persona)
                else:
                    print("Warning: No personas found in JSON file.")
            else:
                print(f"Warning: Personas file not found at {json_path}")
        except Exception as e:
            print(f"Error loading personas: {e}")

    def set_persona(self, persona):
        """change current persona"""
        persona_lower = persona.lower()

        # check that persona data was successfully added from json
        if not self.persona_data:
            return "Der ah no personas available. Make one wit **!zuluaddpersona** or contact my creatah."
        
        # check if trying to set to currently active persona
        if persona_lower == self.current_persona:
            return f"De Zulu is already one wit de {self.name}!"

        # check if specified persona exists
        if persona_lower in self.persona_data:
            # set instance variables
            self.current_persona = persona_lower
            persona_obj = self.persona_data[self.current_persona]
            self.name = persona_obj["name"]
            self.context = persona_obj["context"]
            self.voice_id = persona_obj["voice_id"]
            return f"De Zulu has set de persona to: {self.name}"
        return "De Zulu does not recognize dis persona. Use **!zulupersonas** to see de list of valid personas."
    
    def get_personas(self):
        """return list of available persona names (and mark active one)"""
        persona_list = []
        for key, persona_obj in self.persona_data.items():
            if key == self.current_persona:
                persona_list.append(f"{persona_obj['name']} **(ACTIVE)**")
            else:
                persona_list.append(f"{persona_obj['name']}")
        return persona_list
    
    # Commented out but can be implemented
    # def add_persona(self, name, context, voice_id=None):
    #     """Add new persona and save to JSON file"""
    #     name_lower = name.lower()
    #     self.persona_data[name_lower] = {
    #         "name": name,
    #         "context": context,
    #         "voice_id": voice_id
    #     }
    #  
