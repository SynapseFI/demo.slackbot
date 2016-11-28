# misc.slackbot
Slack integration using Synapse for automated savings.


###### Slack Interface

See [samples.md](/samples.md).


###### To Run (Docker)

To build:
```
docker build --rm -t misc.slackbot .
```

To run (env args needed):
```
docker run -d -p 89:80 -v $(pwd)/app:/app -e CLIENT_ID='' -e CLIENT_SECRET='' -e FINGERPRINT='' -e SLACKBOT_TOKEN='' -e SLACKBOT_ID='' --name=misc.slackbot misc.slackbot
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
