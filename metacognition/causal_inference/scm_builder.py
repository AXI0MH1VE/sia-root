from __future__ import annotations

def build_scm_from_dataframe(df, treatment: str, outcome: str, graph_dot: str):
    from dowhy import CausalModel
    model = CausalModel(data=df, treatment=treatment, outcome=outcome, graph=graph_dot)
    identified = model.identify_effect()
    estimate = model.estimate_effect(identified, method_name="backdoor.linear_regression")
    return model, identified, estimate
