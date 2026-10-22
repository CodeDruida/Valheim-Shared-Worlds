import json
from typing import Callable
import sys

class Debug:
    CODES = {
        "Reset": "\033[0m",
        "Underline": "\033[4m",
        "Green": "\033[32m",
        "Yellow": "\033[33m",
        "Red": "\033[91m"
    }

    LEVELS = {
        "Success": f"{CODES['Green']}[SUCCESS]{CODES['Reset']}--",
        "Warning": f"{CODES['Yellow']}[WARNING]{CODES['Reset']}",
        "Error": f"{CODES['Red']}[ERROR]{CODES['Reset']}"
    }

    @staticmethod
    def log(log_type:str , message:str):
        log_type = log_type.capitalize()
        prefix = Debug.LEVELS.get(log_type, f"[{log_type}]")

        print(f"\n{prefix} {message}");

        if log_type == "Error":
            input("Press Enter to exit...");
            sys.exit(1);

    @staticmethod
    def style(style_type:str, message:str) -> str:
        return f"{Debug.CODES[style_type.capitalize()]}{message}{Debug.CODES['Reset']}"

    @staticmethod
    def underline(message:str) -> str:
        return Debug.style("Underline", message)

    @staticmethod
    def paint_red(message:str) -> str:
        return Debug.style("Red", message)

    @staticmethod
    def paint_green(message:str) -> str:
        return Debug.style("Green", message)

class Config:
    settings = {}

    @staticmethod
    def read_settings(path:str):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                Config.settings = json.load(file)

        except FileNotFoundError:
            Debug.log("Error", f"Configuration file not found at {path}")
        except json.JSONDecodeError as e:
            Debug.log("Error", f"Invalid JSON format in config: {e}")

class Menu: 
    @staticmethod
    def select_dir(contents:list, if_exec:dict[str, Callable[[], None]]=None) -> str:
        selected = ""
        while True:
            try:
                user_input = input("   >> ")

                if if_exec != None and user_input in if_exec:
                    if_exec[user_input]()
                    return ""

                index = 0 if user_input == "" else int(user_input) - 1
                selected = contents[index].path
                break
            except:
                Debug.log("Warning", f"Invalid input. Use only numbers in the range of {Debug.underline('[Options]')}")
        return selected

    @staticmethod
    def select_option(message, options, default=""):
        user_input = ""
        while user_input not in options:
            print(message)
            user_input = str.lower(input("   >> "))
            user_input = default if user_input == "" else user_input
        return user_input