# YggTorrent Tracker Fixerr

<div align="center">

[![python](https://img.shields.io/badge/python-3.14-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://www.python.org/)
[![uv](https://img.shields.io/badge/package_manager-uv-202235.svg?logo=uv&labelColor=202235&color=edb641&logoColor=edb641)](https://docs.astral.sh/uv/)
[![httpx](https://img.shields.io/badge/http_client-httpx-202235.svg?logo=web&labelColor=202235&color=edb641&logoColor=edb641)](https://www.python-httpx.org/)
[![litestar](https://img.shields.io/badge/api_server-%E2%AD%90%20_litestar-202235.svg?labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/litestar-org/litestar)
[![asyncio](https://img.shields.io/badge/task_scheduler-asyncio-202235.svg?logo=star&labelColor=202235&color=edb641&logoColor=edb641)](https://docs.python.org/3/library/asyncio.html)
[![pydantic](https://img.shields.io/badge/settings-pydantic-202235.svg?logo=pydantic&labelColor=202235&color=edb641&logoColor=edb641)](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgree.svg?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen](https://img.shields.io/badge/conventional_commits-commitizen-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![security: pip-audit](https://img.shields.io/badge/security-pip--audit-yellow.svg)](https://github.com/pypa/pip-audit)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/python/mypy)
[![linting - Ruff](https://img.shields.io/endpoint.svg?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json&labelColor=202235)](https://github.com/astral-sh/ruff)
[![code style - Ruff](https://img.shields.io/endpoint.svg?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json&labelColor=202235)](https://github.com/astral-sh/ruff)
[![dependabot](https://img.shields.io/badge/dependabot-enabled-025E8C.svg?logo=dependabot&logoColor=white)](https://github.com/dependabot)
[![updatecli](https://img.shields.io/badge/updatecli-enabled-025E8C.svg)](https://www.updatecli.io/)

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3--only-yellow.svg)](https://opensource.org/licenses/)
</div>

## Why

When trying to automate downloads from YggTorrent, you have mainly two options :

* try to automate connection to YggTorrent and bypass cloudflare, even [Prowlarr team gave up](https://github.com/Prowlarr/Prowlarr/issues/2479)
* use YggAPI but you have to give your secret passkey to someone you don't know.

YggTorrent Tracker Fixerr is another way, the better of both. You can still use YggAPI but with a random passkey,
this tool will update the passkey in your torrents with the right one on-the-fly (only on QBittorrent for now,
contributions welcome !) with a webhook automatically pushed to sonarr and radarr to get a notification
when a new torrent is added, it will check if the torrent is a yggtorrent one and update the passkey. It has other features
too to keep life simple when using YggTorrent in a arr stack.

If you want to have notifications on project updates, click on the `Watch` button on the top right of Github project page
and select "Custom > Releases & Security Alerts". Please also add a star if you use the project : it helps me track its
popularity and the effort I should put in.

*Note : this project or maintainer has no link with other arr products (like Sonarr and Radarr), nor with YggTorrent.*

## Features

* Update all torrents that have yggtorrent trackers
* Can update on-the-fly torrents via API/Webhook trigger
* Automatic webhook registration for Sonarr and Radarr, so they can notify YggTorrent Tracker Fixer on new torrents
* Dynamic settings for trackers, fetched from url or on disk to keep them updated
* Cronjobs to fetch settings and update all torrents on a regular basis
* Fully configurable using env var or secrets (/run/secrets)
* Tweaking connection to third party tools : proxy, custom CA

## Installation

* Configure Prowlarr with YggAPI, set a random passkey
* To install yggtorrent-tracker-fixerr, create a folder and go in it : `mkdir yggtorrent-tracker-fixerr && cd yggtorrent-tracker-fixerr`
* Download the docker-compose.yml : `wget https://raw.githubusercontent.com/larueli/yggtorrent_tracker_fixerr/refs/heads/main/docker-compose.yml`
* Edit it to input your passkey (the real one !), your connection settings to your QBittorrent instance, the settings to
connect to sonarr/radarr (technically optional, but required to automatically create webhooks which allows sonarr/radarr
to trigger yggtorrent-tracker-fixerr on new downloads)
* If you want to have radarr and sonarr webhook, you must expose your app (same docker network or reverse proxy) to
sonarr and radarr. Configure the EXTERNAL_URL variable accordingly.
* Run : `docker compose up -d --remove-orphans`
* Enjoy !

## Backup

This project itself doesn't store any data, so nothing to really backup. You should backup your docker-compose.yml to
easily redeploy in case of disaster recovery. Beware, secret data like API keys are in the docker-compose.yml. It is
highly suggested to encrypt your backup.

## Update

* Copy your docker-compose.yml
* Read release notes to see if there is any change in env values. In doubt reinstall from scratch as the project doesn't
store any data at all.
* `docker compose pull`
* `docker compose up -d --remove-orphans`

## Contribute

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

This project is licensed under the GNU GPLv3 License — see the [LICENSE](./LICENSE) file for details.

© 2025 Ivann LARUELLE
