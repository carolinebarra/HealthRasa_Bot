# HealthRasa_Bot

To use it first activate the virtual environment. Important to double check of version of python is running.
≈python --version
3.7.0
# Windows
# You can also use py -3 -m venv .venv
≈ python -m venv .venv
# Try to Activate.ps1 if doesn't work like that
![image](https://user-images.githubusercontent.com/52780972/162270796-382305f8-7523-4186-bd4e-e1a1011474ee.png)
≈Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
≈./.venv/Scripts/activate
#then
≈pip install -r requirements.txt

to test chat bot:

#First need to make sure to run action with one terminal
rasa run actions
#Another terminal with
rasa shell
