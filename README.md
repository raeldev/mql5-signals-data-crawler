Basic project to extract all public signals information.

### Prerequisites:
  - Docker

### Run with Docker
  - Run this command at folder `docker compose up`
  - Start crawler with `python3 main.py`

### Run without Docker
  - You'll needs python3
  - Clone repo
  - Configure some mongoDb with database "crawler" and collection "mql5signal", replace at line 16 of "main.py" file
  - Run this command at folder `pip3 install -r requirements.txt`
  - Start crawler with `python3 main.py`

### Features
- Made with sync approach
- Supports continue stopped job
- Supports to configure limit of days to ignore sync
- It's uses delay on each request (to prevent ngix block)

### ToDo:
- Use type constructor instead dictionary objects
- Add Python container in docker-compose
- Get Risks Data
- Get login protected data like Trading History

_I'm not a python expert and I do it to learn._
