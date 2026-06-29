# Changelog

## Version 2.1.3-64bit

### Overview
Maintenance release. Rebuilt all third-party dependencies as clean 64-bit wheels for Python 3.13 via `melcom's Galaxy Plugin Scout v1.1.9`.

### Changed
- **Dependency rebuild:** All third-party packages in `/modules/` were removed and reinstalled as verified 64-bit (`cp313-win_amd64`) wheels. All packages now carry proper `.dist-info` metadata.
- **`galaxy_plugin_api` now pip-managed:** The GOG Galaxy Plugin API (`galaxy/`) is now installed and updated via `pip install galaxy_plugin_api` instead of being treated as static bundled code.

### Packages rebuilt (64-bit)
`aiohappyeyeballs`, `aiohttp`, `aiosignal`, `async_timeout`, `attrs`, `certifi`, `frozenlist`, `galaxy_plugin_api`, `idna`, `multidict`, `propcache`, `psutil`, `yarl`

---

## Version 2.1.2-64bit

### Overview
Maintenance release. Rebuilt all third-party dependencies as clean 64-bit wheels
for Python 3.13 and removed an unused library from `/modules/`.

### Changed
- **Dependency rebuild:** All third-party packages in `/modules/` were removed and
  reinstalled as verified 64-bit (`cp313-win_amd64`) wheels via
  `melcom's Galaxy-Aligner-Toolkit v3.1.4`. All packages now carry proper
  `.dist-info` metadata, enabling fully automatic dependency management in future
  maintenance runs.
- **Removed `charset_normalizer`:** Identified as unused by static import analysis
  (`melcom's Clean-Modules v1.4.7`). `aiohttp` does not require it when `idna` is
  present.

### Packages rebuilt (64-bit)
`aiohappyeyeballs`, `aiohttp`, `aiosignal`, `async_timeout`, `attrs`, `certifi`,
`frozenlist`, `idna`, `multidict`, `propcache`, `psutil`, `yarl`

---

## Version 2.1.1-64bit

### Overview
This release adds real-time playtime tracking (including commercial rounding) for all locally installed Amazon Games titles and introduces stable persistent-cache syncing to report accumulated hours to GOG Galaxy.

### Added
- **Real-Time Playtime Tracking:** Enabled background monitoring of running game processes. The plugin now records session start and end timestamps directly inside the existing `_update_running_states` loop and GOG-initiated `launch_game` calls, tracking last played dates and total minutes dynamically.
- **Kaufmännisch-Round Playtime:** Playtime session tracking now commercially rounds (`round()`) to the nearest minute, preventing strict truncation loss and ensuring even brief playing sessions are credited.

### Changed
- **Playtime Synchronization:** Implemented the standard `get_game_time()` interface. GOG Galaxy now automatically reads and displays locally tracked, rounded playing times from the persistent cache upon startup.

### Technical Breakdown

#### 1. Playtime Session Tracking
**Files:** `plugin.py`

Integrated active session tracking into `_update_running_states` to capture running state transitions. When a transition to running is detected (either through an in-client play action or background launch), a start timestamp is recorded. When the process terminates, elapsed minutes are calculated.

#### 2. Commercial Rounding
**Files:** `plugin.py`

Replaced strict truncation with commercial rounding (`round()`) to calculate playtime sessions. If a user plays for at least 30 seconds, it is rounded up to the nearest minute to prevent shorter playing sessions from being completely discarded.

#### 3. Persistent Cache Synchronization
**Files:** `plugin.py`

Playtime minutes and last played timestamps are securely written to GOG's local `persistent_cache`. The newly implemented `get_game_time()` method acts as a bridge to feed this data back to GOG Galaxy's user interface.

---

## Version 2.1.0-64bit

### Fixed
- **Comprehensive fix for the Purple "Play" Button issue:** Resolved multiple underlying architectural bugs where GOG Galaxy's grayed-out "Play" button prematurely reverted to purple (active) after launching a game. The following core fixes were implemented to resolve this:
  - **Direct SQLite Database Process Tracking:** Bypassed unreliable Windows Registry uninstaller strings. The plugin now queries the actual `InstallDirectory` directly from `GameInstallInfo.sqlite` (`DbSet` table) case-insensitively. This ensures older titles, DOSBox wrappers, and indie games are tracked accurately.
  - **Transient Database Empty-State Protection:** Added a database safeguard in `_update_local_games`. When the Amazon Games client briefly empties or locks the database file during game launches, the transient empty state is ignored to prevent GOG from wiping the active launch cooldown and reverting the button to purple.
  - **Startup Cache Self-Healing:** Implemented dynamic cache recovery in `tick()`. If the SQLite database is locked or inaccessible on startup, the plugin now recovers and initializes its local cache on subsequent ticks instead of remaining permanently disabled.
  - **Precise Path Boundary Checking:** Replaced basic substring matching in process detection with precise prefix-based path boundary checks (`proc_path.startswith`) to reliably monitor active executables within the game's actual folder.
  - **Case-Insensitive Product ID Extraction:** Updated the registry regex extraction pattern to support uppercase characters in game IDs, preventing games with capitalized product IDs from being skipped.

---

## Version 2.0.2-64bit

### Overview
This release reorganizes the plugin's file structure by moving third-party utility libraries and dependencies into a dedicated subfolder, keeping the root directory clean.

### Changed
- **Directory reorganization:** Moved all utility libraries and third-party dependencies from the root directory into a new `/Modules/` subdirectory.
- **Path configuration:** Updated the entry point (`plugin.py`) to automatically add `/Modules/` to the system path (`sys.path`) during startup, ensuring all dependencies are loaded correctly.

---

## Version 2.0.1-64bit

### Overview
This maintenance release focuses on stability, data consistency, and resilience inside the Amazon Games integration. The update hardens database handling, prevents accidental library removals during temporary failures, improves cache safety, and reduces the risk of synchronization issues that could otherwise cause visible library churn inside GOG Galaxy.

### Fixed
- **Database errors no longer appear as an empty library:** Temporary SQLite failures are now handled separately from valid empty results.
- **Library preservation during database faults:** Existing owned and local game data is no longer removed when the Amazon database cannot be read successfully.
- **False game removals prevented:** Synchronization paths now distinguish between missing data and unavailable data sources.
- **Cache removal hardening:** Unsafe cache removal operations were protected against missing-key scenarios.
- **KeyError crash risk reduced:** Cache update paths now safely handle inconsistent or delayed state transitions.

### Changed
- **Database result handling improved:** Error states and successful empty responses are now treated as separate outcomes.
- **Synchronization logic hardened:** Library updates are only applied when valid source data is available.
- **Local cache management improved:** Cache cleanup routines now operate defensively and avoid unnecessary exceptions.
- **Background stability improvements:** Internal update paths are more tolerant of temporary failures and data source interruptions.

### Technical Breakdown

#### 1. Database error separation
**Files:** `db_client.py`

The database layer now differentiates between a legitimate empty result and a temporary database access failure. This prevents synchronization code from interpreting read failures as a user owning zero games.

#### 2. Library synchronization protection
**Files:** `plugin.py`

Owned-game and local-game update paths now avoid destructive synchronization when source data is unavailable due to database errors. Existing Galaxy library entries remain intact until valid data becomes available again.

#### 3. Cache safety improvements
**Files:** `plugin.py`

Cache maintenance logic was updated to safely handle missing entries and prevent avoidable `KeyError` exceptions during state transitions and synchronization events.

---

## Version 2.0.0-64bit

### Overview
This release modernizes the Amazon Games integration for the 64-bit GOG Galaxy client and Python 3.13. It fixes 64-bit pointer handling during local database decryption, restores reliable 32-bit registry lookups for installed game detection, hardens client process control, and reduces background polling overhead. The result is a more stable plugin that starts cleanly, scans installed titles correctly, and avoids the crashes and regressions that affected the legacy 32-bit build.

### Added
- **64-bit client support:** The plugin is now packaged and branded as a 64-bit build for the current GOG Galaxy client environment.
- **64-bit-safe DPAPI handling:** `utils.py` now defines explicit `ctypes` argument and return types for `CryptUnprotectData`, `LocalFree`, and `memcpy` so 64-bit pointers are not truncated during local database decryption.
- **Bundled 64-bit native dependencies:** The release includes updated 64-bit compiled modules for modern Python 3.13 runtime compatibility.
- **Safer owned-game parsing:** Empty or corrupted database entries are now ignored instead of being passed blindly into JSON parsing.
- **More defensive client and process handling:** Uninstall, start, stop, and running-state checks now handle missing values and shell invocation correctly.

### Fixed
- **Fatal crashes during local database decryption:** Correct 64-bit memory handling prevents segfaults when reading protected data from the Amazon Games local database.
- **Missing game library detection:** Registry access now explicitly targets the 32-bit `Wow6432Node` view from 64-bit Python, restoring installed game detection.
- **Amazon Games App shutdown failure:** The `taskkill` call now uses a proper argument list instead of a shell string, allowing GOG Galaxy to close the app reliably.
- **Excessive CPU and registry spam:** `tick()` now rate-limits installation checks instead of querying the registry on every cycle.
- **Crashes from malformed uninstall entries:** The plugin now validates uninstall strings and install locations before using them.
- **False negatives in running-state checks:** `game_running()` now returns `False` cleanly when no matching process is found.
- **Crash risk from broken database rows:** Invalid or empty entries are skipped safely instead of failing the whole import path.

### Changed
- **`manifest.json` refreshed:** The plugin name, version, description, and author string were updated to reflect the 64-bit release.
- **`version.py` bumped to `0.6.0`:** The internal changelog now documents the 64-bit compatibility work and related fixes.
- **`plugin.py` polling logic updated:** Installation detection is now throttled to reduce background overhead.
- **`client.py` lifecycle handling improved:** Start, stop, uninstall, and installed-game discovery paths are now more defensive.
- **`utils.py` registry and crypto access modernized:** Registry reads and DPAPI calls now use explicit 64-bit-safe setup.

### Technical Breakdown

#### 1. 64-bit safe database decryption
**Files:** `utils.py`

The original build could truncate pointer-sized values when calling Windows crypto APIs from 64-bit Python. The new build defines explicit `ctypes` signatures for `CryptUnprotectData`, `LocalFree`, and `memcpy`, which keeps the decrypted buffer handling safe and stable on modern 64-bit systems.

#### 2. Installed-game detection under 64-bit Python
**Files:** `utils.py`

The plugin now opens the Windows uninstall registry with `registry.KEY_WOW64_32KEY`, which forces 64-bit Python to look in the 32-bit registry view where the Amazon Games App and classic entries are stored. This restores detection of installed games that were previously invisible.

#### 3. Client control and process management
**Files:** `client.py`

The shutdown path now passes `taskkill` as a proper argument array, and the uninstall/start helpers no longer assume that all paths or strings are present and valid. That makes app control far more reliable and prevents avoidable runtime errors.

#### 4. Background polling and import hardening
**Files:** `plugin.py`

The plugin no longer hammers the registry on every tick. It rate-limits installation checks and also protects the owned-games import path against empty, missing, or malformed database rows, which improves stability during startup and synchronization.

---

## Version 0.5.2 and Earlier
*(Legacy releases by [Rall3n](https://github.com/Rall3n) - see the [original repository](https://github.com/Rall3n/galaxy-integration-amazon/releases) for historical changelog entries.)*