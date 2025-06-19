import random

def make_pmt_decision(agent, flood_level=0.0, threat_threshold=0.6, coping_threshold=0.6):
    scenario = getattr(agent.model, "selected_scenario", "default")

    threat_raw = agent.threat_score

    # Adjust threat for 'heugem_only'
    if scenario == "heugem_only" and agent.zone != "Heugem":
        threat_raw = 0.1  # Low threat for other zones

    threat = min(max(threat_raw / 5.0 + random.uniform(-0.03, 0.03), 0), 1)
    coping = min(max(agent.coping_score / 5.0 + random.uniform(-0.03, 0.03), 0), 1)

    if threat > threat_threshold and coping > coping_threshold:
        return "mitigate"
    elif threat > threat_threshold and coping <= coping_threshold:
        return "evacuate"
    else:
        return "do_nothing"


def apply_social_influence(agent, model, social_threshold=None):
    if not getattr(model, "use_social_ties", False):
        return

    # Find neighbors in same zone excluding self
    neighbors = [
        a for a in model.schedule.agents
        if a.zone == agent.zone and a != agent and getattr(a, "action", None) in ["evacuate", "mitigate"]
    ]

    if not neighbors:
        return

    influence_ratio = len(neighbors) / len([
        a for a in model.schedule.agents if a.zone == agent.zone and a != agent
    ])

    strength = getattr(agent, "social_network_strength", 0)
    if social_threshold is None:
        social_threshold = 0.6 - (strength * 0.05)  # default behavior

    if influence_ratio > social_threshold:
        agent.action = "mitigate"
        agent.was_influenced = True


def adjust_threat_with_social_influence(agent, influential_neighbors=1):
    """
    Optionally boost threat score slightly if neighbors are evacuating (not mandatory).
    """
    if influential_neighbors >= 1:
        agent.threat_score = min(1.0, agent.threat_score + 0.05)


# Optional alias for pre-flood phase
pre_flood_decision = make_pmt_decision
