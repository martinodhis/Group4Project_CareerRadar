import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './UseAuth';
import { apiDelete, apiGet, apiPost } from '../services/Api';
import { fetchJobs } from '../services/JobApi';

export const useJobs = (initialTag = '') => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState(initialTag);
  const [reloadCount, setReloadCount] = useState(0);

  const updateSearchTerm = useCallback((query) => {
    setLoading(true);
    setError(null);
    if (query === searchTerm) {
      setReloadCount((current) => current + 1);
    } else {
      setSearchTerm(query);
    }
  }, [searchTerm]);

  useEffect(() => {
    const controller = new AbortController();
    fetchJobs(20, searchTerm, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setJobs(data);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err.message || 'Failed to load jobs.');
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [searchTerm, reloadCount]);

  const refetch = useCallback(() => {
    setLoading(true);
    setError(null);
    setReloadCount((current) => current + 1);
  }, []);

  return { jobs, loading, error, searchTerm, setSearchTerm: updateSearchTerm, refetch };
};

export const useSavedJobs = () => {
  const { user } = useAuth();
  const [savedJobIds, setSavedJobIds] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    if (!user) return () => { active = false; };

    apiGet('/saved-jobs')
      .then((response) => {
        if (active) {
          setSavedJobIds(response.data.saved_jobs.map((saved) => String(saved.job_id)));
          setError(null);
        }
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      });

    return () => {
      active = false;
    };
  }, [user]);

  const toggleSavedJob = async (id) => {
    const key = String(id);
    if (!user) {
      setError('Sign in to save jobs to your account.');
      return;
    }
    setError(null);
    if (savedJobIds.includes(key)) {
      try {
        await apiDelete(`/saved-jobs/${encodeURIComponent(id)}`);
        setSavedJobIds((current) => current.filter((savedId) => savedId !== key));
      } catch (requestError) {
        setError(requestError.message);
      }
      return;
    }
    try {
      await apiPost('/saved-jobs', { job_id: id });
      setSavedJobIds((current) => [...current, key]);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return { savedJobIds: user ? savedJobIds : [], toggleSavedJob, savedJobsError: user ? error : null };
};

export default useJobs;
