# STP Segmentation WDL

This repository contains WDL scripts that will be used to run workflows on Terra.bio.

## Quick Overview: WDL, Docker, and Cromwell

#### What is WDL (Workflow Description Language)?

WDL is a language for describing computational workflows. It allows you to define tasks, inputs, outputs, and dependencies. WDL files usually end with a .wdl extension.

#### What is Docker?

Docker is a platform for developing, shipping, and running applications in containers. Containers provide a consistent environment for running software, regardless of the underlying infrastructure. Dockerfiles are used to create Docker images, which are portable snapshots of an application and its dependencies.

#### What is Cromwell?

Cromwell is a workflow management system designed to execute WDL (Workflow Description Language) workflows. It's developed by the Broad Institute for managing complex scientific workflows. Local Setup instructions mentioned [here](https://github.com/broadinstitute/stp_segmentation_wdl?tab=readme-ov-file#testing-wdl-workflow-on-a-local-machinecluster).

### A) WDL Guide:

- WDL comprises the following components: workflow, task, and call. Import components/scripts before drafting the workflow block. Specify required inputs, and for optional ones, append a "?" right after the input type (e.g., Float?). Utilize scatter-gather to submit jobs parallelly. In WDL, the following statement must be used to allow the scatter-gather approach on optional inputs, e.g.: "if defined(image_mpp) then select_first([image_mpp]) else 0.0", where "image_mpp" is an optional Float input. The “defined function” checks whether this input has been defined or not. Then, the “select_first function” retrieves the first available or first defined element of the "array" image_mpp; the image_mpp variable has to be displayed as an array because the select_first function just works this way as it accepts only an array. The "else" statement is also apparently necessary, even though, generally, for other programming languages, it is not required to include an "else" statement. Each algorithm (cellpose, deepcell and baysor) is stored in different scripts, thereby modularizing the pipeline slightly. 

- Follow the steps mentioned [here](https://support.terra.bio/hc/en-us/articles/8888504224283-How-to-set-up-a-WDL-on-Github-Dockstore) to publish the WDL workflow on Dockstore.

- WDL requires docker image paths for each of its “task” blocks. The images are available on DockerHub in OPP and jishar's account. WDL is simply used to communicate with Terra on how and what to run. Internally, it could employ Python scripts to execute operations (these python scripts are called using bash or smaller pythonic scripts). These Python scripts are stored in specified locations within the respective Docker images. 

### B) Docker Guide:

To build a Docker image locally, you'll need to follow these general steps:

1. Install Docker: Ensure that Docker is installed on your local machine. You can download Docker Desktop for Windows or Mac from the [Docker website](https://www.docker.com/products/docker-desktop) or install Docker Engine on Linux.

2. Create a Dockerfile: Create a file named `Dockerfile` (without any file extension) in your project directory. This file will contain instructions for building your Docker image. If you are on a Mac, ensure to remove the “.txt” extension completely by navigating to the “Get Info” section of the Dockerfile and manually removing the extension of this text bar.

3. Build the Docker Image: Open a terminal or command prompt and type in,
  
    ``cd {directory_having_dockerfile}``
  
    ``docker build -f Dockerfile -t image_name:tag .``

4. Replace `image_name` with the desired name for your Docker image and `tag` with a version or tag for the image (usually “latest” is used as a tag). The dot (`.`) at the end specifies the build context (current directory).

5. To specify a builder, use the following command:

- template:
  
  `` docker buildx build --platform {builder} -t {image_name}:{tag} . ``
  
- example:
  
  `` docker buildx build --platform linux/amd64 -t test_docker_for_tile_version2 . ``


  
4. Verify the Image: After the build process completes, you can verify that the Docker image was created successfully by running,
   ``
   docker images
   ``

5. Tag the Image Locally: After building your Docker image locally, use the `docker tag` command to assign a specific tag to the image,
   ``
   docker tag image_name:latest your_username/repository:tag
   ``
Replace `image_name:latest` with the name and tag of your locally built image, and `your_username/repository:tag` with the desired repository name and tag on Docker Hub.

6. Push the Tagged Image: Once you have tagged the image with the desired version or tag, you can push it to Docker Hub using the `docker push` command,
   ``
   docker push your_username/repository:tag
   ``
This command will push the image with the specified tag (`tag`) to your Docker Hub repository (`your_username/repository`).


## Testing WDL Workflow on a Local Machine/Cluster:

### A) Install Cromwell on Local Machine/Cluster:

To set up Cromwell, refer to the guidelines provided here: [Cromwell Installation Guidelines](https://cromwell.readthedocs.io/en/stable/tutorials/FiveMinuteIntro/). Begin by testing an example WDL to ensure successful setup.

### B) Clone the repository:

To test this WDL workflow on your local machine or on a cluster, please clone this repository using either of the following methods:  

1) **Direct Download**: Navigate to the repository and click on "Code" at the upper right corner, then select "Download ZIP". Move the downloaded .zip file to your desired directory on your local machine/cluster and extract its contents.
2) **Git Clone**: Execute the command `git clone https://github.com/broadinstitute/stp_segmentation_wdl.git` to clone the repository and extract the WDL scripts onto your local machine/cluster.

### C) Get Toy Datasets:

Additionally, if you wish to experiment with toy MERSCOPE and Xenium datasets (10,000x10,000 pixels) designed to validate the functionality of the STP cell segmentation pipeline, please contact the STP computational team: [STP Computational Team GitHub](https://github.com/orgs/broadinstitute/teams/stp).

### D) Run Toy WDL on Cromwell:

### E) Run Segmentation WDL Locally 

### F) View Outputs
