import { useState } from 'react';

export default function JobProfileModal({
  existingProfiles,
  onBack,
  onSave,
  isSaving,
  onResetSession,
  startInFormMode,
  isNewApplicant,
}) {
  const [mode, setMode] = useState(startInFormMode ? 'form' : 'list');
  const [editingProfile, setEditingProfile] = useState(null);
  const [profiles, setProfiles] = useState(existingProfiles || []);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({
    jobTitle: '',
    company: '',
    jobDescription: '',
    companyVision: '',
    companyMission: '',
    additionalContext: '',
  });

  const handleBack = () => {
    if (isNewApplicant && mode === 'form') {
      onBack();
    } else {
      setMode('list');
    }
  };

  const startNew = () => {
    onResetSession?.();
    setProfileForm({
      jobTitle: '',
      company: '',
      jobDescription: '',
      companyVision: '',
      companyMission: '',
      additionalContext: '',
    });
    setEditingProfile(null);
    setMode('form');
  };

  const startEdit = (profile) => {
    onResetSession?.();
    setProfileForm({
      jobTitle: profile.jobTitle || '',
      company: profile.company || '',
      jobDescription: profile.jobDescription || '',
      companyVision: profile.companyVision || '',
      companyMission: profile.companyMission || '',
      additionalContext: profile.additionalContext || '',
    });
    setEditingProfile(profile);
    setMode('form');
  };

  const updateField = (field, value) => {
    setProfileForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const submitProfile = (event) => {
    event.preventDefault();

    if (!profileForm.jobTitle.trim() || !profileForm.company.trim() || !profileForm.jobDescription.trim() ||
        !profileForm.companyVision.trim() || !profileForm.companyMission.trim()) {
      alert('Please fill in all required fields: Job title, Company, Job description, Company vision, and Company mission.');
      return;
    }

    const payload = {
      job_title: profileForm.jobTitle.trim(),
      company: profileForm.company.trim(),
      job_description: profileForm.jobDescription.trim(),
      company_vision: profileForm.companyVision.trim(),
      company_mission: profileForm.companyMission.trim(),
      additional_context: profileForm.additionalContext.trim(),
    };

    if (editingProfile?.profileId) {
      setProfiles((current) =>
        current.map((p) => (p.profileId === editingProfile.profileId ? { ...p, ...payload } : p))
      );
    } else {
      const newProfile = payload;
      setProfiles((current) => [...current, newProfile]);
      setSelectedProfile(newProfile);
    }

    setMode('list');
  };

  const handleSave = () => {
    if (!selectedProfile) {
      return;
    }

    const normalizedProfile = {
      profileId: selectedProfile.profileId || selectedProfile.id || '',
      job_title: selectedProfile.jobTitle || selectedProfile.job_title || '',
      company: selectedProfile.company || '',
      job_description: selectedProfile.jobDescription || selectedProfile.job_description || '',
      company_vision: selectedProfile.companyVision || selectedProfile.company_vision || '',
      company_mission: selectedProfile.companyMission || selectedProfile.company_mission || '',
      additional_context: selectedProfile.additionalContext || selectedProfile.additional_context || '',
    };
    onSave(normalizedProfile);
  };

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="job-profile-modal-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Job Profile</p>
            <h2 id="job-profile-modal-title">Target role and company</h2>
            <p className="modal-copy">
              Select a job profile for the interview, or create a new one.
            </p>
          </div>
        </div>

        {mode === 'list' ? (
          <div className="modal-content">
            <div className="job-profile-list">
              {profiles && profiles.length > 0 ? (
                <div className="profile-cards">
                  {profiles.map((profile, index) => {
                    const isSelected = selectedProfile === profile;
                    return (
                      <div
                        className={`profile-card ${isSelected ? 'selected' : ''}`}
                        key={profile.profileId || index}
                        onClick={() => setSelectedProfile(profile)}
                        role="button"
                        tabIndex={0}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="profile-card-header">
                          <div>
                            <h4>{profile.jobTitle || profile.job_title}</h4>
                            <p>{profile.company}</p>
                          </div>
                          <button
                            type="button"
                            className="pill secondary edit-profile-button"
                            onClick={(e) => {
                              e.stopPropagation();
                              startEdit(profile);
                            }}
                          >
                            Edit
                          </button>
                        </div>
                        <p className="profile-description">{profile.jobDescription || profile.job_description}</p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="no-profiles">No job profiles yet. Create one to get started.</p>
              )}
            </div>
          </div>
        ) : null}

        {mode === 'form' ? (
          <div className="modal-content">
            <form id="job-profile-form" className="applicant-form" onSubmit={submitProfile}>
              <label>
                Job title
                <input
                  type="text"
                  value={profileForm.jobTitle}
                  onChange={(event) => updateField('jobTitle', event.target.value)}
                  placeholder="AI Engineer"
                  required
                />
              </label>
              <label>
                Company
                <input
                  type="text"
                  value={profileForm.company}
                  onChange={(event) => updateField('company', event.target.value)}
                  placeholder="TechCorp Inc."
                  required
                />
              </label>
              <label className="full-width">
                Job description
                <textarea
                  value={profileForm.jobDescription}
                  onChange={(event) => updateField('jobDescription', event.target.value)}
                  placeholder="Describe the role and responsibilities..."
                  rows={4}
                  required
                />
              </label>
              <label className="full-width">
                Company vision
                <textarea
                  value={profileForm.companyVision}
                  onChange={(event) => updateField('companyVision', event.target.value)}
                  placeholder="What is the company's vision?"
                  rows={3}
                  required
                />
              </label>
              <label className="full-width">
                Company mission
                <textarea
                  value={profileForm.companyMission}
                  onChange={(event) => updateField('companyMission', event.target.value)}
                  placeholder="What is the company's mission?"
                  rows={3}
                  required
                />
              </label>
              <label className="full-width">
                Additional context
                <textarea
                  value={profileForm.additionalContext}
                  onChange={(event) => updateField('additionalContext', event.target.value)}
                  placeholder="Any other relevant context for the interview..."
                  rows={3}
                />
              </label>
            </form>
          </div>
        ) : null}

        <div className="modal-footer">
          {mode === 'list' ? (
            <>
              <button type="button" className="pill secondary" onClick={onBack}>
                Back
              </button>
              <button type="button" className="pill secondary" style={{ marginLeft: 'auto' }} onClick={startNew}>
                + New job profile
              </button>
              <button
                type="button"
                className="pill"
                onClick={handleSave}
                disabled={isSaving || !selectedProfile}
              >
                {isSaving ? 'Saving...' : 'Save & Start Interview'}
              </button>
            </>
          ) : null}

          {mode === 'form' ? (
            <>
              <button type="button" className="pill secondary" onClick={handleBack}>
                Back
              </button>
              <button type="submit" form="job-profile-form" className="pill">
                {editingProfile ? 'Update profile' : 'Save profile'}
              </button>
            </>
          ) : null}
        </div>
      </section>
    </div>
  );
}
