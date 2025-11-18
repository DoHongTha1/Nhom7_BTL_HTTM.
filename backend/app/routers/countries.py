"""
Country metadata endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from sqlalchemy import desc

from app.database import SessionLocal, CountryData

router = APIRouter()

ASEAN_COUNTRIES = [
    {"code": "VN", "name": "Việt Nam"},
    {"code": "TH", "name": "Thái Lan"},
    {"code": "MY", "name": "Malaysia"},
    {"code": "SG", "name": "Singapore"},
    {"code": "PH", "name": "Philippines"},
    {"code": "ID", "name": "Indonesia"},
    {"code": "KH", "name": "Campuchia"},
    {"code": "LA", "name": "Lào"},
    {"code": "MM", "name": "Myanmar"},
    {"code": "BN", "name": "Brunei"},
]

DEFAULT_AGE_DISTRIBUTION = {
    "VN": [
        {"label": "0-14", "male": 9.8, "female": 9.7},
        {"label": "15-29", "male": 11.2, "female": 10.7},
        {"label": "30-44", "male": 10.1, "female": 10.0},
        {"label": "45-59", "male": 6.8, "female": 7.1},
        {"label": "60+", "male": 4.2, "female": 5.2},
    ],
    "TH": [
        {"label": "0-14", "male": 7.8, "female": 7.5},
        {"label": "15-29", "male": 10.1, "female": 9.8},
        {"label": "30-44", "male": 9.6, "female": 9.5},
        {"label": "45-59", "male": 7.2, "female": 7.4},
        {"label": "60+", "male": 5.0, "female": 5.8},
    ],
    "MY": [
        {"label": "0-14", "male": 8.0, "female": 7.6},
        {"label": "15-29", "male": 9.1, "female": 8.8},
        {"label": "30-44", "male": 7.9, "female": 7.8},
        {"label": "45-59", "male": 5.9, "female": 6.0},
        {"label": "60+", "male": 3.1, "female": 3.6},
    ],
    "SG": [
        {"label": "0-14", "male": 4.6, "female": 4.4},
        {"label": "15-29", "male": 9.0, "female": 8.3},
        {"label": "30-44", "male": 12.1, "female": 11.8},
        {"label": "45-59", "male": 7.5, "female": 7.6},
        {"label": "60+", "male": 5.8, "female": 6.4},
    ],
    "PH": [
        {"label": "0-14", "male": 17.5, "female": 16.9},
        {"label": "15-29", "male": 13.9, "female": 13.2},
        {"label": "30-44", "male": 9.0, "female": 8.5},
        {"label": "45-59", "male": 5.5, "female": 5.2},
        {"label": "60+", "male": 2.8, "female": 3.4},
    ],
    "ID": [
        {"label": "0-14", "male": 17.1, "female": 16.5},
        {"label": "15-29", "male": 15.0, "female": 14.3},
        {"label": "30-44", "male": 11.7, "female": 11.3},
        {"label": "45-59", "male": 8.3, "female": 8.0},
        {"label": "60+", "male": 4.2, "female": 4.8},
    ],
    "KH": [
        {"label": "0-14", "male": 15.9, "female": 15.4},
        {"label": "15-29", "male": 11.3, "female": 10.9},
        {"label": "30-44", "male": 7.5, "female": 7.2},
        {"label": "45-59", "male": 4.2, "female": 4.1},
        {"label": "60+", "male": 2.3, "female": 2.5},
    ],
    "LA": [
        {"label": "0-14", "male": 17.0, "female": 16.5},
        {"label": "15-29", "male": 11.0, "female": 10.4},
        {"label": "30-44", "male": 6.1, "female": 5.8},
        {"label": "45-59", "male": 3.2, "female": 3.1},
        {"label": "60+", "male": 1.4, "female": 1.6},
    ],
    "MM": [
        {"label": "0-14", "male": 13.8, "female": 13.4},
        {"label": "15-29", "male": 11.9, "female": 11.4},
        {"label": "30-44", "male": 8.7, "female": 8.4},
        {"label": "45-59", "male": 5.8, "female": 5.6},
        {"label": "60+", "male": 3.2, "female": 3.7},
    ],
    "BN": [
        {"label": "0-14", "male": 5.0, "female": 4.8},
        {"label": "15-29", "male": 7.4, "female": 7.1},
        {"label": "30-44", "male": 7.0, "female": 6.8},
        {"label": "45-59", "male": 3.8, "female": 3.6},
        {"label": "60+", "male": 1.6, "female": 1.7},
    ],
}


def _format_number(value: float) -> float:
    return float(value) if value is not None else 0.0


def _generate_insights(record: CountryData) -> List[str]:
    population = _format_number(record.population)
    birth_rate = _format_number(record.birth_rate)
    death_rate = _format_number(record.death_rate)
    growth_rate = birth_rate - death_rate if record.growth_rate is None else record.growth_rate
    gdp = _format_number(record.gdp_per_capita)

    insights = [
        f"Dân số hiện tại ~{population:,.0f} người.",
        f"Tỷ lệ sinh {birth_rate:.2f}% - Tỷ lệ tử {death_rate:.2f}‰ - Tăng trưởng {growth_rate:.2f}%.",
        f"GDP bình quân đầu người ~{gdp:,.0f} USD.",
    ]

    if growth_rate > 1.0:
        insights.append("Dân số tiếp tục tăng nhanh – cần chú trọng hạ tầng và dịch vụ công.")
    elif growth_rate > 0:
        insights.append("Tăng trưởng chậm lại – ưu tiên nâng năng suất lao động.")
    else:
        insights.append("Dân số suy giảm – cần chính sách hỗ trợ gia đình trẻ và lao động.")

    return insights


def _generate_research(record: CountryData) -> List[Dict[str, str]]:
    research = []
    gdp = _format_number(record.gdp_per_capita)
    birth_rate = _format_number(record.birth_rate)
    death_rate = _format_number(record.death_rate)

    research.append({
        "title": "Theo dõi cân bằng sinh – tử",
        "description": f"Tỷ lệ sinh {birth_rate:.1f}% so với tỷ lệ tử {death_rate:.1f}%. Cần chính sách phù hợp để ổn định quy mô dân số."
    })

    if gdp:
        research.append({
            "title": "Động lực kinh tế",
            "description": f"GDP/người hiện ~{gdp:,.0f} USD. Đề xuất tập trung vào nâng cao kỹ năng lao động và chuyển dịch cơ cấu."
        })

    research.append({
        "title": "Chính sách đô thị hóa",
        "description": "Theo dõi tốc độ đô thị hóa và phân bổ nguồn lực cho y tế, giáo dục, hạ tầng."
    })

    return research


def _map_stat(value: float, label: str, key: str, fmt: str | None = None, accent: str | None = None):
    entry = {"key": key, "label": label, "value": value}
    if fmt:
        entry["format"] = fmt
    if accent:
        entry["accent"] = accent
    return entry

def _safe_growth(record: CountryData) -> float:
    if record.growth_rate is not None:
        return record.growth_rate
    if record.birth_rate is not None and record.death_rate is not None:
        return record.birth_rate - record.death_rate
    return 0.0

def build_profile(country_info: Dict[str, str], record: CountryData) -> Dict:
    stats = [
        _map_stat(_format_number(record.population) / 1_000_000, "Dân số (triệu)", "population", accent="blue"),
        _map_stat(_format_number(record.birth_rate), "Tỷ lệ sinh (%)", "birthRate", fmt="number"),
        _map_stat(_format_number(record.death_rate), "Tỷ lệ tử (%)", "deathRate", fmt="number"),
        _map_stat(_safe_growth(record), "Tăng trưởng (%)", "growth", fmt="number", accent="green"),
        _map_stat(_format_number(record.gdp_per_capita), "GDP/người (USD)", "gdp", fmt="currency", accent="purple"),
    ]

    form_preset = {
        "name": country_info["name"],
        "countryCode": country_info["code"],
        "population": _format_number(record.population),
        "birthRate": _format_number(record.birth_rate),
        "deathRate": _format_number(record.death_rate),
        "gdpPerCapita": _format_number(record.gdp_per_capita),
        "urbanization": _format_number(record.urbanization),
        "educationIndex": _format_number(record.education_index or 0.7),
        "healthcareSpending": _format_number(record.healthcare_spending or 5.0),
        "fertilityRate": _format_number(record.fertility_rate or 2.0),
        "medianAge": _format_number(record.median_age or 32),
        "lifeExpectancy": _format_number(record.life_expectancy or 74),
    }

    return {
        "code": country_info["code"],
        "name": country_info["name"],
        "formPreset": form_preset,
        "stats": stats,
        "insights": _generate_insights(record),
        "research": _generate_research(record),
        "ageDistribution": DEFAULT_AGE_DISTRIBUTION.get(country_info["code"], []),
    }


@router.get("/countries/asean")
async def get_asean_countries():
    session = SessionLocal()
    profiles = []
    missing_codes = []

    try:
        for country in ASEAN_COUNTRIES:
            record = (
                session.query(CountryData)
                .filter(CountryData.country_code == country["code"])
                .order_by(desc(CountryData.year))
                .first()
            )
            if not record:
                missing_codes.append(country["code"])
                continue
            profiles.append(build_profile(country, record))
    finally:
        session.close()

    if not profiles:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu cho các quốc gia yêu cầu.")

    return {"countries": profiles, "missing": missing_codes}

