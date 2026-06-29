import asyncio
import json
import logging
import sys
import webbrowser

# Add the Modules directory to sys.path so bundled dependencies resolve locally.
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Modules"))

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Feature, Platform, LicenseType, LocalGameState, OSCompatibility
from galaxy.api.types import Authentication, Game, LicenseInfo, LocalGame, GameTime
from time import time
from typing import List

from version import __version__
from client import AmazonGamesClient
from db_client import DBClient
from authentication import create_next_step, START_URI, END_URI
from utils import crypt_unprotect_data


LOCAL_GAMES_TIMEOUT = (1 * 60)
OWNED_GAMES_TIMEOUT = (10 * 60)
FALLBACK_SYNC_TIMEOUT = (2.5 * 60)
RUNNING_CHECK_INTERVAL = 5  # seconds between running-state polls


class AmazonGamesPlugin(Plugin):
    _owned_games_db = None
    _local_games_db = None
    _owned_games_last_updated = 0
    _local_games_last_updated = 0
    _last_install_check = 0
    _last_running_check = 0
    _auth = False
    _uses_entitlements = False

    def __init__(self, reader, writer, token):
        super().__init__(Platform.Amazon, __version__, reader, writer, token)
        self.logger = logging.getLogger('amazonPlugin')
        self._client = AmazonGamesClient()

        self._local_games_cache = None
        self._owned_games_cache = None
        self._local_game_paths = {}  # game_id -> install_directory
        self._game_launch_times = {}  # game_id -> timestamp of last launch_game call
        self._active_sessions = {}  # game_id -> timestamp of active session start

    def _save_cache(self, key: str, data):
        self.persistent_cache[key] = json.dumps(data)
        self.push_cache()

    def _load_cache(self, key: str, default=None):
        if key in self.persistent_cache:
            return json.loads(self.persistent_cache[key])
        return default

    def _init_db(self):
        if not self._owned_games_db:
            entitlements_db_path = self._client.entitlements_db_path

            if entitlements_db_path and entitlements_db_path.exists():
                self.logger.info('Uses new "Entitlements.sqlite" database')
                self._uses_entitlements = True
                self._owned_games_db = DBClient(entitlements_db_path)
            else:
                # Use the legacy database when Entitlements.sqlite is not available.
                self._owned_games_db = DBClient(self._client.owned_games_db_path)

        if not self._local_games_db:
            self._local_games_db = DBClient(self._client.installed_games_db_path)

    def _on_auth(self):
        self.logger.info("Auth finished")
        self._init_db()
        self._auth = True

        self.store_credentials({ 'creds': 'dummy_data_because_local_app' })
        return Authentication('amazon_user_id', 'Amazon Games User')

    async def _auth_finished(self):
        start = time()

        while (time() - 15 <= start):
            if (self._auth):
                return True
            
            await asyncio.sleep(0.5)

        return False

    def _title_wrapper(self, title: str, game_id: str):
        if title:
            return title

        self.logger.warning('Missing title for game_id "%s". Using placeholder title.', game_id)

        return f'Amzn Game ({game_id.split(".")[-1]})'

    def _get_owned_games(self):
        try:
            if self._uses_entitlements:
                rows = self._owned_games_db.select('game_entitlements', rows=['value'])
                if rows is None:
                    return None
                # Skip empty results before parsing the decrypted payload as JSON.
                raw_values = [crypt_unprotect_data(x['value']) for x in rows]
                game_data = [json.loads(val) for val in raw_values if val is not None]
            else:
                # Use the legacy database when Entitlements.sqlite is not available.
                game_data = self._owned_games_db.select('DbSet', rows=['ProductIdStr', 'ProductTitle'])
                if game_data is None:
                    return None

            return {
                # row.get('ProductTitle', '') avoids KeyErrors when a database row is incomplete.
                row['ProductIdStr']: Game(row['ProductIdStr'], self._title_wrapper(row.get('ProductTitle', ''), row['ProductIdStr']), dlcs=None, license_info=LicenseInfo(LicenseType.SinglePurchase))
                for row in game_data
            }
        except Exception:
            self.logger.exception('Failed to get owned games')
            return None

    def _update_owned_games(self):
        if (time() - self._owned_games_last_updated) < OWNED_GAMES_TIMEOUT:
            return

        owned_games = self._get_owned_games()

        for game_id in self._owned_games_cache.keys() - owned_games.keys():
            self.remove_game(game_id)

        for game_id in (owned_games.keys() - self._owned_games_cache.keys()):
            self.add_game(owned_games[game_id])
        
        self._owned_games_cache = owned_games
        self._owned_games_last_updated = time()

    def _get_local_games(self):
        try:
            rows = self._local_games_db.select('DbSet', rows=['*'])
            if rows is None:
                return None
            
            self._local_game_paths = {}
            local_games = {}
            for row in rows:
                id_col = next((k for k in row.keys() if k.lower() == 'id'), 'Id')
                inst_col = next((k for k in row.keys() if k.lower() == 'installed'), 'Installed')
                dir_col = next((k for k in row.keys() if k.lower() == 'installdirectory'), None)

                if row[inst_col]:
                    game_id = row[id_col]
                    local_games[game_id] = LocalGame(game_id, LocalGameState.Installed)
                    if dir_col and row[dir_col]:
                        self._local_game_paths[game_id] = row[dir_col]

            return local_games
        except Exception:
            self.logger.exception('Failed to get local games')
            return None

    def _update_local_games(self):
        """Sync installed-game list from DB (slow, rate-limited).
        Running-state tracking is handled separately in _update_running_states."""
        if (time() - self._local_games_last_updated) < LOCAL_GAMES_TIMEOUT:
            return

        local_games = self._get_local_games()
        if local_games is None:
            self.logger.warning('Skipping local games update because the database read failed; keeping the current Galaxy library state intact.')
            return

        previous_local_games = self._local_games_cache or {}

        REMOVAL_COOLDOWN = 30
        current_time = time()

        for game_id in previous_local_games.keys() - local_games.keys():
            # Suppress removal if the game was launched very recently — the Amazon client
            # briefly empties the database during startup, which would otherwise cause
            # a false uninstall report while the game is still launching.
            if (current_time - self._game_launch_times.get(game_id, 0)) < REMOVAL_COOLDOWN:
                local_games[game_id] = previous_local_games[game_id]
                continue
            self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))
            self._game_launch_times.pop(game_id, None)

        for game_id, local_game in local_games.items():
            prev = previous_local_games.get(game_id)
            if prev and (prev.local_game_state & LocalGameState.Running):
                local_game.local_game_state |= LocalGameState.Running
            if prev is None:
                self.update_local_game_status(local_game)
            local_games[game_id] = local_game

        self._local_games_cache = local_games
        self._local_games_last_updated = time()

    def _game_running_by_path(self, install_directory: str) -> bool:
        try:
            install_loc = os.path.normpath(install_directory).lower()
            if not install_loc.endswith(os.sep):
                install_loc_check = install_loc + os.sep
            else:
                install_loc_check = install_loc

            from galaxy.proc_tools import process_iter
            for proc in process_iter():
                if proc.binary_path:
                    proc_path = os.path.normpath(proc.binary_path).lower()
                    if proc_path.startswith(install_loc_check):
                        return True
        except Exception:
            self.logger.exception('Error checking if game is running by path')
        return False

    def _update_running_states(self):
        """Fast running-state check, runs every RUNNING_CHECK_INTERVAL seconds,
        fully independent of the slow 60s DB sync."""
        if self._local_games_cache is None:
            return
        if (time() - self._last_running_check) < RUNNING_CHECK_INTERVAL:
            return

        LAUNCH_COOLDOWN = 45
        current_time = time()

        for game_id, local_game in self._local_games_cache.items():
            recently_launched = (current_time - self._game_launch_times.get(game_id, 0)) < LAUNCH_COOLDOWN
            
            is_running = False
            if self._local_game_paths and game_id in self._local_game_paths:
                is_running = self._game_running_by_path(self._local_game_paths[game_id])
            
            if not is_running:
                is_running = self._client.game_running(game_id)

            should_be_running = is_running or recently_launched
            currently_running = bool(local_game.local_game_state & LocalGameState.Running)

            if should_be_running != currently_running:
                # Track running state transitions to calculate active playtime sessions.
                if should_be_running and not currently_running:
                    # Session started: record the launch timestamp.
                    self._active_sessions[game_id] = current_time
                    self.logger.info(f"Playtime tracking: Session started for game {game_id}")
                elif not should_be_running and currently_running:
                    # Session ended: calculate the duration and round to the nearest minute.
                    start_time = self._active_sessions.pop(game_id, None)
                    if start_time:
                        duration_mins = round((current_time - start_time) / 60)
                        if duration_mins > 0:
                            time_key = f"time_{game_id}"
                            last_key = f"last_{game_id}"
                            
                            current_total = int(self._load_cache(time_key, 0))
                            new_total = current_total + duration_mins
                            end_timestamp = int(time())
                            
                            # Persist the newly captured playtime statistics to the cache.
                            self._save_cache(time_key, new_total)
                            self._save_cache(last_key, end_timestamp)
                            
                            # Publish the active playtime session to GOG Galaxy immediately.
                            self.update_game_time(GameTime(game_id, new_total, end_timestamp))
                            self.logger.info(f"Playtime tracking: Session ended for game {game_id}. Added {duration_mins} mins. Total: {new_total} mins.")

                if should_be_running:
                    local_game.local_game_state |= LocalGameState.Running
                else:
                    local_game.local_game_state &= ~LocalGameState.Running

                self._local_games_cache[game_id] = local_game
                self.update_local_game_status(local_game)

        self._last_running_check = current_time

    @staticmethod
    def _scheme_command(command, game_id):
        webbrowser.open(f'amazon-games://{command}/{game_id}')

    async def _ensure_initialization(self):
        await asyncio.sleep(FALLBACK_SYNC_TIMEOUT)

        if not self._client.is_installed:
            return

        if not self._local_games_cache:
            self.logger.info('Fallback initialization of `_local_games_cache`')
            self._local_games_cache = {}

        if not self._owned_games_cache:
            self.logger.info('Fallback initialization of `_owned_games_cache`')
            self._owned_games_cache = {}

    # Galaxy plugin methods.

    async def authenticate(self, stored_credentials=None):
        self.logger.info("Plugin authenticate")

        if not stored_credentials:
            return create_next_step(START_URI.SPLASH, END_URI.SPLASH_CONTINUE)

        return self._on_auth()

    async def pass_login_credentials(self, step, credentials, cookies):
        if any(x in credentials['end_uri'] for x in ['splash_continue', 'missing_app_retry']):
            if not self._client.is_installed:
                return create_next_step(START_URI.MISSING_APP, END_URI.MISSING_APP_RETRY)

            return self._on_auth()

        return create_next_step(START_URI.SPLASH, END_URI.SPLASH_CONTINUE)

    async def get_owned_games(self):
        if not await self._auth_finished():
            return []

        if self._owned_games_cache is None:
            self._owned_games_last_updated = time()
            owned_games = self._get_owned_games()
            if owned_games is not None:
                self._owned_games_cache = owned_games
        return list((self._owned_games_cache or {}).values())

    async def get_local_games(self):
        if not await self._auth_finished():
            return []

        if self._local_games_cache is None:
            self._local_games_last_updated = time()
            local_games = self._get_local_games()
            if local_games is not None:
                self._local_games_cache = local_games
        return list((self._local_games_cache or {}).values())

    def handshake_complete(self) -> None:
        self.create_task(self._ensure_initialization(), '_ensure_initialization')

    def tick(self):
        current_time = time()
        if not self._client.is_installed:
            if (current_time - self._last_install_check) > 60:
                self._client.update_install_location()
                self._last_install_check = current_time
        else:
            if (current_time - self._last_install_check) > 5:
                self._client.update_install_location()
                self._last_install_check = current_time

        if self._client.is_installed:
            if self._owned_games_db and self._owned_games_cache is not None:
                self._update_owned_games()

            if self._local_games_db:
                if self._local_games_cache is None:
                    local_games = self._get_local_games()
                    if local_games is not None:
                        self._local_games_cache = local_games
                else:
                    self._update_local_games()
                
                self._update_running_states()

    async def launch_game(self, game_id):
        AmazonGamesPlugin._scheme_command('play', game_id)
        self._game_launch_times[game_id] = time()
        
        # Record the launch timestamp as soon as playtime tracking starts.
        self._active_sessions[game_id] = time()
        
        if self._local_games_cache is not None and game_id in self._local_games_cache:
            local_game = self._local_games_cache[game_id]
            local_game.local_game_state |= LocalGameState.Running
            self._local_games_cache[game_id] = local_game
            self.update_local_game_status(local_game)

    async def uninstall_game(self, game_id):
        self.logger.info(f'Uninstalling game {game_id}')
        result = await self._client.uninstall_game(game_id)
        if result:
            self.update_local_game_status(LocalGame(game_id, LocalGameState.None_))
            if self._local_games_cache is not None:
                self._local_games_cache.pop(game_id, None)

    async def launch_platform_client(self):
        self._client.start_client()

    async def shutdown_platform_client(self):
        self._client.stop_client()

    async def get_os_compatibility(self, game_id, context):
        return OSCompatibility.Windows

    async def get_game_time(self, game_id: str, context) -> GameTime:
        """
        Retrieves the accumulated total playtime and last played timestamp for GOG Galaxy.
        """
        time_key = f"time_{game_id}"
        last_key = f"last_{game_id}"
        
        time_played = self._load_cache(time_key, None)
        last_played = self._load_cache(last_key, None)
        
        return GameTime(
            game_id=game_id,
            time_played=time_played,
            last_played_time=last_played
        )

    @property
    def features(self) -> List[Feature]:
        return [x for x in list(self._features) if x not in [Feature.InstallGame]]

def main():
    create_and_run_plugin(AmazonGamesPlugin, sys.argv)


# Start the plugin event loop.
if __name__ == "__main__":
    main()