# Amazon Games Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This repository contains the Amazon Games integration plugin for the native 64-bit version of GOG Galaxy 2.1+. It is based on the original community integration and has been updated for the current GOG Galaxy client and Python 3.13. The project includes updated dependencies, compatibility fixes, stability improvements, and ongoing maintenance.

---

## ✨ Features

* Imports your owned Amazon Games library into GOG Galaxy
* Detects locally installed Amazon Games titles
* Launches and uninstalls games through the Amazon Games app
* Tracks game time for games launched through the integration
* Supports GOG Galaxy 2.1+ 64-bit and Python 3.13
* Includes updated dependencies, compatibility fixes, and stability improvements

---

## 📦 Installation

### Automatic Installation with Plugin Updater (Recommended)

The easiest way to install the Amazon Games integration is with the [melcom GOG Galaxy Plugin Updater](https://github.com/melcom-creations/galaxy-integrations-64bit/tree/main/tools/melcom-galaxy_plugin_updater). The updater detects existing integrations and can install any supported melcom plugins that are still missing.

1. Download and extract the Plugin Updater.
2. Double-click `update-plugins.bat`.
3. Select your preferred language.
4. Follow the displayed instructions.

### Manual Installation

1. Close GOG Galaxy completely and make sure it is no longer running in the system tray.
2. Download the latest release package from this repository.
3. Extract the ZIP archive directly into:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
```

The resulting directory structure must look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── amazon_c2cd2e29-8b02-35a9-86fc-3faf90255857\
    ├── manifest.json
    ├── plugin.py
    ├── README.md
    └── ...
```

4. Continue with **First Start and Initial Sync** below.

---

## 🚀 First Start and Initial Sync

For the first synchronization after installing or updating the plugin:

1. Start the Amazon Games app and keep it open.
2. Start GOG Galaxy.
3. Connect the Amazon Games integration through **Settings -> Integrations** if necessary.
4. Open the account menu in the top-right corner and select **Sync integrations**.
5. Wait until the synchronization has finished.

---

## 🔄 Resetting the Plugin Database (Troubleshooting)

Reset the local plugin database only if the integration behaves unexpectedly or synchronization problems continue after restarting both applications.

1. Close GOG Galaxy completely.
2. Open `C:\ProgramData\GOG.com\Galaxy\storage\plugins\`.
3. Find every file starting with `amazon_` and ending in `-storage.db`.
4. Rename each matching file by appending `.old`, for example:

   `amazon_xxxxxxxxx-storage.db` -> `amazon_xxxxxxxxx-storage.db.old`

5. Start the Amazon Games app and keep it open.
6. Start GOG Galaxy and reconnect the Amazon Games integration if necessary.
7. Open the account menu in the top-right corner and select **Sync integrations**.
8. Wait until the synchronization has finished.

---

## ⚠️ Important

Do **not** place backup copies of this plugin inside the `plugins\installed` directory.

GOG Galaxy scans every folder inside this directory during startup. Duplicate plugin folders can lead to GUID conflicts or cause Galaxy to load an outdated version of the plugin.

---

## 🙏 Credits

**Original Community Integration**  
Rall3n  
[galaxy-integration-amazon](https://github.com/Rall3n/galaxy-integration-amazon)

**64-bit Port, Maintenance and Improvements**  
melcom

---

## ❤️ Special Thanks

I want to take a moment to thank the people who kept me going during this intense development phase:

* A huge thank you to my friend [**Hustlefan**](https://www.gog.com/u/Hustlefan). Over the past few days, you've been much more than just moral support. You gave me the encouragement I needed, patiently put up with all my Discord spam, and helped beta test the plugins. I'm really happy that you're pleased with the results. Thanks so much for all your support, my friend.

* And a big thank you to my girlfriend [**Florence H.** (fl0H0815)](https://www.gog.com/u/Florence_Heart). While she was enjoying the good life at her parents' place - complete with air conditioning and a huge swimming pool - she kept my spirits up by sending me photos of herself, her friends, her parents, and even her parents' dog. She reminded me that there's a wonderful world outside of a code editor every now and then... 🙈

  *Now that's what I call real support.* ❤️

Thank you both for having my back!

---

## 🤝 Support & Feedback

This project is developed and maintained by one person. Response times may vary, especially during periods when health-related limitations reduce available development time.

**GitHub Issues are intentionally disabled.**

If you would like to report a bug or suggest an improvement, please use the contact form on my website:

📩 [Contact form](https://melcom-creations.github.io/melcom-music/contact.html)

Thank you for your patience and support!
