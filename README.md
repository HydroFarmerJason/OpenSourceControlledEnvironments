# Open Source Controlled Environments

This project provides tools and documentation for building a locally controlled container farm. The goal is to keep growers in charge of their own infrastructure while remaining easy for beginners to use.

![dashboard screenshot](docs/img/dashboard_example.png)

## Getting Started

1. Flash Raspberry Pi OS and connect your Pi to the network.
2. Clone this repository and run the setup wizard as root:

```bash
sudo bash setup/wizard.sh
```

The wizard walks through project metadata, hardware configuration, software installation and privacy options. When finished you'll be able to log in to Mycodo and begin customizing your automation.

## Repository Layout

```
setup/             - interactive setup wizard and helper scripts
config/            - example configuration files
docs/              - user guide and privacy statement
.github/workflows/ - CI configuration (optional)
```

See `docs/user_guide.md` for step‑by‑step setup instructions and `docs/privacy_statement.md` for our local‑first philosophy.
