# special_agent
Experiments in connecting agents, memory management, communication, team work and love

# homework scheduler, awareness, organizer and tutor
* Provide a data secure way to automate the process of keeping track
of homework assignments for the family while sharing the information
to crate tutors based on the homework

## set up your gmail app password
* app password allows a less secure app to access gmail
* it is a 16-digit passcode
* put the code in .env

## installation
### run the installer to setup ollama, pull the models and setup venv
### with python dependencies
```
bash setup/install.bash
```

## running the code
### 1. Start Ollama (leave this terminal open)
```
ollama serve
```

### 2. In another terminal
```
cd "${HOME}/projects/special_agent/"
source venv/bin/activate
chainlit run ui/app.py -w
```