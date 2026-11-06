# Workspaces, capacidad y permisos como código.
# Validado con terraform validate y tflint contra el provider microsoft/fabric 1.14.0.

terraform {
  required_version = ">= 1.6"
  required_providers {
    fabric = {
      source  = "microsoft/fabric"
      version = "~> 1.0"
    }
  }
  # backend "azurerm" { ... }   # estado remoto obligatorio en cuanto haya más de una persona
}

provider "fabric" {}

locals {
  entornos  = ["dev", "test", "prod"]
  funciones = ["datos", "ing", "ana"]

  workspaces = {
    for par in setproduct(local.entornos, local.funciones) :
    "${par[1]}-${par[0]}" => { entorno = par[0], funcion = par[1] }
  }

  # Quién tiene qué rol en cada función. En test y prod nadie edita a mano: solo lectura.
  roles = {
    datos = { ingenieria = "Contributor", analitica = "Viewer" }
    ing   = { ingenieria = "Contributor" }
    ana   = { analitica = "Contributor", ingenieria = "Viewer" }
  }

  asignaciones = merge([
    for clave, ws in local.workspaces : {
      for grupo, rol in local.roles[ws.funcion] :
      "${clave}-${grupo}" => {
        workspace = clave
        grupo     = grupo
        rol       = ws.entorno == "dev" ? rol : "Viewer"
      }
    }
  ]...)
}

resource "fabric_workspace" "ws" {
  for_each     = local.workspaces
  display_name = "${var.proyecto}-${each.value.funcion}-${each.value.entorno}"
  description  = "Gestionado por Terraform (${var.repositorio}). No modificar a mano."
  capacity_id  = var.capacidades[each.value.entorno]
}

# La identidad del pipeline de despliegue es la única que escribe en test y prod
resource "fabric_workspace_role_assignment" "despliegue" {
  for_each     = fabric_workspace.ws
  workspace_id = each.value.id
  principal = {
    id   = var.sp_despliegue_object_id
    type = "ServicePrincipal"
  }
  role = "Contributor"
}

resource "fabric_workspace_role_assignment" "equipos" {
  for_each     = local.asignaciones
  workspace_id = fabric_workspace.ws[each.value.workspace].id
  principal = {
    id   = var.grupos[each.value.grupo]
    type = "Group"
  }
  role = each.value.rol
}
