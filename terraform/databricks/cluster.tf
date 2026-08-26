# Single-node all-purpose cluster for ad-hoc exploration (SQL editor / notebooks).
# Not used by the DLT pipeline itself - that runs on its own (serverless or
# job) compute. Auto-terminates quickly so it doesn't burn trial credit
# if left idle.

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

data "databricks_current_user" "me" {}

# Resolved dynamically instead of hardcoding Standard_DS3_v2: that exact SKU
# hit an Azure capacity stockout in this region/subscription, and this data
# source picks whatever smallest-fitting type is actually available.
data "databricks_node_type" "smallest" {
  local_disk = true
}

resource "databricks_cluster" "explore" {
  cluster_name            = "explore-single-node"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 15
  num_workers             = 0

  # UC-enforced workspaces reject the legacy "No Isolation Shared" mode a
  # bare singleNode config implies - single-node UC clusters must be
  # pinned to one user via SINGLE_USER access mode.
  data_security_mode = "SINGLE_USER"
  single_user_name   = data.databricks_current_user.me.user_name

  spark_conf = {
    "spark.databricks.cluster.profile" = "singleNode"
    "spark.master"                     = "local[*]"
  }

  custom_tags = {
    ResourceClass = "SingleNode"
  }
}
