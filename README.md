# Valheim-Shared-Worlds
<p align="center"><img src="https://img2.storyblok.com/fit-in/1920x1080/f/157036/6000x3337/61023ec07d/skepp.jpg" alt="Valheim official media from https://www.valheimgame.com/pt/#media" width="1000" height="556"/></p>

# 
A tool for Valheim that allows multiple players to share and host the same world save at any time, without the need for a paid dedicated server.

# Why use it?
If you have a group of friends you play Valheim with, you must know how annoying it is to be able to play only when the world's owner is online and host. With this program, **any player** can yoink the latest world save from the cloud, host the game for the group, and become the temporary new owner. 

When the game session is over, the owner can save back to the cloud for the next person to use. It works just like a dedicated server, but free, just "open" it before playing and "close" it after.

# How it Works?
It is a python script that connects your local Valheim saves to a Github repository, turning it to a cloud database basically for your worlds. 

Once the repository is up, you just need to put the address of it on the settings file and the info to locate your local Valheim saves. You can have as many worlds setup as you wish on the repository, and use the program to select which world to load and save, and it keeps track from older saves, so if anyone want to load a backup, you can (just make sure you select the backup date in Valheim menu). 

Be aware that Github does not support files greater than 100mb, so does this program's version, but it's extremely rare that a world save will supass this size, so it should be just fine... I hope. While only **one person** needs to setup the Github repository, **every player** should install this program and configure the settings.json file to work as intended.

Here is what it does on your machine:
 - Checks your OS and local/Steam cloud Valheim saves folder
 - Upload your newest saves to your Github repository
 - Downloads the latest saves from the repository to your PC before playing
 - Can download older saves on the repository, if it's a old one, just make sure to select it on Valheim Backup World menu
 - Delete old backups on the Github repository
 - (Optional) Launches the game after loading save files from database
 - (Optional) After loading a save from repository, runs in the background (using 0% CPU) until you close the game, then automatically asks if you want to upload your new progress

It is open-source, because, you know, stranger danger, don't download from strangers. If you know how to code (or know how to use AI) you can check the source code to see it isn't malicious. I learned from my friends Windows Defender it really don't like some random exes for some reason. Feel free to compile the source code on your pc or edit it to your likings, and if you do and want to contribute getting this code better for the Valheim community, hit me up, and... sorry about the spaghetti code, I speedran to code this because I was working on my free-time instead of playing Valheim with the homies... but at least now I can grind on my friend's world while he is getting his healthy 8 hours sleep hehehehaw

<p align="center"><img src="https://img2.storyblok.com/fit-in/1000x1000/f/157036/802x1054/9da9082a5f/reeds.png" alt="Valheim official media from https://www.valheimgame.com" width="200" height="263"/></p>

## How to Setup? - Total time: 10min~15min
### STEP 1 - Download: 
Download the .zip from **Releases** (there are versions for every OS, I didn't test it on MacOS btw) and extract in any directory.

### STEP 2 - Setup Repository *(Only one player needs to do this)*: 
One from your group needs to setup the repository:

1. Log in your GitHub account and make a new **Empty** and **Private** repository (so your world isn't exposed to the internet). The name is arbitrary
2. Generate a **GitHub Token** to allow the program to upload files. Go to: 
   `Profile Picture (top right) -> Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens -> Generate new token`
3. On expiration, choose *No Expiration*. Under **Repository access**, choose *Only select repositories* and select the one you just created
4. Under **Permissions -> Repository permissions**, find **Contents** and set it to **Read and write**
5. Generate the token and **copy and save it immediately** (it only shows up once. Send this token to your buddies)

*That's all you need from Github, from now on, you can just run the script.* 
*Beware that your friends can alter this repository's contents with this token, so be sure to send it only to the real ones*

### STEP 3 - Configure Settings File: 
Open the config folder and edit the settings.json crucial fields (always insert values in the double quotes. Ex: "steamID": "" will become "steamID": "9999999" and don't delete any comma for God's sake):

  - githubToken: The token created on *STEP 2*. (who created the repository must share this to all players)
  - githubRepository: The path to the repo created on *STEP 2*, the same as the URL of the repo but without the Github domain, just GithubProfileName/GithubRepositoryName
  - maxWorldSaves: How many backups saves to keep on Github
  
  - username: Your nickname (shows who uploaded or load the last save)
  - pc_username: Your OS profile name (used to find local Valheim local saved paths)
  - steam_id: Your Steam ID, the same you use to send to someone as a Friend Request (found on Steam -> Friends -> Add Friends). Needed to locate Steam Cloud saves path 
  - saveMode: You can leave it as "" (program will ask every time which one) or set to "cloud" or "local". This will specify where the world is saved and where to save it. Be sure to keep the same option you did on your world in Valheim Menu (you can select there if the world is local or on steam cloud) 
  - automatic_save_when_game_closes: true if you want the program to wait until you close the game (using 0% CPU), then it asks if you want to upload to the database the world save, keep it false (without "") if you want it to end processes after lauching the game, but then remember to save your progress, opening the program again and doing save operation

## How to Use Valheim-Shared-Worlds:
If this is the first time running the program, open the program and do a *SAVE* operation, there it will see there's no world available in database and ask for you to create one. You must create or already have a world Valheim in-game with the same name.

**To 'OPEN the server':** Run the program before opening the game and run the command **LOAD**. This will get the lastests saves from the Github repository and import the one you select to your pc. Open Valheim, select the world, check "Start Server", and invite the bois

**To 'CLOSE the server':** When you are done gaming, close Valheim. The program will detect the game closed and ask to **SAVE** your progress tp the repository. If you closed the program, open it and run the command **SAVE** on your world. There, ready for your friends to use and play

*Tip: press Enter to accept default values when the program asks questions. Note that in (Y or n) the y is the default. The program isn't case-sensitive (only for world names, yeah, I had to say it just in case)*

<p align="center"><img src="https://img2.storyblok.com/fit-in/1000x1000/f/157036/552x800/322109d551/build-2.png" alt="Valheim official media from https://www.valheimgame.com" width="276" height="400"/></p>

## Have a good one with the bois 🫡
*All images belongs to Valheim official media from https://www.valheimgame.com*

I will start making videos about this and other development things (game devlogs, hell yeah) once I get over my lazyness and abusive working conditions. So if you wanna kindly support and like this type of content...

**Consider subscribing:** https://www.youtube.com/@CodeDruida
