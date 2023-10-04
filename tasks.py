from invoke import task

ENV_NAME = "venv"
CONDA_DIR = "~/anaconda3"
PYTHON_VERSION = "3.10"


@task
def setup(c):
    print("Creating conda environment...")
    c.run(f"conda create --name {ENV_NAME} python={PYTHON_VERSION} -y")
    print("Setting up hooks for the environment...")
    c.run(f"ln -sf $(pwd)/scripts/generate_requirements.sh {CONDA_DIR}/envs/{ENV_NAME}/etc/conda/activate.d/post-activate.sh")
    print(f"All set! Activate your environment using: conda activate {ENV_NAME}")

@task
def requirements(c):
    c.run("bash scripts/generate_requirements.sh")

@task
def clean(c):
    print("Removing environment...")
    c.run(f"conda env remove --name {ENV_NAME}")
    print("Environment removed.")
