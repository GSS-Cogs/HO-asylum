pipeline {
    agent {
        label 'master'
    }
    triggers {
        upstream(upstreamProjects: '../Reference/ref_migration',
                 threshold: hudson.model.Result.SUCCESS)
    }
    stages {
        stage('Clean') {
            steps {
                sh 'rm -rf out'
            }
        }
        stage('Transform') {
            agent {
                docker {
                    image 'cloudfluff/databaker'
                    reuseNode true
                }
            }
            steps {
                sh "jupyter-nbconvert --to python --stdout 'create_dataset_metadata.ipynb' | ipython"
                sh "jupyter-nbconvert --output-dir=out --execute 'main.ipynb' --ExecutePreprocessor.interrupt_on_timeout=True --ExecutePreprocessor.timeout=600"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    jobDraft.replace()
                    uploadTidy(['out/as_01_q.csv'],'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv','asylum_as_01')
                    uploadTidy(['out/as_04.csv'],'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv','asylum_as_04')
                    uploadTidy(['out/as_16_q.csv'],'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv','asylum_as_16_q')
                    uploadTidy(['out/as_19_q.csv'],'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv','asylum_as_19_q')
                    uploadTidy(['out/as_22_q.csv'],'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv','asylum_as_22_q')
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    jobDraft.publish()
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
