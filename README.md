# ai_iot_grupp4
Grupparbete inom AI och IoT kursen\
\
git clone\
python -m venv .venv\
.\venv\Scripts\Activate\
python -m pip install requirements.txt\
uvicorn image_api:app --host 0.0.0.0 --port 8000 --reload\
goto http://127.0.0.1:8000/get_image\
