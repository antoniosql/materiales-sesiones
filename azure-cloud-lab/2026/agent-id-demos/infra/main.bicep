// Azure Cloud Lab 2026 · Entra Agent ID · infraestructura base de las demos (FraSoHome)
// Storage sin claves compartidas, entorno de Container Apps, ACR, managed identities y,
// opcionalmente, un proyecto de Foundry con un modelo desplegado.
targetScope = 'resourceGroup'

@description('Región. Foundry Agent Service y Container Apps deben estar disponibles.')
param location string = resourceGroup().location

@description('Sufijo corto en minúsculas para nombres globales (storage, ACR, Foundry).')
@minLength(3)
@maxLength(8)
param suffix string

@description('Object ID de quien despliega (Nuria): recibe permisos de datos en Storage y de usuario en Foundry.')
param deployerPrincipalId string

@description('Crear la cuenta y el proyecto de Foundry. false si reutilizas uno existente.')
param deployFoundry bool = true

param foundryProjectName string = 'fs-agentes-prj'
param modelName string = 'gpt-4.1-mini'
param modelVersion string = '2025-04-14'
param modelCapacity int = 30

var storageName = 'stfrasohome${suffix}'
var acrName = 'acrfrasohome${suffix}'
var tags = { evento: 'azure-cloud-lab-2026', escenario: 'frasohome', demo: 'entra-agent-id' }

// Roles integrados
var roleStorageBlobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var roleAcrPull = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-frasohome-agents'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-frasohome-agents'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}

// Identidad para descargar imágenes. No es la del agente: esa solo es credencial del blueprint.
resource idPull 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-frasohome-acrpull'
  location: location
  tags: tags
}

// Credencial del blueprint bp-frasohome-operaciones (federated credential). Sin roles propios.
resource idTriage 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-fs-triage'
  location: location
  tags: tags
}

resource pullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, idPull.id, roleAcrPull)
  scope: acr
  properties: {
    principalId: idPull.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleAcrPull)
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    allowSharedKeyAccess: false   // solo Entra ID: ni claves ni SAS
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blob 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource cDevoluciones 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blob
  name: 'devoluciones'
}

resource cBuzon 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blob
  name: 'buzon-devoluciones'
}

resource cResultados 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blob
  name: 'triage-resultados'
}

resource deployerBlob 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, deployerPrincipalId, roleStorageBlobDataContributor)
  scope: storage
  properties: {
    principalId: deployerPrincipalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleStorageBlobDataContributor)
  }
}

module foundry 'modules/foundry.bicep' = if (deployFoundry) {
  name: 'foundry'
  params: {
    location: location
    accountName: 'aif-frasohome-${suffix}'
    projectName: foundryProjectName
    modelName: modelName
    modelVersion: modelVersion
    modelCapacity: modelCapacity
    deployerPrincipalId: deployerPrincipalId
    tags: tags
  }
}

output storageAccountName string = storage.name
output storageAccountId string = storage.id
output containerAppsEnvironmentId string = cae.id
output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output pullIdentityId string = idPull.id
output triageIdentityId string = idTriage.id
output triageIdentityClientId string = idTriage.properties.clientId
output triageIdentityPrincipalId string = idTriage.properties.principalId
output foundryProjectEndpoint string = deployFoundry ? foundry!.outputs.projectEndpoint : ''
output foundryAccountName string = deployFoundry ? foundry!.outputs.accountName : ''
