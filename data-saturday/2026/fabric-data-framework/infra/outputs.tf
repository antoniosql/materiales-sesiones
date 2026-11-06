output "workspace_ids" {
  description = "ID de cada workspace. Se copian a las vars de cada GitHub Environment: WS_DATOS_ID, WS_ING_ID, WS_ANA_ID"
  value       = { for clave, ws in fabric_workspace.ws : clave => ws.id }
}
