from utils import Debug, Config, Menu
from github import Github, GithubException
import requests
import datetime
import sys
import os
import re

class ValheimManager:
    # @staticmethod
    # def get_date_from_file(file_name:str) -> str:
    #     pattern_date = re.compile(r'(\d{8})-?(\d{6})') # Search for date in filename
    #     match = pattern_date.search(file_name)
        
    #     if not match:
    #         return ""
        
    #     date_string = match.group(1) + match.group(2)
    #     return date_string

    @staticmethod
    def get_contents_in_path(path:str="") -> list: # Show content as options and ordered them by date. path=="" = path=="./"
        try:
            contents = Config.settings["repository"].get_contents(path)
            contents = [c for c in contents if c.type == "dir"] # Novo codigo - so aceita diretorios 

            if len(contents) <= 0:
                return []

            if path != "":
                contents = sorted(contents, key=lambda c: c.name, reverse=True) # Ordena arquivos que nao estao na raiz -> arquivos de tempo "%Y-%m-%d_%H-%M-%S" ficam em ordem
        
            print(f"[Options = 1 ... {len(contents)}]")

            for cnt, content in enumerate(contents, start=1):
                print(f"       {cnt}. {content.name}", end=" -> ")
                if path != "":
                    commit_message = Config.settings["repository"].get_commits(path=content.path)[0].commit.message  # Print mensagem de commit do primeiro arquivo no diretorio
                    print(commit_message, end=" ");
                print("\n", end="");

            return contents
        except GithubException as e:
            if e.status == 404:
                return [] # Retorna uma lista vazia se nao houver diretorios
            else:
                raise Debug.log("Error", f"Github: {e}")
        except Exception as e:
            Debug.log("Error", f"Listing contents: {e}")
            return []

    @staticmethod
    def get_server_status(path:str) -> str:
        repo = Config.settings["repository"]
        status = repo.get_contents(path + "/" + Config.settings["Config"]["SERVER_STATUS_FILE"]).decoded_content.decode('utf-8')
        Config.settings["IsServerActive"] = False if "INACTIVE" in status else True
        return f"\n{status}";

    @staticmethod
    def update_server_status(worldName:str, status:str):
        Config.settings["IsServerActive"] = False if "INACTIVE" in status else True
        update_status = Config.settings["repository"].get_contents(worldName + "/" + Config.settings["Config"]["SERVER_STATUS_FILE"])
        username = Debug.underline(Config.settings['Client']['username'])
        status_model = Config.settings["Config"]["SERVER_STATUS_MODEL"]

        Config.settings["repository"].update_file(
            path= update_status.path,
            message= "Updating Status...",
            content= status_model % (status, username),
            sha= update_status.sha
        )
        Debug.log("Success", "Server Status updated.")

    @staticmethod
    def create_new_world():
        print(f"\n > What is the new world server name? (It need to be {Debug.underline('the exactly same name')} as your game saved world)")
        worldName = input("   >> ")
        newFiles = [Config.settings["Config"]["SERVER_STATUS_FILE"]]

        for file in newFiles:
            Config.settings["repository"].create_file(
                path= worldName + "/" + file,
                message= "New file",
                content= Debug.paint_red('INACTIVE')
            )
        Debug.log("Success", "New world files created. Ready for load or save.\n\n")

    @staticmethod
    def load_world(worldName):
        if Config.settings["IsServerActive"]:
            status_text = ValheimManager.get_server_status(worldName)

            if "\nWho is hosting: " in status_text:
                username = status_text.split("\nWho is hosting: ")[-1].strip()
            else:
                username = status_text

            Debug.log("Warning", f"The server is still {Debug.paint_red('OPEN')} by {Debug.underline(username)}. Or the user may have forgot to load back the world to the Github server. Proceeding can {Debug.paint_red('OVERWRITE')} this user's world version that wasn't saved yet or yours if you load the older saved world version.")
            opt = Menu.select_option(" > Are you sure you want to continue? (y or N)",
                            options=["y", "n"],
                            default="n"
                            )
            if opt == "n":
                sys.exit(0)

        print(f"\n{Debug.underline(f'[SELECTED {worldName}]')} Select the save to be loaded (default=most recent): ")
        contents = ValheimManager.get_contents_in_path(worldName) # Diretorios de saves por date

        if contents == []:
            Debug.log("Error", f"No saves available in {worldName}, please, use {Debug.underline('Save')} operation to populate this database")

        latest_save_dir = contents[0]
        contents_in_last_save = Config.settings["repository"].get_contents(latest_save_dir.path)
        local_files = os.listdir(Config.settings["Local_Path"])

        save_up_to_date = True

        for file in contents_in_last_save: # Checa se arquivos estao salvos localmente ja
            if file.type=="file" and file.name not in local_files:
                save_up_to_date = False

        if save_up_to_date:
            opt = Menu.select_option(f"\n > {Debug.paint_green('Your save is up to date!')} Nobody loaded your current saved version yet since you saved it. Want to load this save still? (y or N)",
                            options=["y", "n"],
                            default="n"
                            )
            if opt == "n":
                return

        contents = ValheimManager.get_contents_in_path(worldName) # Diretorios de saves por date
        path_to_import = Menu.select_dir(contents)
        contents_to_import = Config.settings["repository"].get_contents(path_to_import)
        
        print(f"[SELECTED {path_to_import}] Loading world to {'local world saves' if Config.settings['save_mode_selected'] == "local"  else 'Steam cloud world saves'}...")
        for content in contents_to_import:
            worldSave = Config.settings["repository"].get_contents(content.path);
            print(f"{content.name} -> Loaded")

            if worldSave.encoding == "none":
                worldSave = requests.get(worldSave.download_url).content;
            else:
                worldSave = worldSave.decoded_content;
    
            with open(f"{Config.settings['Local_Path']}/{content.name}", "wb") as world:
                world.write(worldSave);
        Debug.log("Success", f"{worldName} save was loaded.")

    @staticmethod
    def save_world(worldName):
        if not Config.settings["IsServerActive"]:
            Debug.log("Warning", f"The server is {Debug.paint_red('NOT OPENED')}. Meaning you didn't opened it before playing, meaning you didn't loaded the last save of the repository. If anyone saved their progress on the repository before you loaded it, this save can {Debug.paint_red('OVERWRITE')} the other world save version.")
            opt = Menu.select_option(" > Are you sure you want to continue? (y or N)",
                            options=["y", "n"],
                            default="n"
                            )
            if opt == "n":
                sys.exit(0);
        try:                      
            local_files = os.listdir(Config.settings["Local_Path"])
            backup_files_time = {
                "db": [],
                "fwl": []
            }

            for f in local_files:
                if f.startswith(f"{worldName}_") or f.startswith(f"{worldName}."): # Garante que nomes como Mundo e Mundo2 sejam confundidos
                    f_name_diff = f[len(worldName):].split('.')[0]

                    time = "".join(char for char in f_name_diff if char.isdigit())

                    if time != "":
                        if ".db" in f:
                            backup_files_time["db"].append((time, f))
                        elif ".fwl" in f:
                            backup_files_time["fwl"].append((time, f))

            backup_files_time["db"] = sorted(backup_files_time["db"], reverse=True);
            backup_files_time["fwl"] = sorted(backup_files_time["fwl"], reverse=True);

            latest_backup_db = ""
            latest_backup_db_time = ""
            if backup_files_time["db"]: # Verifica se existe backup
                latest_backup_db_time, latest_backup_db = backup_files_time["db"][0]
            else:
                Debug.log("Warning", "Backup .db file not found. If this is a new save might not be a problem")

            latest_backup_fwl = ""
            if backup_files_time["fwl"]:
                _, latest_backup_fwl = backup_files_time["fwl"][0]
            else:
                Debug.log("Warning", "Backup .fwl file not found. If this is a new save might not be a problem")

            files_to_export = [
                worldName + ".db",
                worldName + ".fwl",
                latest_backup_db, # E necessario backup para o save funcionar corretamente
                latest_backup_fwl
            ]

            # last_backup_DT = datetime.datetime.strptime(latest_backup_db_time, '%Y%m%d%H%M%S'); # Checagem para verificar se o tempo do arquivo esta certo. Tirado para simplificar sistema ao usuario
            # opt = Menu.select_option(f" > Last local save was at [{last_backup_DT.strftime('%d-%m-%Y %H:%M:%S')}] Upload this save? (Y or n)",
            #             options=["y", "n"],
            #             default="y"
            #             );
            # if opt == "n":
            #     sys.exit(0);
            
            print(f" > {worldName} save's description: ");
            commit_desc = input("   >> ");

            current_time = datetime.datetime.now();
            saved_time = datetime.datetime.strftime(current_time, '%Y-%m-%d_%H-%M-%S')
            commit_message = f"[Saved by: {Config.settings['Client']['username']}] Description: {commit_desc}";
            
            for f_to_export in files_to_export:
                if f_to_export == "":
                    continue

                with open(Config.settings["Local_Path"] + "/" + f_to_export, "rb") as file_content:
                    Config.settings["repository"].create_file(
                        path= f"{worldName}/{saved_time}/{f_to_export}", # repo: Nome mundo / data do save / arquivo
                        message= commit_message,
                        content= file_content.read()
                    );
            Debug.log("Success", f"{worldName} saved.");
        except Exception as e:
            Debug.log("Error", f"World may not exist in {Config.settings['Local_Path']}. Check if the path and world exists. Or you don't have Github permissions to write: {e}");
    