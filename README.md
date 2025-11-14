# octowalrus

A fastapi service for octowalrus by Spark Syndicate

Completely update this file to suit octowalrus!

## Requirements

- [Python 3.11](https://www.python.org/doc/versions/)
- [Docker](https://www.docker.com/)
- [Tilt](https://docs.tilt.dev/install.html)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - for Kubernetes operations
- [asdf](https://asdf-vm.com) - for local installs (optional, see .tool-versions)
- [just](https://just.systems/man/en/) - For development commands (optional, can use npm/tilt directly)

## Development

### Getting Started

This project uses a justfile for all development tasks. Run `just` to see all available commands.

```bash
# Setup and start development
just dev
```