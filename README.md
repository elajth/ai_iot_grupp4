# ai_iot_grupp4
Grupparbete inom AI och IoT kursen\
\
git clone ...\
\
Create venv\
python -m venv .venv\
\
Start venv\
.\venv\Scripts\Activate\
\
Install requirements\
python -m pip install requirements.txt\
\
Start image api\
uvicorn image_api:app --host 0.0.0.0 --port 8000 --reload\
\
goto website\
http://127.0.0.1:8000/get_image\
