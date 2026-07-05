import { useEffect, useState } from 'react';

export default function ApplicantConfirmationModal({
  applicantId,
  onProceed,
}) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(applicantId);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement('textarea');
        textArea.value = applicantId;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
          document.execCommand('copy');
          setIsCopied(true);
          setTimeout(() => setIsCopied(false), 2000);
        } catch (err) {
          alert('Unable to copy automatically. Please manually copy the ID: ' + applicantId);
        }
        document.body.removeChild(textArea);
      }
    } catch (err) {
      alert('Unable to copy. Please manually copy the ID: ' + applicantId);
    }
  };

  return (
    <div className="modal-backdrop" role="presentation" style={{ zIndex: 60 }}>
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="confirmation-modal-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Applicant Created</p>
            <h2 id="confirmation-modal-title">Success!</h2>
            <p className="modal-copy">
              Your applicant profile has been created. Please save this ID for future reference.
            </p>
          </div>
        </div>

        <div className="modal-content">
          <div className="applicant-summary">
            <p className="summary-label">Applicant ID</p>
            <h3>{applicantId}</h3>
            <button
              type="button"
              className="pill secondary"
              style={{ width: 'fit-content', marginTop: '12px' }}
              onClick={handleCopy}
            >
              {isCopied ? 'Copied!' : 'Copy ID'}
            </button>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="pill" onClick={onProceed}>
            Proceed
          </button>
        </div>
      </section>
    </div>
  );
}
