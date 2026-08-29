import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'civic_predict.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def severity_from_score(score):
    if score >= 75:
        return 'Critical'
    elif score >= 50:
        return 'High'
    elif score >= 25:
        return 'Medium'
    else:
        return 'Low'


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Drop existing tables
    for table in ['users', 'issues', 'activities', 'data_sources']:
        c.execute(f"DROP TABLE IF EXISTS {table}")

    # ── Create tables ──────────────────────────────────────────────
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        location_name TEXT NOT NULL,
        city TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        department TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        reported_date TEXT NOT NULL,
        description TEXT,
        predicted_trend TEXT,
        recommendation TEXT,
        complaint_count INTEGER DEFAULT 1,
        historical_incidents INTEGER DEFAULT 0,
        asset_condition TEXT DEFAULT 'Unknown',
        public_impact TEXT DEFAULT 'Medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        issue_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (issue_id) REFERENCES issues(id)
    )''')

    c.execute('''CREATE TABLE data_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'Connected',
        last_updated TIMESTAMP,
        records_count INTEGER DEFAULT 0,
        icon TEXT
    )''')

    # ── Users ──────────────────────────────────────────────────────
    users = [
        ('admin', 'admin123', 'Administrator', 'Administrator', 'All Departments'),
        ('analyst', 'analyst123', 'Rizky Pratama', 'Government Analyst', 'Diskominfo'),
        ('pupr', 'pupr123', 'Budi Santoso', 'Department Officer', 'Dinas PUPR'),
        ('dishub', 'dishub123', 'Ahmad Fauzi', 'Department Officer', 'Dinas Perhubungan'),
        ('lh', 'lh123', 'Siti Rahayu', 'Department Officer', 'Dinas Lingkungan Hidup'),
    ]
    c.executemany(
        "INSERT INTO users (username, password, name, role, department) VALUES (?,?,?,?,?)",
        users,
    )

    # ── Issues (50 mock issues) ────────────────────────────────────
    base_date = datetime(2026, 8, 16)

    issues_raw = [
        # ── Road Infrastructure (Dinas PUPR) ──
        ("Kerusakan Jalan Parah", "Road Infrastructure", "Jl. Ahmad Yani No. 45, Bekasi Barat", "Bekasi", -6.2350, 106.9750, "Dinas PUPR", 91, 47, 5, "Poor", "High", "Worsening", "Prioritize immediate field inspection and emergency repair. Coordinate resource allocation for damaged section."),
        ("Jalan Berlubang Besar", "Road Infrastructure", "Jl. Raya Bogor Km 12, Jakarta Timur", "Jakarta Timur", -6.2200, 106.8700, "Dinas PUPR", 78, 32, 4, "Poor", "High", "Worsening", "Deploy emergency patching team and install warning signage. Schedule permanent repair within 7 days."),
        ("Aspal Retak dan Mengelupas", "Road Infrastructure", "Jl. Gatot Subroto, Tangerang", "Tangerang", -6.2100, 106.6500, "Dinas PUPR", 63, 21, 3, "Fair", "Medium", "Stable", "Schedule resurfacing during low-traffic hours. Inspect underlying road foundation."),
        ("Paving Block Rusak", "Road Infrastructure", "Jl. Pahlawan, Depok", "Depok", -6.4100, 106.8000, "Dinas PUPR", 54, 18, 2, "Fair", "Medium", "Stable", "Replace damaged paving blocks and improve drainage around the area."),
        ("Jalan Ambles di Bahu Jalan", "Road Infrastructure", "Jl. Cileungsi, Bogor", "Bogor", -6.5800, 106.8500, "Dinas PUPR", 85, 38, 4, "Poor", "High", "Worsening", "Emergency stabilization required. Conduct soil investigation and repair subsidence."),
        ("Marka Jalan Memudar", "Road Infrastructure", "Jl. Sultan Agung, Bekasi Timur", "Bekasi", -6.2300, 107.0200, "Dinas PUPR", 35, 12, 1, "Fair", "Low", "Stable", "Repaint road markings during next scheduled maintenance cycle."),
        ("Trotoar Rusak dan Tidak Rata", "Road Infrastructure", "Jl. Thamrin, Jakarta Pusat", "Jakarta Pusat", -6.1900, 106.8250, "Dinas PUPR", 72, 28, 3, "Poor", "Medium", "Worsening", "Reconstruct sidewalk section. Ensure ADA-compliant access during repair."),
        ("Jembatan Retak Struktural", "Road Infrastructure", "Jembatan Ciliwung, Jakarta Selatan", "Jakarta Selatan", -6.2600, 106.8100, "Dinas PUPR", 95, 52, 6, "Poor", "High", "Worsening", "CRITICAL: Close bridge immediately for structural assessment. Deploy engineering team."),
        ("Speed Bump Rusak", "Road Infrastructure", "Jl. Kemang Pratama, Bekasi", "Bekasi", -6.2250, 106.9900, "Dinas PUPR", 28, 8, 1, "Fair", "Low", "Stable", "Rebuild speed bump during next road maintenance schedule."),
        ("Jalan Terendam Air", "Road Infrastructure", "Jl. Raya Cikarang, Bekasi", "Bekasi", -6.3600, 107.1500, "Dinas PUPR", 68, 25, 3, "Poor", "Medium", "Worsening", "Improve drainage to prevent recurring waterlogging. Install temporary pumping if needed."),

        # ── Flooding (Dinas PUPR / Dinas Lingkungan Hidup) ──
        ("Banjir Kiriman", "Flooding", "Kel. Jatiasih, Bekasi", "Bekasi", -6.2500, 106.9600, "Dinas PUPR", 88, 41, 5, "Poor", "High", "Worsening", "Activate emergency flood response. Deploy pumps and sandbags. Coordinate upstream water management."),
        ("Genangan Akibat Hujan", "Flooding", "Jl. Raya Bogor, Jakarta Timur", "Jakarta Timur", -6.2100, 106.8800, "Dinas PUPR", 74, 29, 4, "Fair", "Medium", "Stable", "Clear drainage channels. Monitor water levels and prepare evacuation if levels rise."),
        ("Banjir Rob Pesisir", "Flooding", "Muara Angke, Jakarta Utara", "Jakarta Utara", -6.1050, 106.7800, "Dinas PUPR", 82, 35, 4, "Poor", "High", "Worsening", "Strengthen coastal flood barriers. Install tidal monitoring sensors."),
        ("Banjir Sampah Menyumbat", "Flooding", "Kali Ciliwung, Jakarta Pusat", "Jakarta Pusat", -6.1800, 106.8350, "Dinas Lingkungan Hidup", 86, 39, 5, "Poor", "High", "Worsening", "Emergency cleanup of river blockage. Deploy waste collection teams and install trash barriers."),
        (" genangan Kronis", "Flooding", "Jl. Mangga Besar, Jakarta Barat", "Jakarta Barat", -6.1500, 106.8200, "Dinas PUPR", 71, 26, 4, "Poor", "Medium", "Stable", "Conduct drainage capacity study. Install additional pumping stations."),
        ("Banjir Area Perumahan", "Flooding", "Perumahan Mutiara Gading, Bekasi Timur", "Bekasi", -6.2400, 107.0100, "Dinas PUPR", 79, 33, 4, "Poor", "High", "Worsening", "Coordinate with developer for drainage improvement. Deploy temporary flood mitigation."),
        ("Luapan Sungai", "Flooding", "Kel. Pondok Gede, Bekasi", "Bekasi", -6.2650, 106.9800, "Dinas PUPR", 90, 44, 6, "Poor", "High", "Worsening", "EMERGENCY: Evacuate affected residents. Deploy emergency pumping and river dredging."),
        (" genangan di Underpass", "Flooding", "Underpass Senayan, Jakarta Pusat", "Jakarta Pusat", -6.2000, 106.8050, "Dinas Perhubungan", 83, 36, 4, "Poor", "High", "Worsening", "Install flood detection sensors and automatic barriers. Upgrade pumping capacity."),

        # ── Waste Management (Dinas Lingkungan Hidup) ──
        ("Tumpukan Sampah di Bantaran Sungai", "Waste Management", "Bantaran Kali Ciliwung, Depok", "Depok", -6.4050, 106.8100, "Dinas Lingkungan Hidup", 80, 34, 4, "Poor", "High", "Worsening", "Deploy cleanup crew immediately. Install river barriers and increase patrol frequency."),
        ("TPS Over Capacity", "Waste Management", "TPS Jl. Raya Bekasi, Bekasi Barat", "Bekasi", -6.2300, 106.9700, "Dinas Lingkungan Hidup", 73, 27, 4, "Poor", "Medium", "Worsening", "Increase waste collection frequency. Arrange temporary overflow storage."),
        ("Sampah Menumpuk di Pasar", "Waste Management", "Pasar Baru, Jakarta Pusat", "Jakarta Pusat", -6.1700, 106.8400, "Dinas Lingkungan Hidup", 66, 22, 3, "Fair", "Medium", "Stable", "Coordinate with market management for scheduled waste collection."),
        ("Lalat dan Bau dari TPA", "Waste Management", "TPA Bantar Gebang, Bekasi", "Bekasi", -6.3500, 107.0000, "Dinas Lingkungan Hidup", 77, 31, 4, "Poor", "Medium", "Worsening", "Implement odor control measures. Review waste processing capacity."),
        ("Sampah Plastik di Drainase", "Waste Management", "Jl. Kemang Raya, Jakarta Selatan", "Jakarta Selatan", -6.2550, 106.8150, "Dinas Lingkungan Hidup", 69, 24, 3, "Fair", "Medium", "Stable", "Organize community cleanup drives. Install drain covers to prevent plastic entry."),
        ("Pencemaran Sungai", "Waste Management", "Kali Sunter, Jakarta Utara", "Jakarta Utara", -6.1300, 106.8650, "Dinas Lingkungan Hidup", 84, 37, 5, "Poor", "High", "Worsening", "Investigate pollution source. Enforce environmental regulations. Deploy water treatment."),
        ("Limbah Ilegal", "Waste Management", "Jl. Industri, Tangerang", "Tangerang", -6.1900, 106.6200, "Dinas Lingkungan Hidup", 92, 48, 6, "Poor", "High", "Worsening", "CRITICAL: Investigate illegal dumping. Coordinate with law enforcement. Secure area."),

        # ── Traffic (Dinas Perhubungan) ──
        ("Kemacetan Parah", "Traffic", "Simpang Tol Bekasi Barat", "Bekasi", -6.2280, 106.9680, "Dinas Perhubungan", 76, 30, 4, "Fair", "Medium", "Stable", "Optimize traffic light timing. Deploy traffic officers during peak hours."),
        ("Peralatan Lalu Lintas Rusak", "Traffic", "Jl. Jenderal Sudirman, Jakarta Pusat", "Jakarta Pusat", -6.2050, 106.8200, "Dinas Perhubungan", 67, 23, 3, "Fair", "Medium", "Stable", "Replace damaged traffic equipment. Schedule maintenance check."),
        ("Lampu LaluLinta Mati", "Traffic", "Intersection Jl. Ahmad Yani, Bekasi", "Bekasi", -6.2340, 106.9770, "Dinas Perhubungan", 81, 35, 4, "Poor", "High", "Worsening", "Emergency repair of traffic light system. Deploy manual traffic control."),
        ("Marka Jalan Hilang", "Traffic", "Jl. Raya Cikarang, Bekasi", "Bekasi", -6.3550, 107.1450, "Dinas Perhubungan", 42, 14, 2, "Fair", "Low", "Stable", "Repaint road markings. Include in next scheduled road maintenance."),
        ("Trotoar Digunakan Parkir Liar", "Traffic", "Jl. Mangga Dua, Jakarta Utara", "Jakarta Utara", -6.1450, 106.8300, "Dinas Perhubungan", 58, 20, 3, "Fair", "Medium", "Stable", "Increase enforcement patrols. Install parking barriers and signage."),
        ("Rambu Rusak/Tidak Terlihat", "Traffic", "Jl. Raya Bogor, Depok", "Depok", -6.3950, 106.8050, "Dinas Perhubungan", 55, 19, 2, "Fair", "Medium", "Stable", "Replace damaged signage. Improve visibility with reflective materials."),

        # ── Street Lighting (Dinas PUPR) ──
        ("Lampu Jalan Mati Total", "Street Lighting", "Jl. Kemang Pratama, Bekasi", "Bekasi", -6.2260, 106.9920, "Dinas PUPR", 70, 26, 3, "Poor", "Medium", "Stable", "Replace non-functional lamp units. Check electrical connections."),
        ("Lampu Penerangan Redup", "Street Lighting", "Jl. Raya Cileungsi, Bogor", "Bogor", -6.5750, 106.8550, "Dinas PUPR", 45, 15, 2, "Fair", "Low", "Stable", "Clean lamp fixtures and replace aging bulbs."),
        ("Tiang Lampu Miring", "Street Lighting", "Jl. Pahlawan, Depok", "Depok", -6.4120, 106.7980, "Dinas PUPR", 62, 21, 3, "Poor", "Medium", "Stable", "Straighten and reinforce lamp post. Check foundation stability."),
        ("Lampu LED Berkedip", "Street Lighting", "Jl. Sudirman, Tangerang Selatan", "Tangerang Selatan", -6.3050, 106.7200, "Dinas PUPR", 38, 13, 2, "Fair", "Low", "Stable", "Replace faulty LED driver. Schedule electrical inspection."),
        ("Penerangan Tidak Merata", "Street Lighting", "Jl. Raya Bekasi, Bekasi Timur", "Bekasi", -6.2320, 107.0150, "Dinas PUPR", 51, 17, 2, "Fair", "Medium", "Stable", "Install additional lamp units in dark spots. Review lighting layout plan."),

        # ── Public Facilities (Dinas PUPR) ──
        ("Halte Bus Rusak", "Public Facilities", "Halte Bus Jl. Sudirman, Jakarta Pusat", "Jakarta Pusat", -6.2080, 106.8220, "Dinas PUPR", 75, 30, 4, "Poor", "Medium", "Worsening", "Repair shelter structure and seating. Ensure accessibility compliance."),
        ("Taman Kota Terbengkalai", "Public Facilities", "Taman Alun-alun, Bekasi", "Bekasi", -6.2370, 106.9940, "Dinas PUPR", 48, 16, 2, "Fair", "Low", "Stable", "Resume park maintenance. Repair damaged facilities and replant greenery."),
        ("Toilet Publik Tidak Layak", "Public Facilities", "Terminal Pasar Senen, Jakarta Pusat", "Jakarta Pusat", -6.1750, 106.8400, "Dinas PUPR", 65, 22, 3, "Poor", "Medium", "Stable", "Deep clean and repair plumbing. Install proper ventilation."),
        ("Playground Rusak", "Public Facilities", "Taman Mini Indonesia Indah, Jakarta Timur", "Jakarta Timur", -6.3000, 106.8900, "Dinas PUPR", 56, 19, 2, "Fair", "Medium", "Stable", "Replace damaged playground equipment. Conduct safety inspection."),
        ("Mushola Tidak Terawat", "Public Facilities", "Rest Area Tol Cikampek, Bekasi", "Bekasi", -6.4000, 107.1000, "Dinas PUPR", 44, 15, 2, "Fair", "Low", "Stable", "Clean and repair prayer room. Ensure water supply and sanitation."),

        # ── Drainage (Dinas PUPR) ──
        ("Saluran Drainase Tersumbat", "Drainage", "Jl. Jatibening, Bekasi", "Bekasi", -6.2450, 106.9500, "Dinas PUPR", 87, 40, 5, "Poor", "High", "Worsening", "Emergency drainage clearing. Remove blockage and desludge channel."),
        ("Got Overflow", "Drainage", "Jl. Kemang Selatan, Jakarta Selatan", "Jakarta Selatan", -6.2620, 106.8130, "Dinas PUPR", 73, 28, 4, "Poor", "Medium", "Worsening", "Expand drainage capacity. Clear upstream blockages."),
        ("Saluran Tertutup Bangunan Liar", "Drainage", "Jl. Raya Bogor, Jakarta Timur", "Jakarta Timur", -6.2150, 106.8750, "Dinas PUPR", 80, 33, 4, "Poor", "High", "Worsening", "Coordinate with Satpol PP for illegal structure removal. Restore drainage channel."),
        ("Drainase Tidak Terhubung", "Drainage", "Perumahan Harapan Baru, Bekasi Utara", "Bekasi", -6.2100, 106.9800, "Dinas PUPR", 64, 23, 3, "Fair", "Medium", "Stable", "Connect disconnected drainage sections. Engineer proper flow path."),
        ("Ukuran Drainase Tidak Cukup", "Drainage", "Jl. Alternatif Cibubur, Depok", "Depok", -6.3800, 106.8200, "Dinas PUPR", 72, 27, 3, "Poor", "Medium", "Stable", "Widen drainage channel to handle increased water volume from development."),
        ("Lubang Got Terbuka", "Drainage", "Jl. Masjid Al-Azhar, Jakarta Selatan", "Jakarta Selatan", -6.2580, 106.8080, "Dinas PUPR", 78, 32, 4, "Poor", "High", "Worsening", "Install safety grating immediately. Repair damaged drain covers."),

        # ── Environmental Issues (Dinas Lingkungan Hidup) ──
        ("Pencemaran Udara dari Pabrik", "Environmental Issues", "Kawasan Industri MM2100, Bekasi", "Bekasi", -6.3300, 107.1600, "Dinas Lingkungan Hidup", 89, 42, 5, "Poor", "High", "Worsening", "Conduct air quality monitoring. Investigate factory emissions compliance."),
        ("Pohon Tumbang", "Environmental Issues", "Jl. Rasuna Said, Jakarta Selatan", "Jakarta Selatan", -6.2500, 106.8300, "Dinas Lingkungan Hidup", 71, 26, 3, "Fair", "Medium", "Stable", "Remove fallen tree. Inspect surrounding trees for stability."),
        ("Tanah Longsor", "Environmental Issues", "Jl. Raya Puncak, Bogor", "Bogor", -6.6500, 106.9000, "Dinas Lingkungan Hidup", 93, 46, 6, "Poor", "High", "Worsening", "CRITICAL: Evacuate area. Deploy emergency stabilization and drainage."),
    ]

    # Calculate risk scores, severities, statuses, and dates
    statuses_pool = ['Active', 'Active', 'Active', 'In Progress', 'In Progress', 'Resolved', 'Monitoring']

    for i, issue in enumerate(issues_raw):
        title, cat, loc, city, lat, lng, dept, score, complaints, history, asset, impact, trend, rec = issue
        sev = severity_from_score(score)
        days_ago = random.randint(1, 45)
        reported = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        status = random.choice(statuses_pool)
        if score >= 80:
            status = random.choice(['Active', 'Active', 'In Progress'])
        elif score < 30:
            status = random.choice(['Resolved', 'Monitoring', 'In Progress'])

        desc = f"Laporan mengenai {title.lower()} di {loc}. "
        desc += f"Sudah ada {complaints} pengaduan dari warga sekitar. "
        desc += f"Terdapat {history} insiden serupa di lokasi ini selama 2 tahun terakhir. "
        desc += f"Kondisi aset: {asset}. Dampak terhadap publik: {impact}."

        c.execute('''INSERT INTO issues 
            (title, category, location_name, city, lat, lng, department, risk_score, severity,
             status, reported_date, description, predicted_trend, recommendation,
             complaint_count, historical_incidents, asset_condition, public_impact)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (title, cat, loc, city, lat, lng, dept, score, sev, status, reported,
             desc, trend, rec, complaints, history, asset, impact))

    # ── Activities ─────────────────────────────────────────────────
    activity_templates = [
        ("risk_change", "Risk score updated for {title}", "Risk score changed from {old} to {new} based on new complaint data."),
        ("new_complaint", "New complaint received for {title}", "Citizen complaint filed regarding conditions at {location}."),
        ("status_change", "Status updated for {title}", "Issue status changed to {status} by {dept}."),
        ("prediction", "AI prediction generated for {title}", "System predicted {trend} trend with {confidence}% confidence."),
        ("recommendation", "Recommendation issued for {title}", "AI recommends: {action}"),
        ("alert", "Alert: {title}", "Risk level escalated to {severity} due to increasing complaints."),
    ]

    now = datetime(2026, 8, 16, 8, 0, 0)
    for i in range(40):
        issue_id = random.randint(1, 50)
        tmpl = random.choice(activity_templates)
        act_type = tmpl[0]
        hours_ago = random.randint(0, 72)
        ts = (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')

        c.execute("INSERT INTO activities (type, title, description, issue_id, timestamp) VALUES (?,?,?,?,?)",
                  (act_type, f"Activity for issue #{issue_id}", f"System activity logged for tracking purposes.", issue_id, ts))

    # ── Data Sources ───────────────────────────────────────────────
    data_sources = [
        ("Public Complaints", "Integrated public complaint reports from citizens via 119, online portal, and mobile app", "Connected", "2026-08-16 08:00:00", 12847, "fa-comments"),
        ("Infrastructure Records", "Government infrastructure and asset database maintained by Dinas PUPR", "Connected", "2026-08-16 06:00:00", 8234, "fa-road"),
        ("Historical Incidents", "Archive of past incidents, resolutions, and maintenance records", "Connected", "2026-08-15 23:00:00", 34521, "fa-history"),
        ("Asset Data", "Government asset inventory including roads, bridges, and public facilities", "Processing", "2026-08-16 07:30:00", 5672, "fa-database"),
        ("Location & Mapping Data", "Geographic information system and infrastructure mapping data", "Connected", "2026-08-16 05:00:00", 91023, "fa-map"),
        ("Weather & Climate Data", "Weather patterns, rainfall data, and climate risk indicators", "Needs Attention", "2026-08-14 12:00:00", 2341, "fa-cloud-sun"),
        ("Traffic Flow Data", "Real-time and historical traffic congestion data from sensors", "Connected", "2026-08-16 08:15:00", 45230, "fa-car"),
        ("Environmental Sensors", "Air quality, water level, and environmental monitoring sensors", "Processing", "2026-08-16 07:45:00", 7891, "fa-leaf"),
    ]
    c.executemany("INSERT INTO data_sources (name, description, status, last_updated, records_count, icon) VALUES (?,?,?,?,?,?)", data_sources)

    conn.commit()
    conn.close()

    # Print summary
    conn2 = get_db()
    counts = {}
    for table in ['users', 'issues', 'activities', 'data_sources']:
        counts[table] = conn2.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn2.close()

    print(f"✅ Database initialized at {DB_PATH}")
    print(f"   Users: {counts['users']}")
    print(f"   Issues: {counts['issues']}")
    print(f"   Activities: {counts['activities']}")
    print(f"   Data Sources: {counts['data_sources']}")

    # Show severity distribution
    conn3 = get_db()
    for sev in ['Critical', 'High', 'Medium', 'Low']:
        cnt = conn3.execute("SELECT COUNT(*) FROM issues WHERE severity=?", (sev,)).fetchone()[0]
        print(f"   {sev}: {cnt} issues")
    conn3.close()


if __name__ == '__main__':
    init_db()
