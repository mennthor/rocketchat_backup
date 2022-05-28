# coding: utf-8

"""
Script to backup private messages from RocketChat using the rocketchat_API
wrapper.
"""

import os
import sys
import json
import getpass
import argparse
from requests import sessions

from rocketchat_API.rocketchat import RocketChat
from rocketchat_API.APIExceptions.RocketExceptions import RocketAuthenticationException


def argsort(arr):
    """ Non-numpy argsort version (similar to C++ sort comparator) """
    def comp(enum):
        """ Comparator getting tuples (idx, value), returns value for sort """
        return enum[1]

    # Sort enum tuples via value, but output index
    return [i for i, _ in sorted(enumerate(arr), key=comp)]


def sort_msg_by_ts(msgs):
    """ Sort list of message dicts by timestamp """
    ts = [msg["ts"] for msg in msgs]
    sorted_idx = argsort(ts)
    sorted_msgs = [msgs[i] for i in sorted_idx]
    # Return sorted descending, as the API does too (latest msg is first)
    return sorted_msgs[::-1], sorted_idx[::-1]


def main():
    parser = argparse.ArgumentParser(
        description="Script to backup RocketChat messages from private IM "
        "chats. Messages are stored in JSON format in "
        "`__file__/rocketchat_saved_ims`. Note: Mostly untested, use at own "
        "risk, don't solely rely on it ;)")
    parser.add_argument("username")
    parser.add_argument(
        "-i", action="store_true", dest="incremental",
        help="If given, checks if a backup file for any encountered chats is "
        "already present in the backup storage folder. If so, only load "
        "messages not present in the existing backup file."
        )
    args = parser.parse_args()

    GWDG_SERVER = "https://chat.gwdg.de"
    STORAGE_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "rocketchat_saved_ims")
    if not os.path.isdir(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)

    # Prompt for password to avoid storing / writing it in plaintext
    user = args.username
    passwd = getpass.getpass(
        prompt="Provide password for rocketchat user '{}': ".format(user))

    with sessions.Session() as session:
        try:
            rocket = RocketChat(
                user, passwd, server_url=GWDG_SERVER, session=session)
        except RocketAuthenticationException:
            sys.exit("Invalid credentials for user '{}', exiting...".format(user))

        print("{}acking up RocketChat ('{}') IM messages for '{}' to '{}'\n".format(
              "Incrementally b" if args.incremental else "B",
              GWDG_SERVER, user, STORAGE_PATH))

        # Retrieve and parse list of direct message rooms the user is involved in
        # API point: https://docs.rocket.chat/api/rest-api/methods/im/list
        im_list = rocket.im_list().json()
        # Filter out the own chat, where only the user is present (storage-chat)
        chats = [d for d in im_list["ims"] if len(d["usernames"]) > 1]

        # Retrieve history from every room we got above
        # API point: https://docs.rocket.chat/api/rest-api/methods/im/history
        for chat in chats:
            # File is named with the other user(s) in the chat
            other_user = [u.replace(".", "_")
                          for u in chat["usernames"] if u != user]
            fname = "im_" + "_".join(other_user) + ".json"
            fpath = os.path.join(STORAGE_PATH, fname)

            print("# Handling chat history with '{}'".format(", ".join(other_user)))

            # Get IM room info, extract number of total msgs and use existing file
            # to calculate the numer of new messages to fetch
            counters = rocket.im_counters(room_id=chat["_id"]).json()
            try:
                n_tot_msgs = counters["msgs"]
            except KeyError:
                print("- No messages found for this chat, skipping...")
                continue

            # Check existing file to avoid reloading all messages
            # Note: What if older msgs are edited? Then this fails.
            # Note: This may also break, if there is a max history size on the
            #       RocketChat servers, then we may miss msgs
            # Maybe it's better to load all available msgs everytime and append
            # those not present in the already saved file?
            existing_msgs = None
            n_existing_msgs = 0
            if args.incremental and os.path.isfile(fpath):
                with open(fpath, "r") as infile:
                    existing_msgs = json.load(infile)

                n_existing_msgs = len(existing_msgs["messages"])
                print("- Found existing history ({} msgs) in '{}'"
                      .format(n_existing_msgs, fpath))
                n_tot_msgs -= n_existing_msgs

            if n_tot_msgs is None or n_tot_msgs < 1:
                print("- No (new) messages found for this chat, skipping...")
                continue

            # Get new msgs
            im_hist = rocket.im_history(
                chat["_id"], count=n_tot_msgs, inclusive="true").json()
            if not im_hist["success"]:
                print("Error retrieving messages from chat, skipping...")
                continue

            # If file already exists and we load only new msgs, do some msg ID
            # checks to avoid storing duplicates
            if existing_msgs is not None:
                # Sort to ensure proper time order (API is returning sorted but we
                # can ensure this explicitely)
                existing_msgs_sorted = sort_msg_by_ts(existing_msgs["messages"])[0]
                im_hist_msgs_sorted = sort_msg_by_ts(im_hist["messages"])[0]
                # from IPython import embed; embed()
                latest_existing = existing_msgs_sorted[-1]["ts"]
                im_hist_msgs_sorted = [msg for msg in im_hist_msgs_sorted
                                       if msg["ts"] != latest_existing]

                # Prepend to existing msgs
                im_hist["messages"] = im_hist_msgs_sorted + existing_msgs_sorted

            # Dump to JSON
            print("- Saving {} new messages ({} total) to chat history '{}'"
                  .format(n_tot_msgs, n_tot_msgs + n_existing_msgs, fpath))
            with open(fpath, "w") as outf:
                json.dump(im_hist, outf, indent=2)

    print("\nDone")


if __name__ == "__main__":
    main()
