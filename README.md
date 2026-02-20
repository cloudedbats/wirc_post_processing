# WIRC-post-processing

Post-processing for videos produced by the WIRC-2026 system.

## Installation

Instruction for Linux/macOS users:

    git clone https://github.com/cloudedbats/wirc_post_processing.git
    cd wirc_post_processing
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Instruction for Windows users
(where Python is installed at "C:\Python313\"):

    git clone https://github.com/cloudedbats/wirc_post_processing.git
    cd wirc_post_processing
    C:\Python313\python.exe -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## Run the software in CLI mode.

    cd wirc_post_processing
    source venv/bin/activate # For Linux/macOS.
    # venv\Scripts\activate # For Windows.
    python wirc_postproc_cli.py

CLI means Command Line Interface and it will look something like this:

    > python3 wirc_postproc_cli.py
    
    WIRC Post Processing
    --------------------
    Select configuration file
    by entering line number.
    Ctrl-C to terminate.
    
    1    workflow_standard.yaml
    
    Execute row [1]: 

## Create an executable file

This is about how to create an executable file for people who
don't want to use Python.

    # Skip this if already done.
    cd wirc_post_processing
    source venv/bin/activate # For Linux/macOS.
    # venv\Scripts\activate # For Windows.

    # Create the executable.
    pyinstaller wirc_postproc_cli.spec

The produced executable is to be found here: "dist".
