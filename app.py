"""
CIVIC-PREDICT AI - Government Predictive Analytics Platform
Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from functools import wraps
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.context_processor
def inject_globals():
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        greeting = 'morning'
    elif hour < 17:
        greeting = 'afternoon'
    else:
        greeting = 'evening'
    return dict(greeting=greeting, current_year=datetime.now().year)


# ── Database helpers ───────────────────────────────────────────────

def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── Auth decorator ─────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ── Public routes ──────────────────────────────────────────────────

@app.route('/')
def landing():
    """Landing page - no auth required."""
    return render_template('landing.html', current_user=session.get('name'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page — demo mode: click a role to sign in (no password)."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            session['department'] = user['department']
            return redirect(url_for('dashboard'))
        else:
            error = 'User not found.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for('login'))


# ── Dashboard ──────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with summary metrics and charts."""
    db = get_db()

    # Total issues
    total_issues = db.execute('SELECT COUNT(*) FROM issues').fetchone()[0]

    # Severity counts
    critical_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'Critical'").fetchone()[0]
    high_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'High'").fetchone()[0]
    medium_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'Medium'").fetchone()[0]
    low_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'Low'").fetchone()[0]

    # Predicted worsening count
    predicted_count = db.execute(
        "SELECT COUNT(*) FROM issues WHERE predicted_trend = 'Worsening'"
    ).fetchone()[0]

    # Resolved count
    resolved_count = db.execute(
        "SELECT COUNT(*) FROM issues WHERE status = 'Resolved'"
    ).fetchone()[0]

    # Average response time (hardcoded)
    avg_response_time = '4.2 hrs'

    # Priority issues - top 10 by risk_score
    priority_issues = db.execute(
        'SELECT * FROM issues ORDER BY risk_score DESC LIMIT 10'
    ).fetchall()

    # Recent activities - last 20
    activities = db.execute(
        '''SELECT a.*, i.title as issue_title
           FROM activities a
           LEFT JOIN issues i ON a.issue_id = i.id
           ORDER BY a.timestamp DESC LIMIT 20'''
    ).fetchall()

    # Risk distribution dict for chart
    risk_distribution = {
        'Critical': critical_count,
        'High': high_count,
        'Medium': medium_count,
        'Low': low_count
    }

    # Risk trend data - monthly data for chart
    risk_trend_data = db.execute(
        '''SELECT strftime('%Y-%m', reported_date) as month,
                  COUNT(*) as count,
                  AVG(risk_score) as avg_score
           FROM issues
           GROUP BY month
           ORDER BY month'''
    ).fetchall()

    # Category counts for chart
    cat_counts = db.execute(
        'SELECT category, COUNT(*) as cnt FROM issues GROUP BY category ORDER BY cnt DESC'
    ).fetchall()
    category_labels = [c['category'] for c in cat_counts]
    category_data = [c['cnt'] for c in cat_counts]

    db.close()

    return render_template('dashboard.html',
                           category_labels=category_labels,
                           category_data=category_data,
                           total_issues=total_issues,
                           critical_count=critical_count,
                           high_count=high_count,
                           medium_count=medium_count,
                           low_count=low_count,
                           predicted_count=predicted_count,
                           avg_response_time=avg_response_time,
                           resolved_count=resolved_count,
                           priority_issues=priority_issues,
                           activities=activities,
                           risk_distribution=risk_distribution,
                           risk_trend_data=risk_trend_data)


# ── Risk Map ───────────────────────────────────────────────────────

@app.route('/risk-map')
@login_required
def risk_map():
    """Risk map page showing all issues on a map."""
    db = get_db()
    issues = db.execute(
        'SELECT id, title, category, location_name, city, lat, lng, risk_score, severity, status, predicted_trend '
        'FROM issues'
    ).fetchall()
    import json
    issues_list = []
    for issue in issues:
        issues_list.append({
            'id': issue['id'], 'title': issue['title'], 'category': issue['category'],
            'location_name': issue['location_name'], 'city': issue['city'],
            'lat': issue['lat'], 'lng': issue['lng'], 'risk_score': issue['risk_score'],
            'severity': issue['severity'], 'status': issue['status']
        })

    cities = db.execute('SELECT DISTINCT city FROM issues ORDER BY city').fetchall()
    cats = db.execute('SELECT DISTINCT category FROM issues ORDER BY category').fetchall()
    stats = db.execute('SELECT DISTINCT status FROM issues ORDER BY status').fetchall()
    db.close()
    return render_template('risk_map.html',
                           issues=issues,
                           issues_json=json.dumps(issues_list),
                           categories=[c['category'] for c in cats],
                           cities=[c['city'] for c in cities],
                           statuses=[s['status'] for s in stats])


# ── Issues ─────────────────────────────────────────────────────────

@app.route('/issues')
@login_required
def issues():
    """Issues list with filtering."""
    db = get_db()

    # Get filter values from query params
    category_filter = request.args.get('category', '')
    department_filter = request.args.get('department', '')
    status_filter = request.args.get('status', '')

    # Build query with optional filters
    query = 'SELECT * FROM issues WHERE 1=1'
    params = []

    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    if department_filter:
        query += ' AND department = ?'
        params.append(department_filter)
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)

    query += ' ORDER BY risk_score DESC'
    all_issues = db.execute(query, params).fetchall()

    # Get distinct values for filter dropdowns
    categories = db.execute('SELECT DISTINCT category FROM issues ORDER BY category').fetchall()
    departments = db.execute('SELECT DISTINCT department FROM issues ORDER BY department').fetchall()
    statuses = db.execute('SELECT DISTINCT status FROM issues ORDER BY status').fetchall()

    db.close()

    return render_template('issues.html',
                           issues=all_issues,
                           categories=[c['category'] for c in categories],
                           departments=[d['department'] for d in departments],
                           statuses=[s['status'] for s in statuses],
                           selected_category=category_filter,
                           selected_department=department_filter,
                           selected_status=status_filter)


@app.route('/issues/<int:issue_id>')
@login_required
def issue_detail(issue_id):
    """Issue detail page with related activities."""
    db = get_db()

    issue = db.execute('SELECT * FROM issues WHERE id = ?', (issue_id,)).fetchone()
    if not issue:
        db.close()
        return redirect(url_for('issues'))

    activities = db.execute(
        'SELECT * FROM activities WHERE issue_id = ? ORDER BY timestamp DESC',
        (issue_id,)
    ).fetchall()

    db.close()

    return render_template('issue_detail.html', issue=issue, activities=activities)


# ── Predictions ────────────────────────────────────────────────────

@app.route('/predictions')
@login_required
def predictions():
    """Predictions page - issues grouped by predicted trend."""
    db = get_db()

    worsening = db.execute(
        "SELECT * FROM issues WHERE predicted_trend = 'Worsening' ORDER BY risk_score DESC"
    ).fetchall()

    stable = db.execute(
        "SELECT * FROM issues WHERE predicted_trend = 'Stable' ORDER BY risk_score DESC"
    ).fetchall()

    improving = db.execute(
        "SELECT * FROM issues WHERE predicted_trend = 'Improving' ORDER BY risk_score DESC"
    ).fetchall()

    db.close()

    predictions = {
        'Worsening': worsening,
        'Stable': stable,
        'Improving': improving
    }

    return render_template('predictions.html', predictions=predictions)


# ── Recommendations ────────────────────────────────────────────────

@app.route('/recommendations')
@login_required
def recommendations():
    """Recommendations page - all active issues sorted by risk score."""
    db = get_db()
    issues = db.execute(
        "SELECT * FROM issues WHERE status != 'Resolved' ORDER BY risk_score DESC"
    ).fetchall()
    db.close()
    return render_template('recommendations.html', recommendations=issues)


# ── AI Assistant ───────────────────────────────────────────────────

@app.route('/ai-assistant')
@login_required
def ai_assistant():
    """AI Assistant chat page."""
    return render_template('ai_assistant.html')


@app.route('/api/ai-chat', methods=['POST'])
@login_required
def api_ai_chat():
    """AI Chat API endpoint - keyword-based responses about the data."""
    data = request.get_json()
    user_message = data.get('message', '').lower().strip() if data else ''

    db = get_db()

    response = generate_ai_response(user_message, db)

    db.close()

    return jsonify({'response': response})


def generate_ai_response(message, db):
    """Simple keyword-matching AI assistant that answers questions about the data."""

    # Greeting
    if any(word in message for word in ['hello', 'hi', 'hey', 'halo', 'hai']):
        return ("Hello! I'm CivicPredict AI Assistant. I can help you understand "
                "our civic infrastructure data. Try asking about issues, predictions, "
                "risk scores, or department performance.")

    # Total issues
    if any(word in message for word in ['total issue', 'how many issue', 'jumlah issue', 'how many problem']):
        count = db.execute('SELECT COUNT(*) FROM issues').fetchone()[0]
        return f"There are currently {count} total issues tracked in the system."

    # Critical issues
    if any(word in message for word in ['critical', 'kritis', 'severe', 'darurat']):
        critical = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'Critical'").fetchone()[0]
        high = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'High'").fetchone()[0]
        return (f"There are {critical} Critical and {high} High severity issues. "
                f"Critical issues require immediate attention. "
                f"I recommend prioritizing these for rapid response.")

    # Worsening predictions
    if any(word in message for word in ['worsening', 'getting worse', 'memburuk', 'prediksi']):
        worsening = db.execute(
            "SELECT COUNT(*) FROM issues WHERE predicted_trend = 'Worsening'"
        ).fetchone()[0]
        examples = db.execute(
            "SELECT title, risk_score FROM issues WHERE predicted_trend = 'Worsening' "
            "ORDER BY risk_score DESC LIMIT 5"
        ).fetchall()
        result = f"There are {worsening} issues predicted to worsen. Top concerns:\n"
        for ex in examples:
            result += f"• {ex['title']} (Risk: {ex['risk_score']})\n"
        return result

    # Improving predictions
    if any(word in message for word in ['improving', 'getting better', 'membaik']):
        improving = db.execute(
            "SELECT COUNT(*) FROM issues WHERE predicted_trend = 'Improving'"
        ).fetchone()[0]
        return f"There are {improving} issues predicted to improve over time."

    # By department
    if any(word in message for word in ['department', 'dinas', 'perangkat daerah']):
        depts = db.execute(
            'SELECT department, COUNT(*) as cnt, AVG(risk_score) as avg_score '
            'FROM issues GROUP BY department ORDER BY avg_score DESC'
        ).fetchall()
        result = "Issues by department:\n"
        for d in depts:
            result += f"• {d['department']}: {d['cnt']} issues (Avg Risk: {d['avg_score']:.0f})\n"
        return result

    # By category
    if any(word in message for word in ['category', 'kategori', 'jenis']):
        cats = db.execute(
            'SELECT category, COUNT(*) as cnt, AVG(risk_score) as avg_score '
            'FROM issues GROUP BY category ORDER BY avg_score DESC'
        ).fetchall()
        result = "Issues by category:\n"
        for c in cats:
            result += f"• {c['category']}: {c['cnt']} issues (Avg Risk: {c['avg_score']:.0f})\n"
        return result

    # Average risk (checked before generic risk to avoid "average risk" matching wrong branch)
    if any(word in message for word in ['average', 'avg', 'rata-rata']):
        avg = db.execute('SELECT AVG(risk_score) FROM issues').fetchone()[0]
        return f"The average risk score across all issues is {avg:.1f} out of 100."

    # Risk score / top risks
    if any(word in message for word in ['risk', 'risiko', 'top issue', 'highest risk', 'tertinggi']):
        top = db.execute(
            'SELECT title, risk_score, severity, department FROM issues '
            'ORDER BY risk_score DESC LIMIT 5'
        ).fetchall()
        result = "Top 5 highest risk issues:\n"
        for t in top:
            result += f"• {t['title']} - Risk Score: {t['risk_score']} ({t['severity']}) - {t['department']}\n"
        return result

    # Flooding
    if any(word in message for word in ['flood', 'banjir', 'flooding']):
        count = db.execute("SELECT COUNT(*) FROM issues WHERE category = 'Flooding'").fetchone()[0]
        avg_risk = db.execute(
            "SELECT AVG(risk_score) FROM issues WHERE category = 'Flooding'"
        ).fetchone()[0]
        worsening = db.execute(
            "SELECT COUNT(*) FROM issues WHERE category = 'Flooding' AND predicted_trend = 'Worsening'"
        ).fetchone()[0]
        return (f"There are {count} flooding issues with an average risk score of {avg_risk:.0f}. "
                f"{worsening} of these are predicted to worsen. "
                f"Flooding is a critical concern requiring coordinated response.")

    # Road / traffic
    if any(word in message for word in ['road', 'jalan', 'traffic', 'lalu lintas']):
        road_count = db.execute("SELECT COUNT(*) FROM issues WHERE category = 'Road Infrastructure'").fetchone()[0]
        traffic_count = db.execute("SELECT COUNT(*) FROM issues WHERE category = 'Traffic'").fetchone()[0]
        return (f"There are {road_count} road infrastructure issues and "
                f"{traffic_count} traffic issues being tracked.")

    # Waste / environmental
    if any(word in message for word in ['waste', 'sampah', 'environment', 'lingkungan']):
        waste = db.execute("SELECT COUNT(*) FROM issues WHERE category = 'Waste Management'").fetchone()[0]
        env = db.execute("SELECT COUNT(*) FROM issues WHERE category = 'Environmental Issues'").fetchone()[0]
        return (f"There are {waste} waste management issues and {env} environmental issues. "
                f"Both categories show increasing trends in recent months.")

    # Resolved
    if any(word in message for word in ['resolved', 'selesai', 'done', 'completed']):
        resolved = db.execute("SELECT COUNT(*) FROM issues WHERE status = 'Resolved'").fetchone()[0]
        total = db.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
        pct = (resolved / total * 100) if total > 0 else 0
        return (f"{resolved} out of {total} issues have been resolved ({pct:.1f}%). "
                f"{'Good progress!' if pct > 20 else 'More effort is needed to resolve pending issues.'}")

    # Data sources
    if any(word in message for word in ['data source', 'sumber data', 'data sources']):
        sources = db.execute('SELECT name, status, records_count FROM data_sources').fetchall()
        result = "Data sources status:\n"
        for s in sources:
            result += f"• {s['name']}: {s['status']} ({s['records_count']:,} records)\n"
        return result

    # Help
    if any(word in message for word in ['help', 'bantuan', 'what can you do']):
        return ("I can answer questions about:\n"
                "• Total issues in the system\n"
                "• Critical and high-severity issues\n"
                "• Predictions (worsening/improving trends)\n"
                "• Issues by department or category\n"
                "• Top risk issues\n"
                "• Flooding, road, traffic, waste, and environmental data\n"
                "• Resolution statistics\n"
                "• Data source status\n\n"
                "Try asking something like: 'How many critical issues are there?'")

    # Default response
    return ("I'm not sure I understand that question. Try asking about:\n"
            "• Issues, predictions, or risk scores\n"
            "• Department or category breakdown\n"
            "• Flooding, roads, or traffic data\n"
            "• Type 'help' to see what I can do.")


# ── Analytics ──────────────────────────────────────────────────────

@app.route('/analytics')
@login_required
def analytics():
    """Analytics page with detailed statistics and charts."""
    db = get_db()

    # Category counts
    category_counts = db.execute(
        'SELECT category, COUNT(*) as count FROM issues GROUP BY category ORDER BY count DESC'
    ).fetchall()

    # Department counts
    department_counts = db.execute(
        'SELECT department, COUNT(*) as count, AVG(risk_score) as avg_risk '
        'FROM issues GROUP BY department ORDER BY count DESC'
    ).fetchall()

    # City counts
    city_counts = db.execute(
        'SELECT city, COUNT(*) as count FROM issues GROUP BY city ORDER BY count DESC'
    ).fetchall()

    # Status counts
    status_counts = db.execute(
        'SELECT status, COUNT(*) as count FROM issues GROUP BY status ORDER BY count DESC'
    ).fetchall()

    # Monthly trend
    monthly_trend = db.execute(
        '''SELECT strftime('%Y-%m', reported_date) as month,
                  COUNT(*) as count,
                  AVG(risk_score) as avg_risk
           FROM issues
           GROUP BY month
           ORDER BY month'''
    ).fetchall()

    # Severity distribution
    severity_distribution = db.execute(
        'SELECT severity, COUNT(*) as count FROM issues GROUP BY severity'
    ).fetchall()

    cat_labels = [r['category'] for r in category_counts]
    cat_data = [r['count'] for r in category_counts]
    dept_labels = [r['department'] for r in department_counts]
    dept_data = [r['count'] for r in department_counts]
    city_labels = [r['city'] for r in city_counts]
    city_data = [r['count'] for r in city_counts]
    status_labels = [r['status'] for r in status_counts]
    status_data = [r['count'] for r in status_counts]
    sev_map = {r['severity']: r['count'] for r in severity_distribution}
    sev_data = [sev_map.get('Critical', 0), sev_map.get('High', 0), sev_map.get('Medium', 0), sev_map.get('Low', 0)]
    total_issues = sum(cat_data)
    resolved_count = db.execute("SELECT COUNT(*) FROM issues WHERE status='Resolved'").fetchone()[0]
    cat_summary = []
    for r in category_counts:
        cat_row = db.execute(
            'SELECT COUNT(*) as c, AVG(risk_score) as avg_s FROM issues WHERE category=?', (r['category'],)
        ).fetchone()
        crit = db.execute("SELECT COUNT(*) FROM issues WHERE category=? AND severity='Critical'", (r['category'],)).fetchone()[0]
        hi = db.execute("SELECT COUNT(*) FROM issues WHERE category=? AND severity='High'", (r['category'],)).fetchone()[0]
        worsening = db.execute("SELECT COUNT(*) FROM issues WHERE category=? AND predicted_trend='Worsening'", (r['category'],)).fetchone()[0]
        cat_summary.append({'category': r['category'], 'total': r['count'], 'critical': crit, 'high': hi, 'avg_score': cat_row['avg_s'], 'worsening': worsening})

    db.close()

    return render_template('analytics.html',
                           category_labels=cat_labels, category_data=cat_data,
                           department_labels=dept_labels, department_data=dept_data,
                           city_labels=city_labels, city_data=city_data,
                           status_labels=status_labels, status_data=status_data,
                           severity_data=sev_data,
                           total_issues=total_issues, resolved_count=resolved_count,
                           category_summary=cat_summary)


# ── Data Sources ───────────────────────────────────────────────────

@app.route('/data-sources')
@login_required
def data_sources():
    """Data sources page showing all connected data feeds."""
    db = get_db()
    sources = db.execute('SELECT * FROM data_sources ORDER BY name').fetchall()
    db.close()
    return render_template('data_sources.html', data_sources=sources)


# ── Reports ────────────────────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    """Reports page with summary data for report generation."""
    db = get_db()

    total_issues = db.execute('SELECT COUNT(*) FROM issues').fetchone()[0]
    active_issues = db.execute("SELECT COUNT(*) FROM issues WHERE status = 'Active'").fetchone()[0]
    resolved_issues = db.execute("SELECT COUNT(*) FROM issues WHERE status = 'Resolved'").fetchone()[0]
    critical_issues = db.execute("SELECT COUNT(*) FROM issues WHERE severity = 'Critical'").fetchone()[0]
    avg_risk = db.execute('SELECT AVG(risk_score) FROM issues').fetchone()[0]
    total_complaints = db.execute('SELECT SUM(complaint_count) FROM issues').fetchone()[0]
    high_risk_count = db.execute(
        "SELECT COUNT(*) FROM issues WHERE risk_score >= 75"
    ).fetchone()[0]

    category_breakdown = db.execute(
        'SELECT category, COUNT(*) as count, AVG(risk_score) as avg_risk, '
        'SUM(complaint_count) as total_complaints '
        'FROM issues GROUP BY category ORDER BY count DESC'
    ).fetchall()

    department_breakdown = db.execute(
        'SELECT department, COUNT(*) as count, AVG(risk_score) as avg_risk '
        'FROM issues GROUP BY department ORDER BY avg_risk DESC'
    ).fetchall()

    top_risks = db.execute(
        'SELECT * FROM issues ORDER BY risk_score DESC LIMIT 10'
    ).fetchall()

    from datetime import datetime
    report_date = datetime.now().strftime('%B %d, %Y')
    critical_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity='Critical'").fetchone()[0]
    high_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity='High'").fetchone()[0]
    medium_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity='Medium'").fetchone()[0]
    low_count = db.execute("SELECT COUNT(*) FROM issues WHERE severity='Low'").fetchone()[0]

    db.close()

    return render_template('reports.html',
                           total_issues=total_issues,
                           active_issues=active_issues,
                           resolved_issues=resolved_issues,
                           critical_issues=critical_issues,
                           avg_risk=avg_risk,
                           total_complaints=total_complaints,
                           high_risk_count=high_risk_count,
                           category_breakdown=category_breakdown,
                           department_breakdown=department_breakdown,
                           top_risks=top_risks,
                           critical_count=critical_count,
                           high_count=high_count,
                           medium_count=medium_count,
                           low_count=low_count,
                           report_date=report_date)


# ── Settings ───────────────────────────────────────────────────────

@app.route('/settings')
@login_required
def settings():
    """Settings page showing current user info and preferences."""
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    db.close()
    return render_template('settings.html', user=user)


# ── JSON API Endpoints ─────────────────────────────────────────────

@app.route('/api/dashboard-data')
@login_required
def api_dashboard_data():
    """JSON API for dashboard chart data."""
    db = get_db()

    # Risk distribution
    risk_dist = {}
    for row in db.execute('SELECT severity, COUNT(*) as count FROM issues GROUP BY severity'):
        risk_dist[row['severity']] = row['count']

    # Category distribution
    cat_dist = {}
    for row in db.execute('SELECT category, COUNT(*) as count FROM issues GROUP BY category'):
        cat_dist[row['category']] = row['count']

    # Monthly trend
    monthly = []
    for row in db.execute(
        '''SELECT strftime('%Y-%m', reported_date) as month,
                  COUNT(*) as count, AVG(risk_score) as avg_risk
           FROM issues GROUP BY month ORDER BY month'''
    ):
        monthly.append({
            'month': row['month'],
            'count': row['count'],
            'avg_risk': round(row['avg_risk'], 1)
        })

    # Trend distribution
    trend_dist = {}
    for row in db.execute('SELECT predicted_trend, COUNT(*) as count FROM issues GROUP BY predicted_trend'):
        trend_dist[row['predicted_trend']] = row['count']

    # Department stats
    dept_stats = []
    for row in db.execute(
        'SELECT department, COUNT(*) as count, AVG(risk_score) as avg_risk '
        'FROM issues GROUP BY department'
    ):
        dept_stats.append({
            'department': row['department'],
            'count': row['count'],
            'avg_risk': round(row['avg_risk'], 1)
        })

    db.close()

    return jsonify({
        'risk_distribution': risk_dist,
        'category_distribution': cat_dist,
        'monthly_trend': monthly,
        'trend_distribution': trend_dist,
        'department_stats': dept_stats
    })


@app.route('/api/issues-data')
@login_required
def api_issues_data():
    """JSON API for map data - all issues with location info."""
    db = get_db()
    issues = db.execute(
        'SELECT id, title, category, location_name, city, lat, lng, '
        'risk_score, severity, status, predicted_trend, department, '
        'complaint_count, public_impact '
        'FROM issues'
    ).fetchall()
    db.close()

    result = []
    for issue in issues:
        result.append({
            'id': issue['id'],
            'title': issue['title'],
            'category': issue['category'],
            'location_name': issue['location_name'],
            'city': issue['city'],
            'lat': issue['lat'],
            'lng': issue['lng'],
            'risk_score': issue['risk_score'],
            'severity': issue['severity'],
            'status': issue['status'],
            'predicted_trend': issue['predicted_trend'],
            'department': issue['department'],
            'complaint_count': issue['complaint_count'],
            'public_impact': issue['public_impact']
        })

    return jsonify({'issues': result})


# ── Auto-init database if missing (fresh deploy on Render) ──────────
import os as _os
if not _os.path.exists(config.DATABASE):
    from init_db import init_db
    init_db()

# ── Run ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(_os.environ.get('PORT', 5000))
    app.run(debug=config.DEBUG, host='0.0.0.0', port=port)
