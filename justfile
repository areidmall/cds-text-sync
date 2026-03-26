# just file to run saved commands
# If `just` is not recognised as a command you can install with `winget install --id Casey.Just --exact --scope user`
# Then when installed and shell restarted in this top level directory run `just <command>`. The commands are run in shell defined below. 

set shell := ["powershell.exe", "-c"]
scriptdir :=  "~/AppData/Local/CODESYS/ScriptDir/"
scriptdir18 :=  "c:/Program Files/CODESYS 3.5.18.0/CODESYS/ScriptDir/"

# Powershell script to install the scripts in script dir
install:
    Push-Location {{scriptdir}}; \
    ls; \
    rm Project_*.py
    ls *.py | foreach { copy $_ -Destination {{scriptdir}} -Force }
    # Don't have rights to run this
    @# ls *.py | foreach { copy $_ -Destination "{{scriptdir18}}" -Force } 

pull-upstream:
    git fetch upstream 
    git checkout main
    git merge upstream/main
