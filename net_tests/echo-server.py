from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time

def create_flannel_resources(apps_v1_api, core_v1_api):
    # ServiceAccount for Flannel
    namespace = "kube-system"
    sa_name = "flannel"
    
    # Check if the ServiceAccount already exists
    try:
        core_v1_api.read_namespaced_service_account(name=sa_name, namespace=namespace)
        print(f"ServiceAccount '{sa_name}' already exists in namespace '{namespace}'. Skipping creation.")
        return
    except ApiException as e:
        if e.status == 404:  # Not found
            # ServiceAccount does not exist, create it
            sa = client.V1ServiceAccount(
                metadata=client.V1ObjectMeta(name=sa_name, namespace=namespace)
            )
            core_v1_api.create_namespaced_service_account(namespace=namespace, body=sa)
            print(f"ServiceAccount '{sa_name}' created in namespace '{namespace}'.")
        else:
            # An error other than "Not Found" occurred
            raise
    
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

    apps_v1_api.create_namespaced_daemon_set(namespace="kube-system", body=daemonset)

def deploy_pong_service(apps_v1_api, core_v1_api):
    # # Define the "pong" deployment with an nginx container
    # container = client.V1Container(
    #     name="pong",
    #     image="nginx:alpine",  # Use nginx alpine image for simplicity
    #     ports=[client.V1ContainerPort(container_port=80)],  # nginx listens on port 80 by default
    #     # Define a startup command to replace the default nginx HTML file with a fixed string response
    #     command=["/bin/sh", "-c", "echo 'Pong!' > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"]
    # )

    container = client.V1Container(
        name="pong",
        image="yizhuoliang/simple-server-0215",  # Use your image
        ports=[client.V1ContainerPort(container_port=8080)],
    )
    
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "pong"}),
        spec=client.V1PodSpec(containers=[container])
    )
    
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector=client.V1LabelSelector(match_labels={"app": "pong"}),
    )
    
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="pong"),
        spec=spec,
    )
    
    apps_v1_api.create_namespaced_deployment(namespace="default", body=deployment)

    # NodePort service for external access
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name="pong-service", labels={"app": "pong"}),
        spec=client.V1ServiceSpec(
            selector={"app": "pong"},
            ports=[client.V1ServicePort(port=8080, target_port=8080, node_port=30007)],  # Match nginx's container port
            type="NodePort"  # Specify NodePort type for external access
        )
    )
    
    core_v1_api.create_namespaced_service(namespace="default", body=service)

# a container that constantly send http request to pongs-service
def deploy_ping_service(apps_v1_api, core_v1_api):
    # Define the "ping" deployment
    container = client.V1Container(
        name="ping",
        image="appropriate/curl",  # This image is a simple utility for making HTTP requests
        args=["sh", "-c", "while true; do sleep 2; curl http://pong-service.default.svc.cluster.local:8080; done"],
        # Note: Adjust the curl command according to your pong service's URL and port
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "ping"}),
        spec=client.V1PodSpec(containers=[container])
    )

    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector=client.V1LabelSelector(match_labels={"app": "ping"}),
    )

    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="ping"),
        spec=spec,
    )

    apps_v1_api.create_namespaced_deployment(namespace="default", body=deployment)
    
    print("Ping service deployed")

# This is used for headless service
def get_pod_ip(api_instance, namespace="default", label_selector="app=pong"):
    # Wait a bit for the pod to be scheduled and running
    time.sleep(3)  # Adjust the sleep time as necessary
    
    pods = api_instance.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
    for pod in pods.items:
        print(f"Pod {pod.metadata.name} IP: {pod.status.pod_ip}")
        return pod.status.pod_ip  # Return the IP of the first pod found

# this is used for NodePort service
def list_node_ips(core_v1_api):
    print("Listing nodes with their IPs:")
    ret = core_v1_api.list_node(watch=False)
    for node in ret.items:
        for address in node.status.addresses:
            if address.type == "InternalIP":  # Change this to "ExternalIP" if you're on a cloud provider
                print(f"{node.metadata.name}: {address.address}")


if __name__ == "__main__":
    # Load kubeconfig
    config.load_kube_config()
    
    # Get API instances
    apps_v1_api = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()
    
    # Create Flannel resources
    create_flannel_resources(apps_v1_api, core_v1_api)
    
    # Deploy and expose the "pong" service
    deploy_pong_service(apps_v1_api, core_v1_api)

    # Deoploy the "ping" service
    deploy_ping_service(apps_v1_api, core_v1_api)

    get_pod_ip(core_v1_api)
    list_node_ips(core_v1_api)
    
    print("Flannel and 'pong' service deployed")
