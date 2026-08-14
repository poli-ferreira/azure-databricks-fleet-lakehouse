terraform {
  required_version = ">= 1.7"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.60"
    }
  }
}

# Auth: run `databricks auth login --host <workspace-url>` first, or export
# DATABRICKS_HOST / DATABRICKS_TOKEN. Kept as a separate stack because these
# workspace-level resources can only exist after the workspace does.
provider "databricks" {
  host = var.workspace_url
}
