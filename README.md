<!--
Updaates that need to be made:
1. 
-->

# PR-CYBR-PERFORMANCE-AGENT

## Overview

The **PR-CYBR-PERFORMANCE-AGENT** is designed to monitor, analyze, and optimize the performance of the PR-CYBR ecosystem. It ensures that all systems, applications, and processes run efficiently under various workloads.

## Key Features

- **Performance Monitoring**: Tracks key performance indicators (KPIs) across all agents and systems.
- **Load Testing**: Simulates heavy workloads to evaluate system robustness and scalability.
- **Optimization Recommendations**: Provides actionable insights to enhance performance based on collected data.
- **Alerting and Reporting**: Sends alerts for performance anomalies and generates detailed reports.
- **Resource Efficiency**: Identifies areas to reduce resource usage without compromising performance.

## Getting Started

### Prerequisites

- **Git**: For cloning the repository.
- **Python 3.8+**: Required for running scripts.
- **Docker**: Required for containerization and deployment.
- **Access to GitHub Actions**: For automated workflows.

### Local Setup

To set up the `PR-CYBR-PERFORMANCE-AGENT` locally on your machine:

1. **Clone the Repository**

```bash
git clone https://github.com/PR-CYBR/PR-CYBR-PERFORMANCE-AGENT.git
cd PR-CYBR-PERFORMANCE-AGENT
```

2. **Run Local Setup Script**

```bash
./scripts/local_setup.sh
```
_This script will install necessary dependencies and set up the local environment._

3. **Provision the Agent**

```bash
./scripts/provision_agent.sh
```
_This script configures the agent with default settings for local development._

### Cloud Deployment

To deploy the agent to a cloud environment while keeping infrastructure secrets centralized in Terraform Cloud:

1. **Configure Terraform Cloud Workspace Variables**

   - Use the Terraform Cloud workspace backing this repository to store provider credentials, registry tokens, and all other sensitive values. The shared declarations in [`agent-variables.tf`](agent-variables.tf) describe the variables expected to be present.
   - Optionally group shared settings into a Terraform Cloud variable set so that updates remain centralized across PR-CYBR agents.

2. **Connect GitHub to Terraform Cloud via the workflow bridge**

   - In GitHub, navigate to `Settings` > `Secrets and variables` > `Actions` and create:
     - Repository **variables** `TF_CLOUD_ORGANIZATION`, `TF_WORKSPACE`, and (optionally) `TF_CONFIG_DIRECTORY` to point the workflow at the correct Terraform Cloud workspace and configuration path.
     - A repository **secret** `TFC_WORKFLOW_TOKEN` containing a Terraform Cloud user, team, or workload-identity API token with permission to queue runs in the selected workspace.
   - No cloud provider credentials or registry passwords are stored in GitHub—Terraform Cloud injects them during the run.

3. **Deploy Using GitHub Actions**

   - The bridge workflow is defined in `.github/workflows/terraform-cloud-bridge.yml`. Pull requests to `main` queue speculative plans, and merges to `main` queue apply runs in Terraform Cloud.
   - Push changes that include Terraform configuration updates to `main` to trigger an apply run, or open a pull request for a plan-only validation.

4. **Manual Deployment**

   - Use the deployment script for manual deployment if a Terraform Cloud run is not required:

```bash
./scripts/deploy_agent.sh
```

   - Ensure you have Docker and cloud CLI tools installed and configured on your machine.

## Integration

The `PR-CYBR-PERFORMANCE-AGENT` integrates with other `PR-CYBR` agents to monitor and optimize performance across the ecosystem. It communicates with agents like `PR-CYBR-BACKEND-AGENT`, `PR-CYBR-FRONTEND-AGENT`, and `PR-CYBR-INFRASTRUCTURE-AGENT` to collect performance data and provide optimization recommendations.

## Usage

•	Development
•	Start the performance monitoring tools:

```bash
python setup.py develop
```

- Configure monitoring parameters in the config/ directory.

•	Testing
•	Run performance tests:

```bash
python -m unittest discover tests
```

•	Building for Production
•	Build the agent for production use:

```bash
python setup.py install
```

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.

---

_For more information, refer to the [PR-CYBR Documentation](https://github.com/PR-CYBR/PR-CYBR-PERFORMANCE-AGENTWiki) or contact the PR-CYBR team._
