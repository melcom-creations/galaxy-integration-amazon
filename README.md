# ⚔️ Battle.net Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This repository contains the Battle.net integration plugin for the 64-bit version of GOG Galaxy 2.1+.

The original community integration has been updated to work with the current 64-bit GOG Galaxy client and Python 3.13. This version includes compatibility updates, dependency updates, stability improvements, bug fixes, and ongoing maintenance.

---

## ✨ Features

- Compatible with GOG Galaxy 2.1+ (64-bit)
- Python 3.13 support
- Updated 64-bit dependencies
- Battle.net local client integration
- Automatic setup flow via setup.html
- Warcraft III Classic information pages (EN + DE)
- Ongoing maintenance and stability improvements

---

## 📦 Installation

### Standard Installation (Recommended)

1. Close GOG Galaxy completely.
2. Download the latest release from this repository.
3. Open the following folder:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
````

4. Extract the ZIP archive **directly into this folder**.

After extraction, the structure must look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── battlenet_ba170431-0649-482f-863b-d248592f1842\
    ├── manifest.json
    ├── plugin.py
    ├── setup.html
    ├── wc3_classic_info.html
    ├── wc3_classic_info_DE.html
    └── ...
```

5. Start GOG Galaxy.

---

## ⚙️ First Login / Setup Flow (IMPORTANT)

On first login, the plugin will automatically open `setup.html`.

This setup page is required to complete authentication and initialization.

The setup process will remain active until the required Battle.net credentials are stored in:

```text
consts.py
```

Specifically:

```python
CLIENT_ID = ""
CLIENT_SECRET = ""
```

Once valid values are set, the setup page will no longer be shown and the plugin will proceed normally.

If these values are missing or empty, the setup page will continue to appear on each startup.

---

## 🌍 Warcraft III Classic Information Pages

This plugin includes additional informational HTML pages:

* `wc3_classic_info.html`
* `wc3_classic_info_DE.html`

The German version (`_DE`) is included for localized users.

These pages can also be accessed directly from the plugin directory after installation.

---

## 🔄 Resetting the Plugin Database (Recommended)

If the plugin behaves unexpectedly after an update, reset the local plugin database:

1. Open:

```text
C:\ProgramData\GOG.com\Galaxy\storage\plugins\
```

2. Locate files beginning with:

```text
battlenet_
```

and ending with:

```text
-storage.db
```

3. Rename each file by appending `.old`.

Example:

```text
battlenet_xxxxxxxxx-storage.db
```

becomes

```text
battlenet_xxxxxxxxx-storage.db.old
```

4. Restart GOG Galaxy.
5. Reconnect Battle.net integration if needed.

---

## ⚠️ Important

Do **not** keep backup copies of this plugin inside the `plugins\installed` directory.

Duplicate plugin folders may lead to GUID conflicts or cause outdated versions to be loaded by GOG Galaxy.

---

## 🙏 Credits

**Original Community Integration**
Friends of Galaxy
https://github.com/FriendsOfGalaxy/galaxy-integration-battlenet

**Battle.net API / Integration Work**
Community contributors

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

📩 https://melcom-creations.github.io/melcom-music/contact.html

Thank you for your patience and support!
