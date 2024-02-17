from kubernetes import client, config
from kubernetes.client.rest import ApiException

def cleanup_resources(apps_v1_api, core_v1_api):
    namespace = "kube-system"
    sa_name = "flannel"
    daemonset_name = "kube-flannel-ds"
    
    # Delete ServiceAccount in kube-system namespace
    try:
        core_v1_api.delete_namespaced_service_account(name=sa_name, namespace=namespace)
        print(f"ServiceAccount '{sa_name}' deleted.")
    except ApiException as e:
        if e.status != 404:  # Not found
            raise
    
    # Delete DaemonSet in kube-system namespace
    try:
        apps_v1_api.delete_namespaced_daemon_set(name=daemonset_name, namespace=namespace)
        print(f"DaemonSet '{daemonset_name}' deleted.")
    except ApiException as e:
        if e.status != 404:
            raise

    # Cleanup resources in default namespace
    namespace = "default"
    resources = {
        "deployment": ["pong", "ping"],  # List of deployments to delete
        "service": ["pong-service"]  # List of services to delete
    }

    # Delete Deployments
    for deployment_name in resources["deployment"]:
        try:
            apps_v1_api.delete_namespaced_deployment(name=deployment_name, namespace=namespace)
            print(f"Deployment '{deployment_name}' deleted.")
        except ApiException as e:
            if e.status != 404:
                raise

    # Delete Services
    for service_name in resources["service"]:
        try:
            core_v1_api.delete_namespaced_service(name=service_name, namespace=namespace)
            print(f"Service '{service_name}' deleted.")
        except ApiException as e:
            if e.status != 404:
                raise

if __name__ == "__main__":
    # Load kubeconfig
    config.load_kube_config()

    # Get API instances
    apps_v1_api = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()

    # Cleanup resources
    cleanup_resources(apps_v1_api, core_v1_api)
    
    print("Cleanup completed")
