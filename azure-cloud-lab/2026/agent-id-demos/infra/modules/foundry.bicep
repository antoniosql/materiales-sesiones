// Cuenta de Foundry (AIServices) con un proyecto y un modelo desplegado.
param location string
param accountName string
param projectName string
param modelName string
param modelVersion string
param modelCapacity int
param deployerPrincipalId string
param tags object

var roleAzureAIUser = '53ca6127-db72-4b80-b1b0-d745d6d5456d' // «Azure AI User», renombrado «Foundry User»

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: accountName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: accountName
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}

resource model 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: modelName
  sku: {
    name: 'GlobalStandard'
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: account
  name: projectName
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'FraSoHome · agentes'
    description: 'Proyecto de la demo 2 de Azure Cloud Lab 2026 (Entra Agent ID)'
  }
}

resource deployerUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, deployerPrincipalId, roleAzureAIUser)
  scope: account
  properties: {
    principalId: deployerPrincipalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleAzureAIUser)
  }
}

output accountName string = account.name
output projectName string = project.name
output projectEndpoint string = 'https://${accountName}.services.ai.azure.com/api/projects/${projectName}'
