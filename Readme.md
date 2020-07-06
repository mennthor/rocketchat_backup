# RocketChat IM Backup

This Python script provides simple functionality to backup messages in JSON format from private chats (IM) from RocketChat servers.

**Note: The script is a draft version, may fail or be unreliable. The rocketchat URL from my institute is hardcoded, but you can easily change it or make it an CLI argument.**

## Prerequisites

_Note: The following commands are assumed to be executed in the cloned repo folder._

You'll need Python 3 to execute this script (Python 2 may work too, but I never tested it).

The projects dependencies can be managed by the [poetry package manager](https://python-poetry.org/) through the `pyproject.toml` file, although you'll only need the `rocketchat-API` module (see below for non-poetry setup).
If you have poetry, you can run

```bash
$ poetry install
```

### Manual

You'll need to install the `rocketchat-API` module eg. via

```bash
$ pip install --user rocketchat-API
```

The API module is a wrapper around the [RocketChat REST API](https://docs.rocket.chat/api/rest-api).

## Usage

Invoke the backup script with

```bash
$ poetry run python rocketchat_save_im_history.py [-i] <username>
```

or if not using poetry, use

```bash
$ python rocketchat_save_im_history.py [-i] <username>
```

directly.

Here `<username>` is your RocketChat user name (for my institute it's `prename.surname`) and the optional switch `-i` (incremental) can be given to attempt incremental backups, without downloading all messages over and over (not sure if this is necessary, but maybe there are limitations on how frequent the underlying RocketChat REST API can be queried).

It then prompts for your password (securely using `getpass()`) and (hopefully) scans the server for your private IM messages in your direct message chat rooms.
If any are found, they are fetched and stored in the folder `rocketchat_saved_ims` next to this script.

If you want, you could use the stored JSON files to create HTML files with a nice chat room layout for easier readability afterwards.
