# Jenkins Setup Instructions

**Important:**

If you are using Jenkins for CI/CD, make sure to configure your Jenkins job as follows:

- In the Jenkins web interface, go to your job and click **Configure**.
- Under the **Pipeline** section:
  - Set **Definition** to `Pipeline script from SCM`.
  - Set **Script Path** to `messaging_app/Jenkinsfile`.
- Save and run the job.

This ensures Jenkins uses the correct pipeline script for this project.
