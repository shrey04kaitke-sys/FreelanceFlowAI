from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CostItem:
    description: str
    hours: float = 0.0
    cost: float = 0.0

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Each cost item needs a description.")
        if self.hours < 0 or self.cost < 0:
            raise ValueError("Hours and costs cannot be negative.")


def calculate_estimate(items: list[CostItem], hourly_rate: float, contingency_percent: float = 0.0) -> dict:
    if hourly_rate < 0 or contingency_percent < 0:
        raise ValueError("Rate and contingency cannot be negative.")
    rows = []
    subtotal = 0.0
    for item in items:
        labor = item.hours * hourly_rate
        line_total = labor + item.cost
        subtotal += line_total
        rows.append({**asdict(item), "labor": round(labor, 2), "total": round(line_total, 2)})
    contingency = subtotal * contingency_percent / 100
    return {"items": rows, "subtotal": round(subtotal, 2), "contingency": round(contingency, 2), "total": round(subtotal + contingency, 2)}
