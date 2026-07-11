import asyncio
import os
import re
import subprocess
from typing import Optional

from galaxy.proc_tools import process_iter
from pathlib import Path

from utils import get_uninstall_programs_list


class AmazonGamesClient:
    _CLIENT_NAME_ = 'Amazon Games'
    install_location: Optional[Path] = None

    def __init__(self):
        self._get_install_location()

    def _get_install_location(self):
        for program in get_uninstall_programs_list():
            install_location = program.get('InstallLocation')
            if program.get('DisplayName') == self._CLIENT_NAME_ and install_location:
                self.install_location = Path(install_location).resolve()
                break

    def update_install_location(self):
        if not self.install_location or not self.install_location.exists():
            self._get_install_location()


    @staticmethod
    def _exec(args, cwd=None):
        subprocess.Popen(
            args,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            cwd=cwd,
            shell=False
        )

    async def _aexec(self, args, cwd=None):
        proc = await asyncio.create_subprocess_exec(*args)
        return await proc.wait()

    @property
    def is_installed(self):
        return self.install_location and self.install_location.exists()
    
    @property
    def is_running(self):
        for proc in process_iter():
            if proc is None:
                continue
            binary_path = proc.binary_path
            if binary_path and Path(binary_path).resolve() == self.exec_path:
                return True

        return False

    @property
    def exec_path(self):
        if not self.install_location:
            return ''

        return self.install_location.joinpath("Amazon Games.exe")

    @property
    def owned_games_db_path(self):
        if self.install_location:
            return self.install_location.joinpath('..', 'Data', 'Games', 'Sql', 'GameProductInfo.sqlite').resolve()

    @property
    def entitlements_db_path(self):
        if self.install_location:
            return self.install_location.joinpath('..', 'Data', 'Games', 'Sql', 'Entitlements.sqlite').resolve()

    @property
    def installed_games_db_path(self):
        if self.install_location:
            return self.install_location.joinpath('..', 'Data', 'Games', 'Sql', 'GameInstallInfo.sqlite').resolve()

    @property
    def cookies_path(self):
        if self.install_location:
            return self.install_location.joinpath("Electron3", "Cookies")

    @property
    def remover(self):
        if self.install_location:
            return self.install_location.joinpath('Amazon Games Services', 'Fuel', 'helpers', 'Amazon Game Remover.exe')

    def get_installed_games(self):
        for program in get_uninstall_programs_list():
            if not program['UninstallString'] or 'Amazon Game Remover.exe'.lower() not in program['UninstallString'].lower():
                continue
            
            if not program['InstallLocation'] or not os.path.exists(os.path.abspath(program['InstallLocation'])):
                continue

            # Support product IDs that contain uppercase letters.
            match = re.search(r'-p\s([a-zA-Z\d\-]+)', program['UninstallString'])
            if match:
                game_id = match.group(1)
                yield {
                    'game_id': game_id,
                    'program': program
                }

    async def uninstall_game(self, game_id):
        # Convert the executable path to a string before passing it to subprocess.
        return_code = await self._aexec([str(self.remover), '-m', 'Game', '-p', game_id])
        return True if return_code == 0 else False

    def start_client(self):
        if not self.is_running:
            # Pass the command as a list when shell=False.
            AmazonGamesClient._exec([str(self.exec_path)])

    def stop_client(self):
        if self.is_running:
            # subprocess expects the command as a sequence when shell=False.
            AmazonGamesClient._exec(['taskkill', '/t', '/f', '/im', 'Amazon Games.exe'])

    def game_running(self, game_id):
        for game in self.get_installed_games():
            if game['game_id'] == game_id:
                # Normalize the install path by removing redundant separators and converting it to lowercase.
                install_loc = os.path.normpath(game['program']['InstallLocation']).lower()
                
                # Compare path boundaries explicitly.
                if not install_loc.endswith(os.sep):
                    install_loc_check = install_loc + os.sep
                else:
                    install_loc_check = install_loc
                
                for proc in process_iter():
                    if proc is None:
                        continue
                    binary_path = proc.binary_path
                    if binary_path:
                        proc_path = os.path.normpath(binary_path).lower()
                        # Check whether the running executable is inside the install directory.
                        if proc_path.startswith(install_loc_check):
                            return True
        return False
