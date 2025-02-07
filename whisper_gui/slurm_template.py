import subprocess
import os
import logging
from datetime import datetime
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

class SlurmTemplate:

    def __init__(self, job_time, whisper_module, commands, whoami, script_dir):

        self.account = None
        self.node_type = "core"
        self.num_nodes = 1
        self.job_time = job_time
        self.job_name = f"Whisper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_file = None
        self.error_file = None
        self.slurm_constraints = None
        self.whisper_module = whisper_module
        self.commands = None

        self.cluster = os.environ.get("CLUSTER")
        self.whoami = whoami
        self.script_dir = script_dir
        self.script_name = f"{self.job_name}.sh"


    def script(self):
        
        sbatch_script = f"""#!/bin/bash -l
        #SBATCH -A {self.account}
        #SBATCH -p {self.node_type}
        #SBATCH -n {self.num_nodes}
        #SBATCH -t {self.job_time}
        #SBATCH -J {self.job_name}
        #SBATCH -o {self.output_file}/{self.job_name}_%u_%j.out
        #SBATCH -e {self.error_file}/{self.job_name}_%u_%j.out
        {self.slurm_constraints}

        module load {self.whisper_module}

        {self.commands}

        """

        try: 
            with open(f"{self.script_dir}/{self.script_name}", "w") as f:
                f.write(sbatch_script)
            return True
        except Exception as e:
            logger.exception("Error occurred in writing bash script: ", e.stderr)
            return False

    def submit(self):

        device = "gpu"


        if self.cluster == "rackham" or self.cluster == "snowy":

            group_list = subprocess.run(f"groups {self.whoami}", shell=True, capture_output=True, text=True).stdout.strip()
            self.account = group_list.split()[-1]

            if device == "gpu":
                self.slurm_constraints = f"#SBATCH --gres=gpu:1 -M snowy"

            command = f"sbatch -M snowy {self.script_dir}/{self.script_name}"

        elif self.cluster == "bianca":

            hostname = subprocess.run(["hostname", "-s"], shell=True, capture_output=True, text=True).stdout.strip()
            self.account = hostname.split("-")[0]

            if device == "gpu":
                self.slurm_constraints = f"#SBATCH -C gpu --gpus-per-node=1"

            command = f"sbatch {self.script_dir}/{self.script_name}"

        try:
            if self.script():
                result =  subprocess.run(command, check=True, text=True, capture_output=True)
                if result.returncode == 0:
                    logger.info(f"Job {self.job_name} submitted successfully")
        except subprocess.CalledProcessError as e:
            logger.exception("Error occurred while submitting the job: ", e.stderr)