from flask import Blueprint, Response

rss_bp = Blueprint('rss', __name__)

@rss_bp.route('/rss', methods=['GET'])
def get_rss_feed():
    """返回 podcast RSS feed"""
    rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Heario AI News</title>
            <description>AI-powered news summaries</description>
            <link>http://localhost:5000</link>
        </channel>
    </rss>"""
    
    return Response(rss_xml, mimetype='application/rss+xml')