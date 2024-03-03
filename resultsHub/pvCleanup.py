from kubernetes import client, config

def delete_pv():
    v1 = client.CoreV1Api()
    print("Deleting PersistentVolume...")
    v1.delete_persistent_volume(name="example-pv")

def delete_pvc():
    v1 = client.CoreV1Api()
    print("Deleting PersistentVolumeClaim...")
    v1.delete_namespaced_persistent_volume_claim(name="example-pvc", namespace="default")

def delete_deployment():
    apps_v1 = client.AppsV1Api()
    print("Deleting Deployment...")
    apps_v1.delete_namespaced_deployment(name="example-deployment", namespace="default")

def main():
    config.load_kube_config()  # Loads your kube config

    delete_deployment()  # Deployments should be deleted before the PVCs they use
    delete_pvc()
    delete_pv()

    print("Cleanup completed successfully.")

if __name__ == "__main__":
    main()
