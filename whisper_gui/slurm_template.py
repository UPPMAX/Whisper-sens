import subprocess
import os
from datetime import datetime
from pathlib import Path

class SlurmTemplate(str):

    def __init__(self):

        self.account = None
        self.node_type = None
        self.num_nodes = None
        self.job_time = None
        self.job_name = f"Whisper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_file = None
        self.error_file = None
        self.slurm_constraints = None
        self.whisper_module = None
        self.commands = None

        self.cluster = os.environ.get("CLUSTER")
        self.whoami = os.environ.get("whoami")
        self.script_dir = None
        self.script_name = f"{self.job_name}.sh"


    def script(self):
        
        sbatch_script = f"""#!/bin/bash -l
        #SBATCH -A {self.account}
        #SBATCH -p {self.node_type}
        #SBATCH -n {self.num_nodes}
        #SBATCH -t {self.job_time}
        #SBATCH -J {self.job_name}
        #SBATCH -o {self.output_file}
        #SBATCH -e {self.error_file}
        {self.slurm_constraints}

        module load {self.whisper_module}

        {self.commands}

        """

        with open(f"{self.script_dir}/{self.script_name}", "w") as f:
            f.write(sbatch_script)

    def submit(self):

        

        if self.cluster == "Rackham" or self.cluster == "Snowy":

            self.script_dir = f"/home/{self.whoami}/Desktop/Whisper_logs"

            if Path.exists(self.script_dir) == False:
                os.mkdir(self.script_dir)

            command = f"sbatch -M snowy {self.script_dir}/{self.script_name}.sh"

        elif self.cluster == "Bianca":

            self.script_dir = f"/home/{self.whoami}/Desktop/proj/Whisper_logs"

            if Path.exists(self.script_dir) == False:
                os.mkdir(self.script_dir)

            command = f"sbatch {self.script_dir}/{self.script_name}.sh"

        try:
            result =  subprocess.run(command, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("Error occurred:", e.stderr)