import requests
import discord_utils
import time
import bodystuff
import json
import subprocess
from datetime import datetime
import os

class DiscordUpdater:

    def __init__(self):
        self.old = None
        self.repos = ["body", "qoft"]
        if os.path.exists("old.json"):
            with open("old.json", "r") as f:
                self.old = f.read()


    def run(self):
        while True:
            self.run_task()
            time.sleep(90)

    def push(self, repo : str):
        current_time = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        subprocess.run("git add .", cwd=repo, shell=True)
        subprocess.run(f"git commit -m \"Updated data the {current_time}\"", cwd=repo, shell=True)
        subprocess.run("git push", cwd=repo, shell=True)

    def run_task(self):


        client_build_number = discord_utils.get_client_build()

        out = {
            "build_numbers": {
                "client": client_build_number,
                "main": discord_utils.get_main_ver(),
                "native": discord_utils.get_native_build()
            },
            "useragents": {
                "desktop": {

                }
            }
            
        }

        for user_agent in self.get_desktop_user_agents():
            useragent_info = discord_utils.get_useragent_infos(client_build_number, user_agent)
            out["useragents"]["desktop"][user_agent] = useragent_info


        out = json.dumps(out, indent=4)
        if self.old == out:
            bodystuff.logger.info("No changes detected, skipping update...")
            return
        
        bodystuff.logger.success("Changes detected, updating...")

        for repo in self.repos:
            bodystuff.logger.info(f"Updating", repo=repo)
            subprocess.run("git pull --force", cwd=f"repos/{repo}", shell=True)
            with open(f"repos/{repo}/fetch", "w") as f:
                f.write(out)

            self.push(f"repos/{repo}")
            bodystuff.logger.success(f"Updated", repo=repo)

        bodystuff.logger.success("Update published to all repos!")
        with open("old.json", "w") as f:
            f.write(out)
        self.old = out


                

    def get_desktop_user_agents(self):
        return requests.get("https://raw.githubusercontent.com/microlinkhq/top-user-agents/master/src/desktop.json").json()
    

DiscordUpdater().run()
