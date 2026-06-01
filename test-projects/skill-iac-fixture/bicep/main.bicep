// scan-iac-security fixture — Azure Bicep misconfigurations
// Intentionally vulnerable — do not deploy

param location string = resourceGroup().location

// IAC-BICEP-001: Storage account with public blob access enabled
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'vulnerablestorage001'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: true           // IAC-BICEP-001: public blob access
    supportsHttpsTrafficOnly: false       // IAC-BICEP-002: HTTP allowed
    minimumTlsVersion: 'TLS1_0'          // IAC-BICEP-003: old TLS version
    allowSharedKeyAccess: true            // IAC-BICEP-004: shared key auth
  }
}

// IAC-BICEP-005: Key Vault with public network access and no soft delete
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: 'vulnerable-kv-001'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableSoftDelete: false               // IAC-BICEP-005: no soft delete
    enablePurgeProtection: false          // IAC-BICEP-006: can purge secrets permanently
    networkAcls: {
      defaultAction: 'Allow'             // IAC-BICEP-007: all networks allowed
      bypass: 'AzureServices'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: '*'                     // IAC-BICEP-008: all service principals
        permissions: {
          secrets: ['get', 'list', 'set', 'delete', 'purge']
          keys: ['all']
        }
      }
    ]
  }
}

// IAC-BICEP-009: SQL Server with public access and weak admin password
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: 'vulnerable-sql-server'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'Bicep_SQL_P@ssw0rd123!'  // IAC-BICEP-009: hardcoded
    publicNetworkAccess: 'Enabled'        // IAC-BICEP-010: public access
    minimalTlsVersion: '1.0'             // IAC-BICEP-011: old TLS
  }
}

// IAC-BICEP-012: NSG rule allowing all inbound traffic
resource nsg 'Microsoft.Network/networkSecurityGroups@2022-07-01' = {
  name: 'vulnerable-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-all-inbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'       // IAC-BICEP-012: all sources
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'allow-rdp'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '3389'   // RDP
          sourceAddressPrefix: '*'       // IAC-BICEP-013: RDP from internet
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}
