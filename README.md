# Open Source Controlled Environments

This repository contains tooling for setting up an autonomous container farm control system.

The main script `setup_wizard.sh` implements a full-featured interactive setup wizard. Run it as root on your Raspberry Pi to configure sensors, privacy settings, optional software packages, and dashboard generation.

```bash
sudo bash setup_wizard.sh
```

The wizard walks you through hardware configuration, Mycodo installation, backup scheduling, and other options tailored to your use case.
