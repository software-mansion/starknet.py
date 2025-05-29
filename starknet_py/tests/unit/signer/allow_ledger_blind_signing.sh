#!/bin/sh

curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/right # Go to version screen
curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/right # Go to settings screen
curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/both # Go to blind signing screen
curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/both # Allow blind signing
curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/left # Go to "Back" screen
curl -d '{"action":"press-and-release"}' http://127.0.0.1:5001/button/both # Return to main screen
