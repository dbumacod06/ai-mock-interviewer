import { useEffect, useState } from 'react';

export default function InterviewReviewModal({ sessionId, onClose }) {
  const [reviewPairs, setReviewPairs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReview();
  }, [sessionId]);

  const fetchReview = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/interview-review/${encodeURIComponent(sessionId)}`);
      if (res.ok) {
        const data = await res.json();
        setReviewPairs(data.review_pairs || []);
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to load interview review.');
      }
    } catch {
      setError('Could not reach the backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal review-modal" role="dialog" aria-modal="true" aria-labelledby="review-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Review</p>
            <h2 id="review-title">Suggested Responses</h2>
            <p className="modal-copy">
              AI-generated answers based on the applicant's profile and CV.
            </p>
          </div>
        </div>

        <div className="modal-content">
          {isLoading ? (
            <p className="no-profiles">Generating review...</p>
          ) : error ? (
            <p className="no-profiles error">{error}</p>
          ) : reviewPairs.length > 0 ? (
            <div className="review-pairs">
              {reviewPairs.map((pair, i) => (
                <div className="review-pair" key={i}>
                  <div className="review-question">
                    <p className="review-label">Interviewer Question</p>
                    <p className="review-text">{pair.interviewer_question}</p>
                  </div>
                  <div className="review-response">
                    <p className="review-label">Suggested Response</p>
                    <p className="review-text">{pair.suggested_response}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-profiles">No review data available.</p>
          )}
        </div>

        <div className="modal-footer">
          <button type="button" className="pill secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </section>
    </div>
  );
}
