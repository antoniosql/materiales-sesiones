variable "proyecto" {
  description = "Prefijo de los workspaces: <proyecto>-<función>-<entorno>"
  type        = string
}

variable "repositorio" {
  description = "Repositorio que gestiona estos workspaces (aparece en su descripción)"
  type        = string
}

variable "capacidades" {
  description = "ID de la capacidad de Fabric para cada entorno"
  type        = map(string)
}

variable "sp_despliegue_object_id" {
  description = "Object ID del service principal que usa el pipeline de despliegue"
  type        = string
}

variable "grupos" {
  description = "Object ID de los grupos de Entra ID: ingenieria, analitica"
  type        = map(string)
}
