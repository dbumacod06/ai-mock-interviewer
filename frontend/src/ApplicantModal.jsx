import { useEffect, useState } from 'react';

export default function ApplicantModal({
  applicantDetails,
  isLoadingApplicant,
  isEditing,
  onFindApplicant,
  onNext,
  onCreateNew,
}) {
  const [step, setStep] = useState(null);
  const [applicantId, setApplicantId] = useState('');
  const [applicantForm, setApplicantForm] = useState({
    firstName: applicantDetails.firstName || '',
    lastName: applicantDetails.lastName || '',
    preferredName: applicantDetails.preferredName || '',
  });

  useEffect(() => {
    setApplicantForm({
      firstName: applicantDetails.firstName || '',
      lastName: applicantDetails.lastName || '',
      preferredName: applicantDetails.preferredName || '',
    });
  }, [applicantDetails]);

  const updateApplicantField = (field, value) => {
    setApplicantForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const submitApplicantDetails = (event) => {
    event.preventDefault();

    if (!applicantForm.firstName.trim() || !applicantForm.lastName.trim() || !applicantForm.preferredName.trim()) {
      alert('Please fill in all required fields: First name, Last name, and Preferred name.');
      return;
    }

    onNext({
      first_name: applicantForm.firstName.trim(),
      last_name: applicantForm.lastName.trim(),
      preferred_name: applicantForm.preferredName.trim(),
    });
  };

  const submitApplicantId = (event) => {
    event.preventDefault();
    onFindApplicant(applicantId.trim());
  };

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="applicant-modal-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Welcome</p>
            <h2 id="applicant-modal-title">Tell us about the applicant</h2>
            <p className="modal-copy">
              Capture the profile before starting the interview flow so the assistant has the right context.
            </p>
          </div>
        </div>

        <div className="modal-content">
          {!step ? (
            <div className="applicant-record-prompt">
              <p>Do you already have an applicant record in our system?</p>
            </div>
          ) : null}

          {step === 'lookup' ? (
            <form id="applicant-lookup-form" className="applicant-form" onSubmit={submitApplicantId}>
              <label className="full-width">
                Applicant ID
                <input
                  type="text"
                  value={applicantId}
                  onChange={(event) => setApplicantId(event.target.value)}
                  placeholder="app_usr_849201"
                  required
                />
              </label>
            </form>
          ) : null}

          {step === 'create' ? (
            <form id="applicant-create-form" className="applicant-form" onSubmit={submitApplicantDetails}>
              <label>
                First name
                <input
                  type="text"
                  value={applicantForm.firstName}
                  onChange={(event) => updateApplicantField('firstName', event.target.value)}
                  placeholder="First name"
                  required
                  disabled={isEditing}
                />
              </label>
              <label>
                Last name
                <input
                  type="text"
                  value={applicantForm.lastName}
                  onChange={(event) => updateApplicantField('lastName', event.target.value)}
                  placeholder="Last name"
                  required
                  disabled={isEditing}
                />
              </label>
              <label>
                Preferred name
                <input
                  type="text"
                  value={applicantForm.preferredName}
                  onChange={(event) => updateApplicantField('preferredName', event.target.value)}
                  placeholder="Preferred name"
                  required
                  disabled={isEditing}
                />
              </label>
            </form>
          ) : null}
        </div>

        <div className="modal-footer">
          {!step ? (
            <>
              <button type="button" className="pill secondary" onClick={() => {
                setStep('create');
                onCreateNew?.();
              }}>
                No, enter details
              </button>
              <button type="button" className="pill" onClick={() => setStep('lookup')}>
                Yes, use applicant ID
              </button>
            </>
          ) : null}

          {step === 'lookup' ? (
            <>
              <button type="button" className="pill secondary" onClick={() => setStep(null)}>
                Back
              </button>
              <button type="submit" form="applicant-lookup-form" className="pill" disabled={isLoadingApplicant || !applicantId.trim()}>
                {isLoadingApplicant ? 'Finding...' : 'Start interview'}
              </button>
            </>
          ) : null}

          {step === 'create' ? (
            <>
              <button type="button" className="pill secondary" onClick={() => setStep(null)}>
                Back
              </button>
              <button type="submit" form="applicant-create-form" className="pill">
                {isEditing ? 'Next' : 'Next'}
              </button>
            </>
          ) : null}
        </div>
      </section>
    </div>
  );
}
