# SET UP CLUSTER:
(4 nodes) Spark-Cluster, instance type: m4.large
(4 nodes) Kafka-Cluster , instance type: m4.large
(1 node) PostgreSQL, instance type: m4.large
(1 node) Dash , instance type: m4.large

## EC2 Instances Setup
Follow this [guide](https://blog.insightdatascience.com/create-a-cluster-of-instances-on-aws-899a9dc5e4d0) to create multiple clusters of instances on AWS.

## AWS Security Group Setup
Follow this [guide](https://docs.google.com/document/d/1ErNGLnbQPqpwL-SxlRRixj7FNOXWhCu0cqfXTsDos88/edit) to set up AWS security group. 

## Kafka Multiple Brokers Setup
Follow this [guide](https://docs.google.com/document/d/1xArTOXGDeAgFDAZPf_uOSBHvGr6IjNDOVh5-1ZRR4dE/edit#heading=h.fuw1m7gj5l2g) to create multiple brokers and zookeepers for Kafka. (# of Kafka clusters can only be odd number)

## Spark Multiple Workers Setup
Follow this [guide](https://blog.insightdatascience.com/simply-install-spark-cluster-mode-341843a52b88) to install Spark with multiple workers. 

## PostgreSQL Setup
Follow this [guide](https://blog.insightdatascience.com/simply-install-postgresql-58c1e4ebf252) to install PostgreSQL. 
