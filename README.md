# ampfactor-demo-client
Demo client script to trigger aristotle ampfactor service and wait for response.

## Running the script

### Setting up virtual environment
Create virtual environment
```bash
python -m venv env
```

Activate virtual environment, on windows:
```bash
.\env\Scripts\activate
```
or on linux:
```bash
source env/bin/activate
```

Install dependencies inside virtual environment
```bash
pip install -r requirements.txt
```

### Getting credentials
Configuration parameters in the top of the script contain some secrets that
should not be added to source control. These instead contain placeholders
(`<REPLACE_ME>`). The contents of these need to be provided separately.


### Running the script
Make sure the virtual environment is activated, then run:
```
python demo_client.py <job_id>
```
where `<job_id>` is replaced with the integer job id from HySEA. 
The script has been tested with job_id `16761`.
