# RocketChat IM Backup

This script provides simple functionality to backup messages in JSON format from private chats (IM) from RocketChat servers.
**Note: Script is a draft version, may fail or be unreliable.**

## Prerequisites

You'll need Python3 and to install the `rocketchat-API` module eg. via

```
pip install --user rocketchat-API
```

The API module is a wrapper around the [RocketChat REST API](https://docs.rocket.chat/api/rest-api).

## Usage

For now, invoke the script with

```
$ python rocketchat_save_im_history.py [-i] <username>
```

where `<username>` is your RocketChat (GWDG) user name (usually `prename.surname` and the optional switch `-i` (incremental) can be given to attempt incremental backups, without downloading all messages over and over (not sure if this is necessary, but maybe there are limitations on how frequent the underlying RocketChat REST API can be queried).

It then prompts for your password (securely using `getpass()`) and (hopefully) scans the server for your private IM messages in your direct message chat rooms.
If any are found, they are fetched and stored in the folder `rocketchat_saved_ims` next to this script.

If you want, you could use the stored JSON files to create HTML files with a nice chat room layout for easier readability afterwards.
