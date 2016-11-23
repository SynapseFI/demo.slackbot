# misc.slackbot

Synapse's file compression and storage service.


###### Slack Interface
See [samples.md](/samples.md).


###### To Run (Docker)

To build:
```
docker build --rm -t misc.slackbot .
```

To run:
```
docker run -d -p 89:80 -v $(pwd)/app:/app --name=misc.slackbot misc.slackbot
```


###### App Structure

```
├── app
│   ├── app.py
│   ├── commands.py
│   ├── config.py
│   ├── core/
│   ├── db.py
│   ├── models.py
│   ├── run.py
│   ├── schema.sql
│   ├── static/
│   │   ├── jquery-3.1.1.min.js
│   │   ├── register.css
│   │   ├── register.js
│   │   └── spin.min.js
│   ├── synapse_bot.py
│   ├── synapse_client.py
│   └── templates
│       └── register.html
```
