#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history" / "units"

INF_TEMPLATE = "WAEF Heavy Infantry Division"
TANK_TEMPLATE = "WAEF Medium Tank Division"

COUNTRIES = {
    "WEF": {"location": 6521, "file": "WAEF_WEF_1941.txt"},
    "EEF": {"location": 6380, "file": "WAEF_EEF_1941.txt"},
}


def infantry_template() -> str:
    return r'''division_template = {
    name = "WAEF Heavy Infantry Division"

    regiments = {
        heavy_infantry = { x = 0 y = 0 }
        heavy_infantry = { x = 0 y = 1 }
        heavy_infantry = { x = 0 y = 2 }

        heavy_infantry = { x = 1 y = 0 }
        heavy_infantry = { x = 1 y = 1 }
        heavy_infantry = { x = 1 y = 2 }

        heavy_infantry = { x = 2 y = 0 }
        heavy_infantry = { x = 2 y = 1 }
        heavy_infantry = { x = 2 y = 2 }

        artillery_brigade = { x = 3 y = 0 }
        artillery_brigade = { x = 3 y = 1 }
        artillery_brigade = { x = 3 y = 2 }

        anti_tank_brigade = { x = 4 y = 0 }
        anti_tank_brigade = { x = 4 y = 1 }
        anti_tank_brigade = { x = 4 y = 2 }
    }

    regimental_support = {
        regimental_artillery = { x = 0 y = 0 }
        regimental_anti_tank = { x = 0 y = 1 }
    }

    support = {
        normal_engineer = { x = 0 y = 0 }
        horse_logistics_company = { x = 0 y = 1 }
        horse_field_hospital = { x = 0 y = 2 }
        horse_signal_company = { x = 0 y = 3 }
        maintenance_company = { x = 0 y = 4 }

        recon = { x = 1 y = 0 }
        military_police = { x = 1 y = 1 }
        artillery = { x = 1 y = 2 }
        anti_air = { x = 1 y = 3 }
    }
}
'''


def tank_template() -> str:
    return r'''division_template = {
    name = "WAEF Medium Tank Division"

    regiments = {
        medium_armor = { x = 0 y = 0 }
        medium_armor = { x = 0 y = 1 }
        medium_armor = { x = 0 y = 2 }
        medium_armor = { x = 0 y = 3 }

        medium_armor = { x = 1 y = 0 }
        medium_armor = { x = 1 y = 1 }
        medium_armor = { x = 1 y = 2 }

        medium_armor = { x = 2 y = 0 }
        medium_armor = { x = 2 y = 1 }
        medium_armor = { x = 2 y = 2 }

        mechanized = { x = 3 y = 0 }
        mechanized = { x = 3 y = 1 }
        mechanized = { x = 3 y = 2 }
        mechanized = { x = 3 y = 3 }
    }

    regimental_support = {
        regimental_motorized_artillery = { x = 0 y = 0 }
        regimental_motorized_anti_tank = { x = 0 y = 1 }
    }

    support = {
        engineer = { x = 0 y = 0 }
        motorized_logistics_company = { x = 0 y = 1 }
        field_hospital = { x = 0 y = 2 }
        signal_company = { x = 0 y = 3 }
        mot_maintenance_company = { x = 0 y = 4 }

        mobile_recon = { x = 1 y = 0 }
        motorized_military_police = { x = 1 y = 1 }
        motorized_artillery = { x = 1 y = 2 }
        motorized_anti_air = { x = 1 y = 3 }
    }
}
'''


def division(name: str, template: str, location: int) -> str:
    return f'''    division = {{
        name = "{name}"
        location = {location}
        division_template = "{template}"
        start_experience_factor = 1.0
        start_equipment_factor = 1.0
        start_manpower_factor = 1.0
    }}
'''


def build(tag: str, location: int) -> str:
    chunks = [infantry_template(), "\n", tank_template(), "\nunits = {\n"]
    for i in range(1, 301):
        chunks.append(division(f"{tag} Heavy Infantry Division {i:03d}", INF_TEMPLATE, location))
    for i in range(1, 31):
        chunks.append(division(f"{tag} Medium Tank Division {i:03d}", TANK_TEMPLATE, location))
    chunks.append("}\n")
    return "".join(chunks)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for tag, cfg in COUNTRIES.items():
        content = build(tag, cfg["location"])
        path = OUT / cfg["file"]
        path.write_text(content, encoding="utf-8")
        if content.count("division = {") != 330:
            raise RuntimeError(f"{tag}: expected 330 divisions")
        if content.count("division_template = {") != 2:
            raise RuntimeError(f"{tag}: expected 2 templates")
        print(f"{tag}: wrote 300 infantry + 30 tank divisions to {path}")


if __name__ == "__main__":
    main()
