def comms_agent(scenario, plan, prev):
    alerts = [{"zone":"Z1","msg":"Proceed to pickup P1 at 09:10"}]
    return {"alerts": alerts, "planVersion": plan["version"]}
