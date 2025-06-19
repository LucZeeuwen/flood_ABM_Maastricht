import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from run_simulation import initialize_model

# Parameters
threat_threshold = 0.75
coping_threshold = 0.50
step_to_plot = 5
threat_increments = [0.1, 0.2, 0.3, 0.4, 0.5]
social_thresholds = [0, 0.5, 0.75, 1]
neighbourhoods = ["Randwyck", "Heugemerveld", "Heugem"]

records = []

for social_threshold in social_thresholds:
    for elevated in neighbourhoods:
        for increment in threat_increments:
            model = initialize_model(threat_threshold=threat_threshold, coping_threshold=coping_threshold, social_threshold=social_threshold)
            # Set threat appraisal for each agent
            for agent in model.schedule.agents:
                if agent.zone == elevated:
                    agent.threat_score = min(agent.threat_score + increment * 5, 5.0)
                else:
                    agent.threat_score = agent.threat_score  # unchanged
            for step in range(1, step_to_plot + 1):
                model.step()
            mitigators = sum(1 for agent in model.schedule.agents if getattr(agent, 'action', None) == 'mitigate' and agent.zone == elevated)
            records.append({
                'Neighbourhood': elevated,
                'Increment': increment,
                'Mitigators': mitigators,
                'SocialThreshold': social_threshold
            })

# Create DataFrame
results_df = pd.DataFrame(records)

# Plot: FacetGrid with one grouped bar plot per social threshold
sns.set(style="whitegrid")
g = sns.FacetGrid(results_df, col="SocialThreshold", col_wrap=2, height=5, sharey=True)
g.map_dataframe(sns.barplot, x='Increment', y='Mitigators', hue='Neighbourhood', palette='deep')
g.add_legend(title='Neighbourhood')
g.set_titles(col_template="Social Threshold = {col_name}")
g.set_axis_labels('Threat Appraisal Increment (Elevated Neighbourhood)', 'Mitigating Agents at Step 5')
g.fig.subplots_adjust(top=0.85)
g.fig.suptitle('Mitigating Agents at Step 5\nLocal Threat Appraisal Increase by Neighbourhood\nGrouped by Social Threshold')
plt.savefig('output/mitigation_step5_grouped_barplot_social_thresholds.png', dpi=300)
plt.show() 