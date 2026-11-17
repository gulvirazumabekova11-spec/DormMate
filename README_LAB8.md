# DormMate — №8 зертханалық жұмысқа дайын қосымша пакет

Бұл ZIP — **бұрынғы GitHub DormMate жобасына ҚОСЫЛАТЫН** файлдар. Бұрынғы `app/`, `ui.py`, `test_api.py`, `conftest.py` файлдарын ауыстырмаңыз. Себебі GitHub-тегі репозиторий ZIP-ын осы ортаға толық жүктеу мүмкін болмады.

## Орнату
1. GitHub репозиторийінен `Code → Download ZIP` арқылы ескі DormMate-ті алыңыз, архивтен шығарыңыз.
2. Осы пакеттегі **`.github/` және `lab8/`** папкаларын бұрынғы жобаның түбіріне көшіріңіз.
3. VS Code-та ескі DormMate түбірін ашып, терминалға енгізіңіз:

```powershell
py -m pip install -r requirements.txt
py -m pip install locust bandit
py -m pytest -v --junitxml=lab8-results.xml
py -m bandit -r app
```

## Жүктемелік тест (жергілікті сервер)
Бірінші терминал:
```powershell
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Екінші терминал (сценарийлерді **бір-бірден**, тек өз серверіңде орында):
```powershell
py -m locust -f lab8/locustfile.py --headless -u 5 -r 1 -t 1m --host http://127.0.0.1:8000 --csv lab8/results/users5
py -m locust -f lab8/locustfile.py --headless -u 20 -r 2 -t 2m --host http://127.0.0.1:8000 --csv lab8/results/users20
py -m locust -f lab8/locustfile.py --headless -u 50 -r 5 -t 3m --host http://127.0.0.1:8000 --csv lab8/results/users50
py -m locust -f lab8/locustfile.py --headless -u 100 -r 10 -t 3m --host http://127.0.0.1:8000 --csv lab8/results/users100
```

CPU/RAM: Windows Task Manager → Processes немесе Performance бетінен өлшеп, скриншот алыңыз. Locust оларды серверден автоматты оқымайды.

## GitHub Actions
Көшірген файлдарды GitHub-қа жүктеңіз. `Actions` қойындысынан **DormMate Lab 8 - Tests and Security** workflow нәтижесін қараңыз. Жасыл белгі шықпайынша жұмыс өтті деп жазбаңыз.

## HTTP әдісі туралы
Бұрынғы DormMate `PUT` емес, `PATCH` әдісін қолданады. FastAPI-дағы қате JSON/валидация жағдайлары — көбінесе 422, жалпы тапсырмадағы 400 емес.

## Нақты статус
Пакет файлдарының синтаксисі тексеріледі; бастапқы жоба және GitHub Actions/Locust толық орындалған жоқ. Нәтижелерді ойдан шығармаңыз, нақты іске қосқаннан кейін `lab8/docs/ЕСЕП_ҮЛГІСІ.md` толтырыңыз.
