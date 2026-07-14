"""SQLite store for port-terminal container counts."""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ports.db")

SEED_PORTS: list[tuple[str, int]] = [
    ("JNPT-CT", 12540),
    ("JNPT-ET", 11875),
    ("MUN-CT", 14230),
    ("MUN-NT", 13680),
    ("CHN-CT", 10250),
    ("CHN-ST", 9640),
    ("KAT-CT", 7840),
    ("KMR-ET", 7265),
    ("HAZ-CT", 8950),
    ("HAZ-ET", 8410),
    ("KDL-CT", 7920),
    ("KDL-WT", 8155),
    ("PPV-CT", 6830),
    ("PPV-ST", 6415),
    ("DAH-CT", 5120),
    ("DAH-ET", 5480),
    ("VTZ-CT", 8855),
    ("VTZ-ET", 8320),
    ("GGV-CT", 6650),
    ("KRI-CT", 7345),
    ("KRI-ST", 6895),
    ("KAK-CT", 5930),
    ("KAK-ET", 5650),
    ("PRD-CT", 6150),
    ("PRD-ET", 5810),
    ("DMR-CT", 5425),
    ("DMR-ET", 5185),
    ("GPR-CT", 4210),
    ("GPR-ET", 3980),
    ("CCU-DT", 7525),
    ("CCU-RT", 6985),
    ("HAL-CT", 6615),
    ("COK-CT", 7310),
    ("COK-WT", 6870),
    ("VLD-CT", 9480),
    ("NML-CT", 6025),
    ("NML-ET", 5740),
    ("MRM-CT", 4965),
    ("MRM-ET", 4735),
    ("TUT-CT", 7085),
    ("TUT-ET", 6745),
    ("KRK-CT", 4380),
    ("KRK-ET", 4155),
    ("BVN-CT", 3920),
    ("BVN-ET", 3765),
    ("JAI-CT", 4510),
    ("JAI-ET", 4325),
    ("DRT-CT", 4050),
    ("DRT-ET", 3895),
    ("BEP-CT", 2950),
    ("BEP-ET", 2810),
    ("PBL-CT", 2120),
    ("PBL-ET", 1985),
    ("CUD-CT", 2545),
    ("CUD-ET", 2410),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS port_containers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                port_terminal TEXT NOT NULL UNIQUE,
                containers INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_data() -> None:
    conn = get_connection()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO port_containers (port_terminal, containers) "
            "VALUES (?, ?)",
            SEED_PORTS,
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    seed_data()
    print(f"Seeded {len(SEED_PORTS)} port terminals into {DB_PATH}")
