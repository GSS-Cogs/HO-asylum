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
                script {
                    ansiColor('xterm') {
                        sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'Home Office, Immigration Statistics October to December 2016, Asylum table as 01 q.ipynb'"
                        sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'as_04 Asylum applications from main applicants and dependants.ipynb'"
                        sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'Asylum seekers receiving support(As_16_q).ipynb'"
                        sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'Refugees resettled(As_19_q).ipynb'"
                        sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'Arrivals under Dublin regulations(As_22_q).ipynb'"
                    }
                }
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'cloudfluff/csvlint'
                    reuseNode true
                }
            }
            steps {
                script {
                    ansiColor('xterm') {
                        sh "csvlint -s schema.json"
                    }
                }
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    jobDraft.replace()
                    uploadTidy(['out/as_01_q.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                               'migration/ho-asylum/as_01',
                               'out/as_01_q.csv-metadata.trig')
                    uploadTidy(['out/as_04.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                               'migration/ho-asylum/as_04',
                               'out/as_04.csv-metadata.trig')
                    uploadTidy(['out/as_16_q.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                               'migration/ho-asylum/as_16_q',
                               'out/as_16_q.csv-metadata.trig')
                    uploadTidy(['out/as_19_q.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                               'migration/ho-asylum/as_19_q',
                               'out/as_19_q.csv-metadata.trig')
                    uploadTidy(['out/as_22_q.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv',
                               'migration/ho-asylum/as_22_q',
                               'out/as_22_q.csv-metadata.trig')
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
            script {
                archiveArtifacts 'out/*'
                updateCard "5b472c73559a6db3a04e9ebc"
            }
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
