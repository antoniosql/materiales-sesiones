// Azure Cloud Lab 2026 · Container Apps de las demos: servidor MCP (demo 2) y agente propio (demo 3)
targetScope = 'resourceGroup'

param location string = resourceGroup().location
param containerAppsEnvironmentId string
param acrLoginServer string
param pullIdentityId string
param triageIdentityId string
param triageIdentityClientId string
param storageAccountName string
param mcpImage string
param triageImage string

@description('Tenant de Entra donde viven el blueprint y la identidad de agente.')
param tenantId string = tenant().tenantId

@description('appId del blueprint bp-frasohome-operaciones.')
param blueprintAppId string

@description('Client id de la identidad de agente fs-triage-devoluciones.')
param agentIdentityClientId string

param pollSeconds int = 60

var tags = { evento: 'azure-cloud-lab-2026', escenario: 'frasohome', demo: 'entra-agent-id' }

resource mcp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-fs-devoluciones-mcp'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${pullIdentityId}': {} }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        { server: acrLoginServer, identity: pullIdentityId }
      ]
    }
    template: {
      containers: [
        {
          name: 'mcp'
          image: mcpImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            { name: 'STORAGE_ACCOUNT', value: storageAccountName }
            { name: 'DEVOLUCIONES_CONTAINER', value: 'devoluciones' }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

resource triage 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-fs-triage'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${pullIdentityId}': {}
      '${triageIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [
        { server: acrLoginServer, identity: pullIdentityId }
      ]
    }
    template: {
      containers: [
        {
          name: 'fs-triage-devoluciones'
          image: triageImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            { name: 'AZURE_TENANT_ID', value: tenantId }
            { name: 'AZURE_CLIENT_ID', value: triageIdentityClientId }
            { name: 'BLUEPRINT_APP_ID', value: blueprintAppId }
            { name: 'AGENT_IDENTITY_CLIENT_ID', value: agentIdentityClientId }
            { name: 'STORAGE_ACCOUNT', value: storageAccountName }
            { name: 'POLL_SECONDS', value: string(pollSeconds) }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

output mcpUrl string = 'https://${mcp.properties.configuration.ingress.fqdn}/mcp'
output triageAppName string = triage.name
