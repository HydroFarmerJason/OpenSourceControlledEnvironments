# Setup Wizard

This folder contains the modular `wizard.sh` script and supporting files for configuring a Raspberry Pi based controlled environment system. The wizard is designed for non-technical users and walks through selecting a role, goal, hardware complexity, and privacy level.

Run the wizard from the repository root:

```bash
sudo ./setup/wizard.sh
```

The script records your selections to `config/user_choices.json` for later integration with dashboards or automation tools. To extend the wizard, edit or add functions in `wizard.sh`.
