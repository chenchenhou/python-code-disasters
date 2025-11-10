pipeline {
    agent any

    environment {
        // Defined in Kubernetes Deployment, but safe to set here for visibility/override
        SONAR_HOST_URL = "http://sonarqube:9000"
        BUCKET = "${env.BUCKET}" // GCS bucket created by Terraform
        DATAPROC_CLUSTER = "${env.DATAPROC_CLUSTER}" // Dataproc cluster name
        DATAPROC_REGION = "${env.DATAPROC_REGION}" // Dataproc region
        HADOOP_INPUT_PATH = "gs://${BUCKET}/repo-${BUILD_NUMBER}/files/"
        HADOOP_OUTPUT_PATH = "gs://${BUCKET}/output-${BUILD_NUMBER}/"
    }

    stages {
        stage('Checkout') {
            steps {
                // Clones the 'master' branch due to your job configuration
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def result = sh(
                        script: """
                        sonar-scanner \
                            -Dsonar.projectKey=python-code-disasters \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=admin \
                            -Dsonar.password=admin \
                            -Dsonar.qualitygate.wait=true
                        """,
                        returnStdout: true
                    ).trim()

                    echo result

                    if (result.contains("QUALITY GATE STATUS: FAILED")) {
                        error("Quality Gate failed, aborting pipeline")
                    }
                }
            }
        }
        //TODO: change to terraform
        stage('Prepare and Run Hadoop Job') {
            steps {
                script {
                    // 1. Upload source code and MapReduce scripts to GCS
                    sh """
                        # Recursively copy all repository files to a unique GCS input path
                        gsutil -m cp -r . ${HADOOP_INPUT_PATH}
                        
                        # Copy mapper/reducer to GCS where Dataproc can access them
                        gsutil cp hadoop/mapper.py gs://${BUCKET}/mapper.py
                        gsutil cp hadoop/reducer.py gs://${BUCKET}/reducer.py
                        
                        echo "Uploaded files to GCS for MapReduce input."
                    """
                    
                    // 2. Submit the MapReduce Job to Dataproc (GCloud CLI is in your Docker image)
                    sh """
                        gcloud \
                        dataproc jobs submit hadoop \
                        --cluster=${DATAPROC_CLUSTER} \
                        --region=${DATAPROC_REGION} \
                        --jar=file:///usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
                        -- \
                        -D mapreduce.input.fileinputformat.input.dir.recursive=true \
                        -files gs://${BUCKET}/mapper.py,gs://${BUCKET}/reducer.py \
                        -input ${HADOOP_INPUT_PATH} \
                        -output ${HADOOP_OUTPUT_PATH} \
                        -mapper "python3 mapper.py" \
                        -reducer "python3 reducer.py"
                        
                        echo "Hadoop job submitted. Output will be in ${HADOOP_OUTPUT_PATH}"
                    """
                }
            }
        }

        stage('Display Results') {
            steps {
                script {
                    // Display the final result (as required by the prompt)
                    echo "--- MapReduce Line Count Results ---"
                    sh "gsutil cat ${HADOOP_OUTPUT_PATH}part-*"
                }
            }
        }
    }
}