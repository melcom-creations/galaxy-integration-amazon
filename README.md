# Amazon Games Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This repository contains the Amazon Games integration plugin for the 64-bit version of GOG Galaxy 2.1+.

The original community integration has been updated to work with the current 64-bit GOG Galaxy client and Python 3.13. In addition to compatibility improvements, this project includes dependency updates, bug fixes, stability improvements and ongoing maintenance.

---

## ✨ Features

* Compatible with GOG Galaxy 2.1+ (64-bit)
* Python 3.13 support
* Updated 64-bit dependencies
* Improved stability and compatibility
* Ongoing maintenance and bug fixes

---

## 📦 Installation

### Standard Installation (Recommended)

1. Close GOG Galaxy completely.
2. Download the latest release from this repository.
3. Open the following folder:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
```

4. Extract the ZIP archive **directly into this folder**.

The resulting directory structure **must** look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── amazon_c2cd2e29-8b02-35a9-86fc-3faf90255857\
    ├── manifest.json
    ├── plugin.py
    ├── README.md
    └── ...
```

5. Start GOG Galaxy.

### If the plugin folder is missing

If a future ZIP archive does **not** already contain the folder

```text
amazon_c2cd2e29-8b02-35a9-86fc-3faf90255857
```

perform the following steps:

1. Open:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
```

2. Create a new folder named exactly:

```text
amazon_c2cd2e29-8b02-35a9-86fc-3faf90255857
```

3. Extract **all files from the ZIP archive into this newly created folder**.

The final directory structure must look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── amazon_c2cd2e29-8b02-35a9-86fc-3faf90255857\
    ├── manifest.json
    ├── plugin.py
    ├── README.md
    └── ...
```

---

## 🔄 Resetting the Plugin Database (Recommended)

If the plugin behaves unexpectedly after an update, resetting the local plugin database is recommended.

1. Open:

```text
C:\ProgramData\GOG.com\Galaxy\storage\plugins\
```

2. Locate all files beginning with:

```text
amazon_
```

and ending with:

```text
-storage.db
```

3. Rename each database by appending `.old` to its filename.

Example:

```text
amazon_xxxxxxxxx-storage.db
```

becomes

```text
amazon_xxxxxxxxx-storage.db.old
```

4. Start GOG Galaxy again.
5. Reconnect the Amazon Games integration if necessary.

---

## ⚠️ Important

Do **not** place backup copies of this plugin inside the `plugins\installed` directory.

GOG Galaxy scans every folder inside this directory during startup. Duplicate plugin folders can lead to GUID conflicts or cause Galaxy to load an outdated version of the plugin.

---

## 🙏 Credits

**Original Community Integration**
Rall3n

https://github.com/Rall3n/galaxy-integration-amazon

**64-bit Port, Maintenance and Improvements**
melcom

---

## ❤️ Special Thanks

I want to take a moment to thank the people who kept me going during this intense development phase:

* A huge thank you to my friend **Hustlefan**. Over the past few days, you've been much more than just moral support. You gave me the encouragement I needed, patiently put up with all my Discord spam, and helped beta test the plugins. I'm really happy that you're pleased with the results. Thanks so much for all your support, my friend.

* And a big thank you to my girlfriend **Florence H. (fl0H0815)**. While she was enjoying the good life at her parents' place - complete with air conditioning and a huge swimming pool - she kept my spirits up by sending me photos of herself, her friends, her parents and even her parents' dog. She reminded me that there's a wonderful world outside of a code editor every now and then... 🙈

  *Now that's what I call real support.* ❤️

Thank you both for having my back!

---

## 🤝 Support & Feedback

This project is developed and maintained by one person. Response times may vary, especially during periods when health-related limitations reduce available development time.

**GitHub Issues are intentionally disabled.**

If you would like to report a bug or suggest an improvement, please use the contact form on my website:

📩 https://melcom-creations.github.io/melcom-music/contact.html

Thank you for your patience and support!
