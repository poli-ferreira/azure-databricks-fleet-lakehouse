# Single-node all-purpose cluster for ad-hoc exploration (SQL editor / notebooks).
# Not used by the DLT pipeline itself - that runs on its own (serverless or
# job) compute. Auto-terminates quickly so it doesn't burn trial credit
# if left idle.

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "explore" {
  cluster_name            = "explore-single-node"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = 15
  num_workers              = 0

  spark_conf = {
    "spark.databricks.cluster.profile" = "singleNode"
    "spark.master"                     = "local[*]"
  }

  custom_tags = {
    ResourceClass = "SingleNode"
  }
}
