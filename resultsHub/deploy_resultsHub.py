from kubernetes import client, config

def create_local_pv(node_name, local_path, pv_name, storage_size):
    config.load_kube_config()  # Load the kubeconfig file

    api_instance = client.CoreV1Api()

    # Define the PersistentVolume
    persistent_volume = client.V1PersistentVolume(
        api_version="v1",
        kind="PersistentVolume",
        metadata=client.V1ObjectMeta(name=pv_name),
        spec=client.V1PersistentVolumeSpec(
            capacity={"storage": storage_size},
            access_modes=["ReadWriteOnce"],
            persistent_volume_reclaim_policy="Retain",
            storage_class_name="local-storage",
            local=client.V1LocalVolumeSource(path=local_path),
            node_affinity=client.V1VolumeNodeAffinity(
                required=client.V1NodeSelector(
                    node_selector_terms=[
                        client.V1NodeSelectorTerm(
                            match_expressions=[
                                client.V1NodeSelectorRequirement(
                                    key="kubernetes.io/hostname",
                                    operator="In",
                                    values=[node_name]
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )

    # Create the PersistentVolume
    try:
        api_instance.create_persistent_volume(body=persistent_volume)
        print(f"PersistentVolume '{pv_name}' created.")
    except ApiException as e:
        if e.status == 409:
            print(f"PersistentVolume '{pv_name}' already exists.")
        else:
            print(f"Exception when creating PersistentVolume: {e}")

def create_local_storage_class():
    config.load_kube_config()  # Load the kubeconfig file

    api_instance = client.StorageV1Api()

    # Define the StorageClass
    storage_class = client.V1StorageClass(
        api_version="storage.k8s.io/v1",
        kind="StorageClass",
        metadata=client.V1ObjectMeta(name="local-storage"),
        provisioner="kubernetes.io/no-provisioner",
        volume_binding_mode="WaitForFirstConsumer",
        reclaim_policy="Retain"
    )

    # Create the StorageClass
    try:
        api_instance.create_storage_class(body=storage_class)
        print("StorageClass 'local-storage' created.")
    except ApiException as e:
        if e.status == 409:
            print("StorageClass 'local-storage' already exists.")
        else:
            print(f"Exception when creating StorageClass: {e}")

def create_statefulset_with_pv():
    config.load_kube_config()  # Load kubeconfig

    api_instance = client.AppsV1Api()

    # Define container
    container = client.V1Container(
        name="results-hub",
        image="yizhuoliang/results-hub:latest",
        ports=[client.V1ContainerPort(container_port=50051)]
    )

    # Define VolumeClaimTemplates
    volume_claim_templates = [
        client.V1PersistentVolumeClaim(
            metadata=client.V1ObjectMeta(name="results-hub-storage"),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=client.V1ResourceRequirements(
                    requests={"storage": "1Gi"}
                ),
                # If using local volumes, specify the appropriate StorageClass
                storage_class_name="local-storage"
            )
        )
    ]

    # Define Pod template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "results-hub"}),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=[
                client.V1Volume(
                    name="results-hub-storage",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name="results-hub-storage"
                    )
                )
            ]
        )
    )

    # Define StatefulSet spec
    stateful_set_spec = client.V1StatefulSetSpec(
        service_name="results-hub",
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": "results-hub"}),
        template=template,
        volume_claim_templates=volume_claim_templates
    )

    # Define the StatefulSet
    stateful_set = client.V1StatefulSet(
        api_version="apps/v1",
        kind="StatefulSet",
        metadata=client.V1ObjectMeta(name="results-hub"),
        spec=stateful_set_spec
    )

    # Create StatefulSet
    api_instance.create_namespaced_stateful_set(
        namespace="default",
        body=stateful_set
    )

    print("StatefulSet created.")

if __name__ == "__main__":
    # CREATE PV
    node_name = "your-node-name" # Replace with your node's name
    local_path = "/mnt/local-storage" # Replace with your directory path
    pv_name = "local-pv"
    storage_size = "1Gi" # Adjust the size as needed
    create_local_pv(node_name, local_path, pv_name, storage_size)

    # CREATE STORAGE CLASS
    create_local_storage_class()

    # DEPLOY RESULTSHUB
    create_statefulset_with_pv()
