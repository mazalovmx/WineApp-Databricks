## Cursor Cloud specific instructions

This is a **greenfield repository** (WineApp-Databricks) with no source code yet — only a `README.md` describing the intent: a Databricks App for finding daily best wine deals.

### Current state

- No application code, dependencies, build configuration, tests, or lint setup exist.
- No services to start or test.

### Environment

- Python 3.12 and pip are available in the base VM image.
- Node.js and git are also pre-installed.
- When code is added, update the VM startup script (`SetupVmEnvironment`) to install the chosen dependencies (e.g., `pip install -r requirements.txt` or `pnpm install`).

### Expected stack (from README context)

The project name suggests a Databricks Apps deployment. Common stacks include Python with Dash, Streamlit, Gradio, or Flask, plus the Databricks SDK/CLI. Adjust tooling once the stack is chosen.
