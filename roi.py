def cement_roi(
    monthly_batches: int,
    volume_m3_per_batch: float,
    cement_content_kg_m3: float,
    overdesign_reduction_pct: float,
    cement_cost_per_ton: float,
    scrap_before_pct: float,
    scrap_after_pct: float,
    batch_cost_usd: float,
    lab_tests_per_month: int,
    hours_per_test: float,
    labor_rate_usd_h: float,
    implementation_cost_usd: float = 0.0,
):
    monthly_volume_m3 = monthly_batches * volume_m3_per_batch
    cement_saved_kg = monthly_volume_m3 * cement_content_kg_m3 * (overdesign_reduction_pct / 100.0)
    cement_saved_cost = (cement_saved_kg / 1000.0) * cement_cost_per_ton

    scrap_delta = max(0.0, (scrap_before_pct - scrap_after_pct) / 100.0)
    scrap_savings = monthly_batches * batch_cost_usd * scrap_delta

    lab_savings = lab_tests_per_month * hours_per_test * labor_rate_usd_h

    total_savings = cement_saved_cost + scrap_savings + lab_savings

    roi = None
    payback_months = None
    if implementation_cost_usd > 0:
        roi = ((total_savings - implementation_cost_usd) / implementation_cost_usd)
        if total_savings > 0:
            payback_months = implementation_cost_usd / total_savings

    return {
        "cement_saved_kg": cement_saved_kg,
        "cement_saved_cost": cement_saved_cost,
        "scrap_savings": scrap_savings,
        "lab_savings": lab_savings,
        "total_savings": total_savings,
        "roi": roi,
        "payback_months": payback_months,
    }
