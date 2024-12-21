# IOT Project

Assuming you have `python3-virtualenv` or equivelnt installed on your system, run the following commands while inside
the local repository to create the virtual Python environment

```shell
virtualenv ./.venv/
```

then activate the environment and install packages

```shell
# in bash
source ./.venv/bin/activate

# or, in fish
source ./.venv/bin/activate.fish

pip install -r requirements.txt
```
## Running

In the Python virtual envirnoment

```
# in one terminal window, start the server
python3 api/flask_server.py

# then in another one run
python3 main.py
```

Finally, open your this URL in your browser: `http://<rpi-ip>:8765`
