# Heario Performance Monitoring Guide

This guide explains how to use the performance monitoring tools to identify bottlenecks in the Heario news search functionality.

## Overview

The performance monitoring system consists of several components:

1. **Performance Logging** - Added to backend endpoints and services
2. **Performance Monitor Script** - Measures individual components
3. **Performance Test Runner** - Load testing and bottleneck analysis
4. **Performance Middleware** - Real-time API monitoring
5. **Performance Dashboard** - Web-based monitoring interface

## Quick Start

### 1. Run Individual Component Analysis

```bash
cd /Users/cyril/Documents/git/heario/backend
python performance_monitor.py --iterations 3 --query "台灣"
```

This will:
- Test News API performance
- Test Jina AI performance
- Test Gemini summarization performance
- Generate comprehensive performance report

### 2. Run Load Testing

```bash
python performance_test_runner.py --sequential 3 --concurrent 3 --queries "台灣" "AI" "科技"
```

This will:
- Run sequential requests (baseline)
- Run concurrent requests (load test)
- Analyze bottlenecks
- Generate recommendations

### 3. Run Stress Testing

```bash
python performance_test_runner.py --stress-test --stress-duration 60 --stress-rps 2
```

### 4. Monitor Real-time Performance

Start your Flask server and visit:
- `http://localhost:5001/api/performance/dashboard` - Performance dashboard
- `http://localhost:5001/api/performance/metrics` - Recent metrics API

## Understanding the Results

### Performance Logs

Several log files are generated:

1. **performance.log** - Main endpoint performance logs
2. **crawler_performance.log** - News API and Jina AI performance
3. **summarizer_performance.log** - Gemini summarization performance
4. **api_performance.log** - Real-time API monitoring

### Key Metrics

- **Total Time** - End-to-end request time
- **News API Time** - Time to fetch articles from News API
- **Jina AI Time** - Time to fetch full content per article
- **Summarization Time** - Time to generate summary per article
- **Database Time** - Time for database operations

### Identifying Bottlenecks

The tools will automatically identify the slowest component:

1. **Jina AI Bottleneck** - If Jina AI takes >50% of total time
2. **Summarization Bottleneck** - If Gemini takes >30% of total time  
3. **News API Bottleneck** - If News API is consistently slow
4. **Database Bottleneck** - If database operations are slow

## Common Performance Issues

### Jina AI Issues
- **Symptoms**: High Jina AI response times (>10s per article)
- **Causes**: Network latency, blocked domains, rate limiting
- **Solutions**: 
  - Implement caching
  - Reduce timeout values
  - Process articles in parallel
  - Use fallback content sources

### Gemini Summarization Issues
- **Symptoms**: High summarization times (>5s per article)
- **Causes**: API rate limiting, large content size, network issues
- **Solutions**:
  - Implement request batching
  - Reduce content size before summarization
  - Add caching for similar content
  - Use fallback summarization methods

### Database Issues
- **Symptoms**: Slow database lookups/inserts (>1s)
- **Solutions**:
  - Add database indexes
  - Optimize queries
  - Consider connection pooling

## Performance Optimization Recommendations

Based on typical results, here are optimization priorities:

### Priority 1: Jina AI Optimization
```python
# In news_crawler.py, add timeout control
response = requests.get(jina_url, headers=headers, timeout=15)  # Reduced from 30s

# Consider parallel processing
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    jina_results = list(executor.map(crawler.fetch_with_jina, urls))
```

### Priority 2: Caching Implementation
```python
# Add Redis caching for Jina AI results
import redis
cache = redis.Redis()

def fetch_with_jina_cached(self, url: str) -> str:
    cache_key = f"jina:{url}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result.decode('utf-8')
    
    result = self.fetch_with_jina(url)
    if result:
        cache.setex(cache_key, 3600, result)  # Cache for 1 hour
    return result
```

### Priority 3: Database Optimization
```python
# Add indexes to MongoDB
db.news.create_index([("url", 1)])  # Index on URL for duplicate checking
db.news.create_index([("created_at", -1)])  # Index for chronological queries
```

## Monitoring in Production

### Set up Log Rotation
```bash
# Add to crontab
0 0 * * * /usr/sbin/logrotate /path/to/logrotate.conf
```

### Set up Alerts
Monitor the performance logs for:
- Average response times > 30 seconds
- Success rates < 95%
- Jina AI failure rates > 20%
- Database operation times > 2 seconds

### Performance Dashboard
The built-in dashboard at `/api/performance/dashboard` provides:
- Real-time performance metrics
- Endpoint performance breakdown
- Error tracking
- Performance alerts

## Interpreting Test Results

### Example Good Performance
```
PERFORMANCE_SUMMARY - Total: 8.45s, News API: 1.2s, Avg Jina: 2.1s, Avg Summarization: 1.8s
```
- Well-balanced across components
- Total time under 10 seconds
- No single component dominating

### Example Jina AI Bottleneck
```
PERFORMANCE_SUMMARY - Total: 45.2s, News API: 1.1s, Avg Jina: 18.3s, Avg Summarization: 2.1s
```
- Jina AI taking 40% of total time
- Need to optimize Jina AI calls

### Example Summarization Bottleneck
```
PERFORMANCE_SUMMARY - Total: 25.1s, News API: 1.0s, Avg Jina: 3.2s, Avg Summarization: 12.4s
```
- Summarization taking 50% of total time
- Need to optimize Gemini API calls

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd /Users/cyril/Documents/git/heario/backend
   # Install required packages
   pip install aiohttp
   ```

2. **Permission Errors on Log Files**
   ```bash
   chmod 666 /Users/cyril/Documents/git/heario/backend/*.log
   ```

3. **MongoDB Connection Issues**
   - Check if MongoDB is running
   - Verify MONGODB_URI in .env file

4. **API Key Issues**
   - Verify NEWS_API_KEY is set
   - Verify JINA_API_KEY is set (if using authenticated Jina)
   - Verify GEMINI API key is set

### Performance Testing Best Practices

1. **Test with Clean Database** - Clear old articles before testing
2. **Test Different Queries** - Use various search terms
3. **Test at Different Times** - Network conditions vary
4. **Run Multiple Iterations** - Get statistical significance
5. **Monitor System Resources** - Check CPU, memory, network during tests

## Next Steps

After identifying bottlenecks:

1. **Implement targeted optimizations** based on test results
2. **Set up continuous monitoring** in production
3. **Create performance benchmarks** for regression testing
4. **Consider architectural changes** if needed (caching, load balancing, etc.)

For questions or issues, check the performance logs and dashboard for detailed metrics.