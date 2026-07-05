import { useEffect, useState } from 'react';

export default function SessionModal({
  applicantId,
  onContinueSession,
  onStartNewSession,
}) {
  const [existingSessions, setExistingSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingSessionId, setDeletingSessionId] = useState(null);

  const fetchSessions = async () => {
    try {
      const response = await fetch(
        `/api/applicant-sessions/${encodeURIComponent(applicantId)}`
      );
      if (response.ok) {
        const data = await response.json();
        setExistingSessions(data);
      } else {
        setExistingSessions([]);
      }
    } catch {
      setExistingSessions([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [applicantId]);

  const handleStartNew = () => {
    onStartNewSession();
  };

  const handleContinue = () => {
    if (selectedSession) {
      onContinueSession(selectedSession.session_id);
    }
  };

  const handleDelete = async (sessionId) => {
    setDeletingSessionId(sessionId);
    try {
      const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete session.');
      }
      // Refresh the list
      await fetchSessions();
      if (selectedSession?.session_id === sessionId) {
        setSelectedSession(null);
      }
    } catch (err) {
      alert(err.message || 'Failed to delete session.');
    } finally {
      setDeletingSessionId(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="session-selection-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Session</p>
            <h2 id="session-selection-title">Select session</h2>
            <p className="modal-copy">
              Continue an existing interview session or start a new one.
            </p>
          </div>
        </div>

        <div className="modal-content">
          {isLoading ? (
            <p className="no-profiles">Loading sessions...</p>
          ) : existingSessions.length > 0 ? (
            <div className="profile-cards">
              {existingSessions.map((session) => {
                const isSelected = selectedSession?.session_id === session.session_id;
                const isDeleting = deletingSessionId === session.session_id;
                return (
                  <div
                    className={`profile-card ${isSelected ? 'selected' : ''}`}
                    key={session.session_id}
                    onClick={() => setSelectedSession(session)}
                    role="button"
                    tabIndex={0}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="profile-card-header">
                      <div>
                        <h4>
                          Session {session.session_id.slice(0, 8)}
                          {session.is_done ? (
                            <span className="session-status done">Done</span>
                          ) : (
                            <span className="session-status active">Active</span>
                          )}
                        </h4>
                        <p>
                          CV v{session.cv_version} · {session.job_profile?.job_title || 'Unknown role'} at{' '}
                          {session.job_profile?.company || 'Unknown company'}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="pill secondary delete-session-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(session.session_id);
                        }}
                        disabled={isDeleting}
                        aria-label={`Delete session ${session.session_id.slice(0, 8)}`}
                      >
                        {isDeleting ? '...' : 'Delete'}
                      </button>
                    </div>
                    <p className="profile-description">Created {formatDate(session.created_at)}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="no-profiles">No existing sessions. Start a new session to begin.</p>
          )}
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="pill secondary"
            style={{ marginLeft: 'auto' }}
            onClick={handleStartNew}
          >
            Start new session
          </button>
          <button
            type="button"
            className="pill"
            onClick={handleContinue}
            disabled={!selectedSession}
          >
            Continue session
          </button>
        </div>
      </section>
    </div>
  );
}
