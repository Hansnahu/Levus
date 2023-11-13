from src.eventCommandHandler import CommandHandler
from src.bots.gtp4free import Botia
from src.voiceToText.annyangV2 import Annyang
from watchdog.observers import Observer
import os, asyncio, pyttsx3, re, threading
#TODO: añadirle la funcion de reconocimiento de voz y gestos para ser administrados por la IA
class Levus():
  bot_name = 'gato' # For now it is the name of the bot 
  _commands = []
  _debug = True
  _IA = Botia()
  voiceRecognitionActive = False
  imageRecognitionActive = False
  observer = Observer()
  def __init__(self):
    self.annyang = Annyang(self)
    self.annyang._debug = True

    command_dir = os.path.join(os.path.dirname(__file__), "commands")
    self.command_handler = CommandHandler(self, command_dir)
    self.observer.schedule(self.command_handler, path=command_dir, recursive=True)
  def start(self):
    self.observer.start()

  def voiceRecognitionToggle(self):
    if self.voiceRecognitionActive:
      self.annyang.abort()
      self.voiceRecognitionActive = False
    else:
      threading.Thread(target=self.annyang.start).start()
      self.voiceRecognitionActive = True
    
  def imageRecognitionToggle(self):
    pass
  def stopAll(self):
    if self.voiceRecognitionActive:
      self.annyang.abort()
    if self.imageRecognitionActive:
      self.annyang.abort()
  def add_commands(self, commands):
    if self._debug: print("[DEBUG] add_commands - NEW COMMANDS - " + str(commands))
    for phrase, callback in commands.items():
      self._commands.append((phrase, callback))
  def remove_commands(self, commands):
    if isinstance(commands, str):
      commands = [commands]
        
    if self._debug: print("[DEBUG] remove_commands - OLD COMMANDS - " + str(self._commands))
    self._commands = [(phrase, callback) for phrase, callback in self._commands if phrase not in commands]
  
  def get_bot_name(self):
    return self.bot_name
  def set_bot_name(self, name):
    self.bot_name = name
  
  def check_commands(self, text):
    text_lower = text.lower()
    isCommand = False
    for phrase, callback in self._commands:
        if phrase.lower() in text_lower:
            isCommand = True
            if self._debug: print(f'Command matched: {phrase}')
            text = text[text_lower.index(phrase.lower()) + len(phrase):]
            try:
                from src.command import Botcommand
                command: Botcommand = callback(self)
                if command.needArgument and text == '':
                  print('FALTA ARGUMENTO')  
                  break
                command.execute(text)
                break
            except Exception as e:
                if self._debug: print(f'Error executing {phrase}: {e}')
    if isCommand == False:
      asyncio.run(self.askIA(text))
      
  async def askIA(self,text):
    response = await self._IA.askInternet(text, temperature=0.1)
    print(response)
    try: pyttsx3.speak(response)
    except Exception as e:
      if self._debug: print(e)
      
    return text