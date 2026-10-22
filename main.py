from github import Github
from github import Auth
from utils import Debug, Config, Menu
from valheim_manager import ValheimManager
import subprocess
import time
import psutil
import platform
import os
import sys
from pathlib import Path
# pyinstaller --noconfirm --onefile --distpath ../ src/main.py

def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


SETTINGS_PATH = app_dir() / "config" / "settings.json"
CREATE_NEW_WORLD_CMD= "$CREATE_WORLD"

def launch_game(cmd: list[str]):
    subprocess.Popen(cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

def main():
    os.system("")
    Config.read_settings(SETTINGS_PATH)
    while True:
        try:
            git = Github(auth=Auth.Token(Config.settings['Server']['githubToken']))
            repo = git.get_repo(Config.settings['Server']['githubRepository'])        

            Config.settings["repository"] = repo
            Config.settings["IsServerActive"] = False
            break;
        except Exception as e:
            Debug.log("Warning", f"Connection to the repository rejected. Check your internet, token and repository name: {e}")
            input("Press any key to check again...")

    print("<-~-~- { VALHEIM SHARED OFFLINE SERVER } -~-~->")
    print(f"Tip: press {Debug.underline('Enter')} to accept default values. Note that in (Y or n) the y is the default\n")

    operation = Menu.select_option(f"\n > {Debug.underline('Save')} or {Debug.underline('Load')} world save?",
                        options=["save", "load"]
                        )

    worldName = ""
    while worldName == "":
        print(f" > Select the world (type {CREATE_NEW_WORLD_CMD} to create a new save directory for a world) (default=1)", end=" ")
        contents = ValheimManager.get_contents_in_path()

        if contents == []:
            print("\n[No world have been saved yet]")
            ValheimManager.create_new_world()
            continue

        worldName = Menu.select_dir(contents, 
                                    if_exec={CREATE_NEW_WORLD_CMD: ValheimManager.create_new_world}) # Retorna "" se fal

    print(ValheimManager.get_server_status(worldName))
    print("- " * 20)

    print(Debug.style("UNDERLINE", f"\n[SELECTED {worldName}]"))

    saveMode = Config.settings["Client"]["saveMode"]
    if saveMode == "":
        saveMode = Menu.select_option(f" > Do you want to {operation} world in {Debug.underline('Local')} or {Debug.underline('Cloud')} path? (default=cloud)",
                                        options=["local", "cloud"],
                                        default="cloud"
                                        )

    client_config = Config.settings["Client"]
    sys_os = platform.system()
    print(f"Using paths configured for {sys_os}")

    if sys_os == "Windows":
        user_os = "Windows"
    elif sys_os == "Linux":
        user_os = "Linux"
    elif sys_os == "Darwin":
        user_os = "MacOS"
    else:
        Debug.log("Warning", f"Operational System not identified, using Linux paths on {SETTINGS_PATH}")
        user_os = "Linux"

    aux_local_path = Config.settings['Client'][user_os]['cloudSavePath'] if saveMode == "cloud" else Config.settings['Client'][user_os]['localSavePath']
    Config.settings["Local_Path"] = aux_local_path % client_config
    Config.settings["gameLaunch"] = Config.settings['Client'][user_os]['gameLaunch']
    Config.settings["save_mode_selected"] = saveMode

    match operation:
        case "save":
            save_to_github(worldName)
        
        case "load":
            ValheimManager.load_world(worldName)
            ValheimManager.update_server_status(worldName, Debug.paint_green("ACTIVE"))

            cmd = Menu.select_option("\n > Launch Valheim? (Y or n) ",
                                    options=["y", "n"],
                                    default="y"
                                    )
            if (cmd == "y"):
                launch_game(Config.settings["gameLaunch"])
        
                if Config.settings["Client"]["automatic_save_when_game_closes"]:
                    monitor_until_closed(worldName)

def save_to_github(worldName:str):
    ValheimManager.save_world(worldName)
    ValheimManager.update_server_status(worldName, Debug.paint_red("INACTIVE"))

    contents = ValheimManager.get_contents_in_path(worldName)
    contents_limit = int(Config.settings['Server']['maxWorldSaves'])

    if len(contents) > contents_limit:
        Debug.log("Warning", f"The save limit set on {SETTINGS_PATH} was reached. LIMIT = ({contents_limit} / SAVES NUMBER = {len(contents)}.)")
        cmd = Menu.select_option(" > Delete last saves out of limits? (Y or n)",
                    options=["y", "n"],
                    default="y"
                    )
        if cmd == "n":
            return

    for old_dir in contents[Config.settings["Server"]["maxWorldSaves"]:]:
        for f in Config.settings["repository"].get_contents(old_dir.path):
            Config.settings["repository"].delete_file(
                path= f.path, 
                message= "Old save number out of limits", 
                sha= f.sha
            )
            print(Debug.underline(f"{f.path} DELETED."))
    Debug.log("Success", "Files saved successfully!")

def monitor_until_closed(worldName:str):
    print("=" * 40)
    print("\n[Monitor] Waiting Valheim to start...")
    
    process_names = ["valheim.exe", "valheim.x86_64", "valheim"]
    target_process = None

    timeout = 60 * 5 # 5 minutos 
    while timeout > 0:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in process_names:
                    target_process = proc
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                pass
        if target_process:
            break
            
        time.sleep(2)
        timeout -= 2
        
    if not target_process:
        Debug.log("Warning", f"[Monitor] Valheim haven't launched in the last {timeout} seconds. Ending Program")
        return

    Debug.log("Success", f"[Monitor] Valheim detected! PID: {target_process.pid}. Starting hibernation until it closes...")

    target_process.wait()
    
    print("\n[Monitor] Valheim Closed!")
    print("=" * 40)

    cmd = Menu.select_option(f"\n > {Debug.paint_green('SAVE')} the latest save of {worldName} to the server? (Y or n)",
            options=["y", "n"],
            default="y"
            )
    if cmd == "y":
        save_to_github(worldName)

if __name__ == '__main__':
    main();
    input("Press Enter to exit...")