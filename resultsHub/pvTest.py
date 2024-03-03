from kubernetes import client, config

def create_pv():
    pv = client.V1PersistentVolume(
        api_version="v1",
        kind="PersistentVolume",
        metadata=client.V1ObjectMeta(name="example-pv"),
        spec=client.V1PersistentVolumeSpec(
            capacity={"storage": "1Gi"},
            volume_mode="Filesystem",
            access_modes=["ReadWriteOnce"],
            persistent_volume_reclaim_policy="Retain",
            storage_class_name="manual",
            local=client.V1LocalVolumeSource(path="/data/my-pv"),
            node_affinity=client.V1VolumeNodeAffinity(
                required=client.V1NodeSelector(
                    node_selector_terms=[
                        client.V1NodeSelectorTerm(
                            match_expressions=[
                                client.V1NodeSelectorRequirement(
                                    key="kubernetes.io/hostname",
                                    operator="In",
                                    values=["your-node-name"]
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )
    return pv

def create_pvc():
    pvc = client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(name="example-pvc"),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            storage_class_name="manual",
            resources=client.V1ResourceRequirements(
                requests={"storage": "1Gi"}
            )
        )
    )
    return pvc

def create_deployment():
    container = client.V1Container(
        name="app",
        image="busybox",  # Using busybox for simple shell commands
        volume_mounts=[client.V1VolumeMount(mount_path="/app/data", name="storage")],
        # Using shell commands to write and read from /app/data/date.txt
        command=["/bin/sh", "-c"],
        args=[
            "echo Writing date to /app/data/date.txt; " +
            "date > /app/data/date.txt; " +
            "echo Reading from /app/data/date.txt; " +
            "cat /app/data/date.txt; " +
            "sleep 3600"  # Sleep for 1 hour to keep the container running for demonstration purposes
        ]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "example"}),
        spec=client.V1PodSpec(containers=[container], volumes=[
            client.V1Volume(name="storage", persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name="example-pvc"))
        ])
    )
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={'matchLabels': {'app': 'example'}}
    )
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="example-deployment"),
        spec=spec
    )
    return deployment


def main():
    config.load_kube_config()  # Loads your kube config
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    pv = create_pv()
    pvc = create_pvc()
    deployment = create_deployment()

    print("Creating PersistentVolume...")
    v1.create_persistent_volume(body=pv)
    print("Creating PersistentVolumeClaim...")
    v1.create_namespaced_persistent_volume_claim(namespace="default", body=pvc)
    print("Creating Deployment...")
    apps_v1.create_namespaced_deployment(namespace="default", body=deployment)

    print("Deployment created successfully.")

if __name__ == "__main__":
    main()
