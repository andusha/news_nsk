1. для начала нужно создать виртуальное окружение.

2. если создала виртуалку, открой папку с виртуалкой в терминале и пиши pip install -r requirements.txt

3. после заходишь через терминал в папку frontend > cd frontend
и пишешь в терминале > npm install 

4. дальше тебе понадобиться 2 терминала.
В 1 ты должна быть в основной папке проекта. В 2 в папке frontend
В 1 пишешь > env FLASK_APP=app.py flask run
В 2 пишешь > npm run watch

вот и все, теперь ты можешь зайти на сайт по ссылке из 1 терминала

а нихуя, не все. Чтоб фласк запустился без ошибок придется еще пошаманить.

в файле по этому пути > .venv/lib/python3.10/site-packages/flask_uploads.py
строчку from werkzeug import secure_filename, FileStorage меняем на from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
