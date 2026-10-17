import requests

BASE_URL = 'https://jobicy.com/api/v2/remote-jobs'

def fetch_jobs_from_api(count=20, tag=''):
    try:
        url = f"{BASE_URL}?count={count}"
        if tag and tag.strip():
            url += f"&tag={tag.strip()}"
        
        response = requests.get(url)
        if response.status_code != 200:
            return []
        
        data = response.json()
        jobs = data.get('jobs', [])
        
        normalized = []
        for job in jobs:
            normalized.append({
                'id': str(job.get('id') or job.get('jobId')),
                'title': job.get('jobTitle') or job.get('title') or 'Untitled role',
                'company': job.get('companyName') or job.get('company') or 'Company',
                'logo': job.get('companyLogo') or job.get('logo') or '',
                'location': job.get('jobGeo') or job.get('location') or 'Remote',
                'level': ', '.join(job.get('jobLevel')) if isinstance(job.get('jobLevel'), list) else (job.get('jobLevel') or job.get('level') or ''),
                'job_types': job.get('jobType') if isinstance(job.get('jobType'), list) else ([job.get('jobType')] if job.get('jobType') else job.get('jobTypes') or []),
                'excerpt': job.get('jobExcerpt') or job.get('excerpt') or '',
                'published_at': job.get('pubDate') or job.get('publishedAt'),
                'url': job.get('url') or job.get('jobUrl') or '',
                'salary_min': job.get('salaryMin') or job.get('salary_min'),
                'salary_max': job.get('salaryMax') or job.get('salary_max'),
                'salary_currency': job.get('salaryCurrency') or job.get('salary_currency') or 'USD',
                'industry': job.get('jobIndustry') or job.get('industry') or []
            })
        return normalized
    except Exception as e:
        print(f"Error fetching from Jobicy: {e}")
        return []
