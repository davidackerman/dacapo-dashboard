import requests
import json
import subprocess
from os.path import expanduser
# from dashboard import socketio


class Nextflow:
    # general settings
    host_name = "nextflow.int.janelia.org"
    nextflow_api = f"https://{host_name}/api"
    ssh_key = None
    verified = True
    error_message = None

    # compute environment settings
    head_queue = "local"
    compute_queue = "local"

    # workflow settings
    pipeline_repo = f"https://github.com/davidackerman/dacapo-nextflow"
    revision = "main"
    config_profiles = ["lsf"]
    main_script = "dacapo.nf"

    def __init__(self, user_info, ssh_key=None):
        self.username = user_info["username"]
        self.api_token = user_info["api_token"]
        self.ssh_key = ssh_key
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if ssh_key:
            # Then this is a first time setup, so need to validate
            res = self.check_token_validity()
            if res.status_code == 200:
                res = self.set_login_node_credentials()
                if res.status_code != 200:
                    self.verified = False
                    self.error_message = (
                        f'Invalid SSH Key. Response: {res.status_code}. {"Error message: "+res.json()["message"] if res.status_code in [400,409] else ""}',
                    )[0]
            else:
                self.verified = False
                self.error_message = (
                    f'Invalid API Token. Response: {res.status_code}. {"Error message: "+res.json()["message"] if res.status_code in [400,409] else ""}',
                )[0]

    def emit(self, type, message):
        return
        socketio.emit(
            "message",
            json.dumps(
                {
                    "username": self.username,
                    "type": type,
                    "message": f"{message}",
                }
            ),
        )

    def check_token_validity(self):
        res = requests.get(url=f"{self.nextflow_api}/tokens", headers=self.headers)
        return res

    def set_login_node_credentials(self):
        credentials = {
            "credentials": {
                "name": "dacapo",
                "provider": "ssh",
                "keys": {
                    "privateKey": self.ssh_key,
                    "passphrase": None,
                },
            }
        }
        res = requests.post(
            url=f"{self.nextflow_api}/credentials",
            data=json.dumps(credentials),
            headers=self.headers,
        )

        return res

    def get_login_node_credentials(self):
        credential_id = None
        res = requests.get(url=f"{self.nextflow_api}/credentials", headers=self.headers)
        for credential in res.json()["credentials"]:
            if credential["name"] == "dacapo":
                credential_id = credential["id"]

        return credential_id

    def set_compute_environment(self, chargegroup):
        workdir = expanduser(f"~{self.username}/") + ".dacapo/nextflow"

        compute_env = {
            "computeEnv": {
                "name": f"dacapo_{chargegroup}",
                "platform": "lsf-platform",
                "config": {
                    "userName": self.username,
                    "workDir": workdir,
                    "launchDir": workdir,
                    "hostName": self.host_name,
                    "headQueue": self.head_queue,
                    "computeQueue": self.compute_queue,
                    "headJobOptions": f"-P {chargegroup}",
                },
                "credentialsId": self.get_login_node_credentials(),
            }
        }

        self.emit(
            "Info",
            f"Setting up first time compute environment for chargegroup {chargegroup}",
        )

        res = requests.post(
            url=f"{self.nextflow_api}/compute-envs",
            data=json.dumps(compute_env),
            headers=self.headers,
        )

        if res.status_code != 200:
            self.emit(
                "Error",
                f'Failed setting up first time compute environment for chargegroup {chargegroup}.  Response: {res.status_code}. {"Error message: "+res.json()["message"] if res.status_code in [400,409] else ""}',
            )
        else:
            self.emit(
                "Success",
                f"Set up first time compute environment for chargegroup {chargegroup}",
            )

        return res

    def get_or_set_compute_environment(self, chargegroup):
        res = requests.get(
            url=f"{self.nextflow_api}/compute-envs", headers=self.headers
        )

        compute_env_id = None
        for compute_env in res.json()["computeEnvs"]:
            if compute_env["name"] == f"dacapo_{chargegroup}":
                compute_env_id = compute_env["id"]

        if not compute_env_id:
            res = self.set_compute_environment(chargegroup)
            if res.status_code == 200:
                compute_env_id = res.json()["computeEnvId"]
        return compute_env_id

    def launch_workflow(self, params_text, chargegroup):
        if not chargegroup:
            chargegroup = subprocess.getoutput(f"lsfgroup {self.username}")

        params_text["lsf_opts"] = f"-P {chargegroup}"
        compute_env_id = self.get_or_set_compute_environment(chargegroup)
        if compute_env_id:
            workdir = expanduser(f"~{self.username}/") + ".dacapo/nextflow"
            workflow = {
                "launch": {
                    "computeEnvId": compute_env_id,
                    "pipeline": self.pipeline_repo,
                    "workDir": workdir,
                    "revision": self.revision,
                    "configProfiles": self.config_profiles,
                    "paramsText": json.dumps(params_text),
                    "mainScript": self.main_script,
                    "pullLatest": True,
                }
            }

            self.emit("Info", f'Submitting run {params_text["run_name"]}')

            res = requests.post(
                url=f"{self.nextflow_api}/workflow/launch",
                data=json.dumps(workflow),
                headers=self.headers,
            )

            if res.status_code == 200:
                workflow_id = res.json()["workflowId"]
                res = requests.get(
                    url=f"{self.nextflow_api}/workflow/{workflow_id}",
                    headers=self.headers,
                )
                user_name = res.json()["workflow"]["userName"]
                self.emit(
                    "Success",
                    f'Submitted run {params_text["run_name"]}, monitor <a href="https://{self.host_name}/user/{user_name}/watch/{workflow_id}" target="_blank">here</a>.',
                )
            else:
                self.emit(
                    "Error",
                    f'Failed to submit run {params_text["run_name"]}. Response: {res.status_code}. {"Error message: "+res.json()["message"] if res.status_code in [400,409] else ""}',
                )
