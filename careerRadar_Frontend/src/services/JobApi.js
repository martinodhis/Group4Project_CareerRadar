import { ApiError, apiGet } from './Api';

const normalizeJob = (job) => {
  if (!job || typeof job !== 'object' || Array.isArray(job)) {
    throw new ApiError('CareerRadar returned an invalid job listing. Please try again.', 502);
  }

  return {
    ...job,
    id: job.id,
    title: job.title || 'Untitled role',
    company: job.company_name || 'Company',
    logo: job.company_logo || '',
    location: job.location || 'Remote',
    level: job.experience_level || '',
    jobTypes: job.employment_type ? [job.employment_type] : [],
    excerpt: job.description || '',
    publishedAt: job.published_at,
    url: getSafeExternalJobUrl(job.url),
    salaryMin: job.salary_min,
    salaryMax: job.salary_max,
    salaryCurrency: job.salary_currency || 'USD',
    industry: [job.industry || job.category].filter(Boolean),
  };
};

export const getSafeExternalJobUrl = (value) => {
  if (typeof value !== 'string' || !value.trim()) return '';
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : '';
  } catch {
    return '';
  }
};

export const fetchJobs = async (count = 20, tag = '', signal) => {
  const params = new URLSearchParams({ limit: String(count) });
  if (tag.trim()) params.set('keyword', tag.trim());
  const response = await apiGet(`/jobs?${params}`, { signal });
  if (!Array.isArray(response.data?.jobs)) {
    throw new ApiError('CareerRadar returned an invalid jobs response. Please try again.', 502);
  }
  return response.data.jobs.map(normalizeJob);
};

export const fetchJob = async (id, signal) => {
  const response = await apiGet(`/jobs/${encodeURIComponent(id)}`, { signal });
  if (!response.data || typeof response.data !== 'object' || Array.isArray(response.data)) {
    throw new ApiError('CareerRadar returned an invalid job response. Please try again.', 502);
  }
  return normalizeJob(response.data);
};

export const formatJobDate = (value) => {
  if (!value) return 'Date unavailable';

  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Date unavailable'
    : new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
};

export const formatSalaryRange = (job) => {
  if (!job) return 'Salary not specified';

  const minimum = job.salaryMin ?? job.salary_min;
  const maximum = job.salaryMax ?? job.salary_max;
  const currency = job.salaryCurrency ?? job.salary_currency ?? 'USD';
  const formatter = new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 0 });

  if (minimum && maximum) return `${formatter.format(minimum)} – ${formatter.format(maximum)}`;
  if (minimum) return `From ${formatter.format(minimum)}`;
  if (maximum) return `Up to ${formatter.format(maximum)}`;
  return 'Salary not specified';
};
