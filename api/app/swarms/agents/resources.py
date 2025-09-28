def resources_agent(scenario, demand, transport, shelter, prev):
    buses = scenario.get("assets", {}).get("buses", 10)
    vans = scenario.get("assets", {}).get("med_vans", 5)
    coverage = min(1.0, (buses*50 + vans*8) / 1000)
    unmet = max(0, int(1000 - (buses*50 + vans*8)))
    return {"buses": buses, "vans": vans, "coverage": coverage, "unmetDemand": unmet}
