import hmac
import hashlib

message = b"smashthestate"

with open("users.txt") as f:
    for username in f:
        username = username.strip()

        digest = hmac.new(
            username.encode(),
            message,
            hashlib.md5
        ).hexdigest()

        print(f"{username} -> {digest[:8]}")

  # Before running this script, create a users.txt file and add all the Bad Actors names discovered on the website, one username per line.
