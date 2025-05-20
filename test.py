- ${{ if eq(parameters.containerAnalysis, true) }}:
  - task: SnykSecurityScan@1
    displayName: 'Scan Docker Image for vulnerabilities with Snyk CLI'
    condition: ${{ parameters.branchConditionToTriggerTasks }}
    inputs:
      serviceConnectionEndpoint: ${{ parameters.SnykServiceConnection }}
      testType: 'container'
      dockerfilePath: '${{ parameters.dockerFile }}'
      dockerImageName: '${{parameters.containerRegistryName}}/${{parameters.dockerACRRepositoryName}}:${{parameters.dockerImageVersion}}'
      monitorWhen: 'always'
      severityThreshold: 'high'
      failOnIssues: '${{ parameters.containerFailOnIssues }}'
      organization: '${{ parameters.snykOrganization }}'
    continueOnError: true
