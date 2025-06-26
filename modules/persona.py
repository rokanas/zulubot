# modules/persona.py
import os
import json
import discord

class Persona:
    def __init__(self, bot=None):
        # init instance variables
        self.persona_data = {}
        self.current_persona = None
        self.name = ""
        self.context = ""
        self.voice_id = ""
        self.bot = bot

        # directory with avatar pictures
        self.assets_dir = "assets"

        self._load_personas()

    async def init_default(self):
        # initialize with default persona and avatar (separate method for async init)
        if self.persona_data:
            first_persona = next(iter(self.persona_data))
            await self.set_persona(first_persona)
        else:
            print("Warning: No personas found in JSON file.")
        
    async def set_persona(self, persona):
        """change current persona"""
        persona_lower = persona.lower()

        # check that persona data was successfully added from json
        if not self.persona_data:
            # return ("Der ah no personas available. Make one wit **!zuluaddpersona** or contact my creatah.", None)
            return ("Der ah no personas available. Please contact my creatah.", None)
        
        # check if trying to set to currently active persona
        if persona_lower == self.current_persona:
            return (f"De Zulu is already one wit de {self.name}!", None)

        # set persona data
        if self._set_persona_data(persona_lower):
            persona_message = f"De Zulu has set de persona to: {self.name}"
            avatar_message = await self.set_avatar()
            return (persona_message, avatar_message)
        
        return ("De Zulu does not recognize dis persona. Use **!zulupersonas** to see de list of valid personas.", None)
    
    async def set_avatar(self):
        """set bot avatar image according to persona"""
        try:
            # construct image path to persona avatar image
            image_path = os.path.join(self.assets_dir, f"{self.current_persona}.png")

            # check if assets directory exists
            if not os.path.exists(self.assets_dir):
                return "Howeva, de assets folda does not exist. De Zulu cannot find his masks."
            
            # check if image file exists
            if not os.path.exists(image_path):
                return "Howeva, de Zulu cannot find his mask in de assets folda."
            
            # read and set avatar
            with open(image_path, 'rb') as image_file:
                avatar_data = image_file.read()
                await self.bot.user.edit(avatar=avatar_data)
                return None
            
        except discord.HTTPException as e:
            print(f"Error setting avatar: {e}")
            if e.status == 429 or e.status == 400:  # rate limited or bad request (usually also rate limited)
                return "Howeva, de Zulu cannot change his mask so quickly."

        except:
            print(f"Error setting avatar: {e}")
            return "Howeva, de Zulu cannot find his mask."
        
    def get_personas(self):
        """return list of available persona names (and mark active one)"""
        if not self.persona_data:
            return ["Neva mind, no personas exist."]
    
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

    # separate from __init__ in case of future !zulurefresh command
    def _load_personas(self):
        # load persona data from json file
        try:
            json_path = os.path.join(os.path.dirname(__file__), '..', 'personas.json')
            print(f"Looking for personas file at: {json_path}")
            # check if json file existss
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.persona_data = data.get('personas', {})
                    print(f"Loaded personas: {list(self.persona_data.keys())}")
            else:
                print(f"Warning: Personas file not found at {json_path}")
        except Exception as e:
            print(f"Error loading personas: {e}")

    # separate from set_persona for future reuse
    def _set_persona_data(self, persona):
            """helper function to set persona data"""      
            # check if specified persona exists   
            if persona in self.persona_data:
                # set instance variables
                self.current_persona = persona
                persona_obj = self.persona_data[self.current_persona]
                self.name = persona_obj["name"]
                self.context = persona_obj["context"]
                self.voice_id = persona_obj["voice_id"]
                return True
            return False

