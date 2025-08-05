"""
Performance Monitoring Middleware for Heario Backend

This middleware automatically tracks and logs performance metrics for all API endpoints.
"""

import time
import logging
import json
from datetime import datetime
from flask import request, g
from functools import wraps
from typing import Dict, Any, List
import threading
import os

class PerformanceMiddleware:
    def __init__(self, app=None, log_file: str = None):
        self.app = app
        self.log_file = log_file or '/Users/cyril/Documents/git/heario/backend/api_performance.log'
        self.metrics_storage = []
        self.metrics_lock = threading.Lock()
        
        # Setup performance logger
        self.logger = logging.getLogger('api_performance')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        self.app = app
        
        @app.before_request
        def before_request():
            g.start_time = time.time()
            g.request_id = f"{int(time.time() * 1000)}_{id(request)}"
        
        @app.after_request
        def after_request(response):
            self.log_request_performance(response)
            return response
        
        # Add performance dashboard endpoint
        @app.route('/api/performance/dashboard', methods=['GET'])
        def performance_dashboard():
            return self.get_performance_dashboard()
        
        @app.route('/api/performance/metrics', methods=['GET'])
        def performance_metrics():
            return self.get_recent_metrics()
    
    def log_request_performance(self, response):
        """Log performance metrics for the current request"""
        if not hasattr(g, 'start_time'):
            return
        
        end_time = time.time()
        duration = end_time - g.start_time
        
        # Extract request information
        endpoint = request.endpoint or 'unknown'
        method = request.method
        path = request.path
        status_code = response.status_code
        
        # Get request size
        request_size = 0
        if request.content_length:
            request_size = request.content_length
        elif hasattr(request, 'data') and request.data:
            request_size = len(request.data)
        
        # Get response size
        response_size = 0
        if response.content_length:
            response_size = response.content_length
        elif hasattr(response, 'data') and response.data:
            response_size = len(response.data)
        
        # Create performance metric
        metric = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration': duration,
            'request_size': request_size,
            'response_size': response_size,
            'user_agent': request.headers.get('User-Agent', ''),
            'remote_addr': request.remote_addr,
            'success': 200 <= status_code < 400
        }
        
        # Add query parameters for search endpoints
        if 'news' in path and request.args:
            metric['query_params'] = dict(request.args)
        
        # Add JSON body for POST requests
        if method == 'POST' and request.is_json:
            try:
                metric['request_body'] = request.get_json()
            except:
                pass
        
        # Store metric in memory (keep last 1000 requests)
        with self.metrics_lock:
            self.metrics_storage.append(metric)
            if len(self.metrics_storage) > 1000:
                self.metrics_storage.pop(0)
        
        # Log the metric
        self.logger.info(f"API_REQUEST - {json.dumps(metric, separators=(',', ':'))}")
        
        # Log slow requests separately
        if duration > 5.0:
            self.logger.warning(f"SLOW_REQUEST - {endpoint} took {duration:.2f}s")
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        with self.metrics_lock:
            metrics = self.metrics_storage.copy()
        
        if not metrics:
            return {
                'message': 'No performance data available',
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate statistics
        recent_metrics = metrics[-100:]  # Last 100 requests
        
        # Overall statistics
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.get('success', False))
        
        # Timing statistics
        durations = [m.get('duration', 0) for m in recent_metrics]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Endpoint statistics
        endpoint_stats = {}
        for metric in recent_metrics:
            endpoint = metric.get('endpoint', 'unknown')
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_duration': 0,
                    'success_count': 0,
                    'error_count': 0
                }
            
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_duration'] += metric.get('duration', 0)
            
            if metric.get('success', False):
                endpoint_stats[endpoint]['success_count'] += 1
            else:
                endpoint_stats[endpoint]['error_count'] += 1
        
        # Calculate averages for endpoints
        for endpoint, stats in endpoint_stats.items():
            if stats['count'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['count']
                stats['success_rate'] = stats['success_count'] / stats['count']
        
        # Identify slow endpoints
        slow_endpoints = {
            endpoint: stats for endpoint, stats in endpoint_stats.items()
            if stats.get('avg_duration', 0) > 3.0
        }
        
        # Recent errors
        recent_errors = [
            {
                'endpoint': m.get('endpoint'),
                'status_code': m.get('status_code'),
                'duration': m.get('duration'),
                'timestamp': m.get('timestamp')
            }
            for m in recent_metrics[-20:]  # Last 20 requests
            if not m.get('success', False)
        ]
        
        dashboard_data = {
            'summary': {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
                'avg_response_time': avg_duration,
                'max_response_time': max_duration,
                'min_response_time': min_duration
            },
            'endpoint_performance': endpoint_stats,
            'slow_endpoints': slow_endpoints,
            'recent_errors': recent_errors,
            'performance_alerts': self.generate_performance_alerts(endpoint_stats),
            'timestamp': datetime.now().isoformat()
        }
        
        return dashboard_data
    
    def get_recent_metrics(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent performance metrics"""
        with self.metrics_lock:
            recent_metrics = self.metrics_storage[-limit:] if self.metrics_storage else []
        
        return {
            'metrics': recent_metrics,
            'count': len(recent_metrics),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_performance_alerts(self, endpoint_stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate performance alerts based on endpoint statistics"""
        alerts = []
        
        for endpoint, stats in endpoint_stats.items():
            avg_duration = stats.get('avg_duration', 0)
            success_rate = stats.get('success_rate', 1)
            request_count = stats.get('count', 0)
            
            # Alert for slow endpoints
            if avg_duration > 10.0:
                alerts.append({
                    'type': 'high_latency',
                    'severity': 'critical',
                    'endpoint': endpoint,
                    'message': f'Endpoint {endpoint} has very high average response time: {avg_duration:.2f}s',
                    'avg_duration': avg_duration
                })
            elif avg_duration > 5.0:
                alerts.append({
                    'type': 'moderate_latency',
                    'severity': 'warning',
                    'endpoint': endpoint,
                    'message': f'Endpoint {endpoint} has high average response time: {avg_duration:.2f}s',
                    'avg_duration': avg_duration
                })
            
            # Alert for low success rates
            if success_rate < 0.8 and request_count >= 5:
                alerts.append({
                    'type': 'low_success_rate',
                    'severity': 'critical',
                    'endpoint': endpoint,
                    'message': f'Endpoint {endpoint} has low success rate: {success_rate:.1%}',
                    'success_rate': success_rate
                })
            elif success_rate < 0.95 and request_count >= 5:
                alerts.append({
                    'type': 'moderate_success_rate',
                    'severity': 'warning',
                    'endpoint': endpoint,
                    'message': f'Endpoint {endpoint} has moderate success rate: {success_rate:.1%}',
                    'success_rate': success_rate
                })
        
        return alerts

def monitor_performance(f):
    """Decorator to add detailed performance monitoring to specific functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        function_name = f.__name__
        
        # Setup function-specific logger
        logger = logging.getLogger(f'function_performance.{function_name}')
        
        try:
            result = f(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"FUNCTION_SUCCESS - {function_name} completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"FUNCTION_ERROR - {function_name} failed in {duration:.2f}s: {str(e)}")
            raise
    
    return decorated_function