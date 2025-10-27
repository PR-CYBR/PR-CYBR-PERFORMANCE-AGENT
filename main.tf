terraform {
  # Terraform Cloud backend configuration
  cloud {
    organization = "PR-CYBR"

    workspaces {
      name = "PR-CYBR-PERFORMANCE-AGENT"
    }
  }

  required_version = ">= 1.0"

  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Minimal null resource to validate the Terraform configuration
# This ensures terraform init, plan, and apply can run successfully
resource "null_resource" "agent_validation" {
  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = "echo 'PR-CYBR-PERFORMANCE-AGENT Terraform configuration validated'"
  }
}

# Output the declared variables for verification
output "agent_info" {
  value = {
    agent_name  = "PR-CYBR-PERFORMANCE-AGENT"
    description = "Performance monitoring and optimization agent"
  }
  description = "Basic agent information"
}
