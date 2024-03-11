from kubernetes import client, config
from kubernetes.client.rest import ApiException

def deploy_stateless_job(image_name_tag, namespace):
    config.load_kube_config()  # Load kubeconfig
    api_instance = client.BatchV1Api()

    # Define the Job
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="results-hub-job", namespace=namespace),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "results-hub-job"}),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="results-hub-job-container",
                        image=image_name_tag,
                        # No ports exposed, but ensures it can communicate within the cluster
                    )],
                    restart_policy="Never"  # Ensure the container exits after completion
                )
            )
        )
    )

    try:
        api_instance.create_namespaced_job(namespace=namespace, body=job)
        print(f"Job 'results-hub-job' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when creating Job: {e}")
        raise

if __name__ == "__main__":
    # CREATE PV
    image_name = "yizhuoliang/job-test1:latest"
    namespace = "default" # for ResultsHub and jobs

    deploy_stateless_job(image_name, namespace)