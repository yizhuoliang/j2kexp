from kubernetes import client, config

def create_flannel_resources(api_instance):
    # Create a ServiceAccount for Flannel
    sa = client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(name="flannel", namespace="kube-system")
    )
    api_instance.create_namespaced_service_account(namespace="kube-system", body=sa)

    # Define the Flannel DaemonSet
    container = client.V1Container(
        name="kube-flannel",
        image="quay.io/coreos/flannel:v0.14.0",  # Use the latest Flannel image
        args=[
            "--ip-masq",
            "--kube-subnet-mgr"
        ],
        security_context=client.V1SecurityContext(privileged=True),
        volume_mounts=[
            client.V1VolumeMount(mount_path="/run/flannel", name="run"),
            client.V1VolumeMount(mount_path="/etc/kube-flannel/", name="flannel-cfg")
        ]
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "flannel"}),
        spec=client.V1PodSpec(
            containers=[container],
            service_account_name="flannel",
            volumes=[
                client.V1Volume(name="run", host_path=client.V1HostPathVolumeSource(path="/run")),
                client.V1Volume(name="flannel-cfg", config_map=client.V1ConfigMapVolumeSource(name="kube-flannel-cfg"))
            ],
            tolerations=[  # Allow scheduling on all types of nodes
                client.V1Toleration(operator="Exists")
            ]
        )
    )

    daemonset = client.V1DaemonSet(
        metadata=client.V1ObjectMeta(name="kube-flannel-ds", namespace="kube-system"),
        spec=client.V1DaemonSetSpec(
            selector=client.V1LabelSelector(match_labels={"app": "flannel"}),
            template=template,
            update_strategy=client.V1DaemonSetUpdateStrategy(type="RollingUpdate")
        )
    )

    api_instance.create_namespaced_daemon_set(namespace="kube-system", body=daemonset)

if __name__ == "__main__":
    # Load the kubeconfig file
    config.load_kube_config()

    # Get the API instance for apps/v1
    apps_v1_api = client.AppsV1Api()

    # Create the Flannel resources
    create_flannel_resources(apps_v1_api)
