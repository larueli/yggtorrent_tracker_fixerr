# Contributing

Every contribution is welcome ! It is recommended to open an issue first to discuss the contribution beforehand and avoid
unneccessary development.

## Features to develop

One thing to do should be implementing new torrent clients (ruTorrent, ...) that implements the `TorrentClient` class

## Knowledge

Check the [README](./README.md) top badges to see the libraries used in this project, you
should have a basic understanding of git, Python and object oriented programming. This project uses precommit, commitizen
and automated tests.

## DevContainers

It is strongly recommended to use the devcontainers provided, as they provide all the toolset required to work on the project
really easily. Use the `classic` if you don't know which one to choose, or `rootless` if using docker-rootless or podman.

## Makefile

The [Makefile](./Makefile) declares actions that helps in various stuff.

* `make setup` will install uv dependencies and precommit hooks used by the project. It is automatically ran when using
devcontainers.
* `make dev` will run the project. I recommend creating a `.env` file based on `.env.dist` and the docker-compose.yml
* `make update` will update uv dependancies and precommits hooks

## Language

Code, text, docs should be written in English.

## Commits

Commits must use the [conventional commit standard](https://www.conventionalcommits.org/en/v1.0.0/). You can read this
[article by cbeam](https://cbea.ms/git-commit/) on the subject. To help doing so, either use the cli (`git add ...`
then `uv run cz c`) or VSCode (using the VSC panel, stage your changes, then click on the circle button to launch the
conventional commit plugin).
