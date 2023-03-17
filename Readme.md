# Title: Nano Beta Bootstrap Cluster

### Description:

This repository contains a Python script (nanobeta_bootstrap_cluster.py) that automates the creation, management, and deletion of a cluster of Nano beta network nodes on Google Cloud Platform. The script leverages the Google Cloud SDK to create instances running Docker containers with specified Nano beta network node versions, allowing users to easily set up, restart, and remove nodes for testing and development purposes.

### Features:

- Create multiple Nano beta network nodes with specified Docker tags and instance counts
- Automatically restart terminated instances
- Delete instances when they are no longer needed
- Configure optional zones for node deployment
- Asynchronous execution for efficient management of multiple nodes

```bash
python3 nanobeta_bootstrap_cluster.py --create "nanocurrency/nano:V24.0" 5 --create "nanocurrency/nano:V25.0DB24" 10
python3 nanobeta_bootstrap_cluster.py --stop
python3 nanobeta_bootstrap_cluster.py --restart
python3 nanobeta_bootstrap_cluster.py --delete
```

This project simplifies the process of managing a cluster of bootstrapping Nano beta network nodes, making it easier for developers and testers to experiment with different node versions and configurations.