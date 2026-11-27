# Puerta 1 · Asistente de Devoluciones (Copilot Studio)

El agente de Copilot Studio no se crea por script: se monta en el portal y luego `agentid copilot` le pone el
estado de partida de la demo 1 (sponsor Marta R. y `FraSoHome.Carril = Produccion`).

## 1 · Crear el agente

El agente completo está en [`agente/`](agente/): instrucciones, origen de conocimiento (`knowledge/kb-operaciones.yaml`)
y tres topics (`topics/*.mcs.yaml`). Es el mismo agente del Bizz Summit 2026.

1. Copilot Studio → entorno de demo → **Create** → **Asistente de Devoluciones FraSoHome**.
2. Instrucciones: [`agente/instrucciones.md`](agente/instrucciones.md). Topics: impórtalos desde `agente/topics/`.
3. Knowledge: sitio de SharePoint `FraSoHome-KB-Operaciones` con las políticas FS-KB (ver `agente/knowledge/kb-operaciones.yaml`).
4. Publica en **Teams y Microsoft 365 Copilot** y pregúntale algo varias veces el día anterior, como Álvaro:
   así hay inicios de sesión en los logs para el beat 2 de la demo 1.

Desde mayo de 2026, Copilot Studio da **Entra Agent ID** automáticamente a cada agente nuevo (blueprint global
*Microsoft Copilot Studio agent identity blueprint*). Si el agente ya existía con app registration, mígralo desde el
Power Platform admin center: es lo que se cuenta en la demo («lo migró Nuria en octubre»).

## 2 · Dejarlo como en la demo 1

```powershell
agentid copilot
```

Busca la identidad por nombre visible. Si encuentra varias o ninguna, copia su object ID desde Copilot Studio →
**Settings → Advanced → Metadata → Entra Agent ID** a `COPILOT_AGENT_IDENTITY_ID` en `.env` y repite.

En la demo 4, `agentid demo4 sponsors` cambia sus sponsors a **Jorge P.** + grupo **FraSoHome · Responsables de
tienda**, y `agentid ensayo reiniciar` vuelve a dejar a Marta.
