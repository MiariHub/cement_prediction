def in_range_flags(input_dict: dict, bounds: dict) -> dict:
    return {
        k: bounds[k][0] <= float(v) <= bounds[k][1]
        for k, v in input_dict.items()
    }

def pass_fail(pred: float, spec_min: float) -> str:
    return "PASS" if pred >= spec_min else "FAIL"

def status_badge(pred: float, spec_min: float) -> str:
    if pred >= spec_min:
        return "✅ Pass"
    elif pred >= spec_min * 0.9:
        return "⚠️ Near Fail"
    else:
        return "❌ Fail"

def out_of_bounds_highlight(k: str, val: float, lo: float, hi: float) -> str:
    icon = "🟥" if val < lo or val > hi else "✅"
    return f"{icon} **{k}**: {val:.2f} (Range: {lo}–{hi})"
