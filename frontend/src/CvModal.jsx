import { useEffect, useState } from 'react';

export default function CvModal({
  cvVersions,
  applicantId,
  onNext,
  onBack,
  isNewApplicant,
}) {
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [isEditMode, setIsEditMode] = useState(isNewApplicant || false);
  const [editForm, setEditForm] = useState({
    currentRole: '',
    currentCompany: '',
    currentResponsibilities: '',
    pastRoles: [],
  });

  const handleBack = () => {
    if (isNewApplicant && isEditMode) {
      onBack();
    } else {
      setIsEditMode(false);
    }
  };

  useEffect(() => {
    if (cvVersions && cvVersions.length > 0) {
      setSelectedVersion(cvVersions[0]);
    } else {
      setSelectedVersion(null);
    }
  }, [cvVersions]);

  const handleUseThisVersion = () => {
    if (selectedVersion) {
      onNext({
        current_role: selectedVersion.cv?.currentRole || '',
        current_company: selectedVersion.cv?.currentCompany || '',
        current_responsibilities: selectedVersion.cv?.currentResponsibilities || '',
        past_roles: selectedVersion.cv?.pastRoles || [],
        version: selectedVersion.cv?.version,
      });
    }
  };

  const handleCreateFromThisVersion = () => {
    if (selectedVersion) {
      setEditForm({
        currentRole: selectedVersion.cv?.currentRole || '',
        currentCompany: selectedVersion.cv?.currentCompany || '',
        currentResponsibilities: selectedVersion.cv?.currentResponsibilities || '',
        pastRoles: selectedVersion.cv?.pastRoles || [],
      });
    } else {
      setEditForm({
        currentRole: '',
        currentCompany: '',
        currentResponsibilities: '',
        pastRoles: [],
      });
    }
    setIsEditMode(true);
  };

  const handleCreateFromScratch = () => {
    setEditForm({
      currentRole: '',
      currentCompany: '',
      currentResponsibilities: '',
      pastRoles: [],
    });
    setIsEditMode(true);
  };

  const handleEditSubmit = (event) => {
    event.preventDefault();

    if (!editForm.currentRole.trim() || !editForm.currentCompany.trim() || !editForm.currentResponsibilities.trim()) {
      alert('Please fill in all required fields: Current role, Current company, and Current responsibilities.');
      return;
    }

    onNext({
      current_role: editForm.currentRole.trim(),
      current_company: editForm.currentCompany.trim(),
      current_responsibilities: editForm.currentResponsibilities.trim(),
      past_roles: editForm.pastRoles.filter(
        (role) => role.role.trim() || role.company.trim() || role.responsibilities.trim()
      ),
    });
  };

  const updateEditField = (field, value) => {
    setEditForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const addPastRole = () => {
    setEditForm((current) => ({
      ...current,
      pastRoles: [...current.pastRoles, { role: '', company: '', responsibilities: '' }],
    }));
  };

  const removePastRole = (index) => {
    setEditForm((current) => ({
      ...current,
      pastRoles: current.pastRoles.filter((_, i) => i !== index),
    }));
  };

  const updatePastRole = (index, field, value) => {
    setEditForm((current) => {
      const updated = [...current.pastRoles];
      updated[index] = { ...updated[index], [field]: value };
      return { ...current, pastRoles: updated };
    });
  };

  const moveCurrentRoleToPast = () => {
    setEditForm((current) => {
      const newPastRole = {
        role: current.currentRole,
        company: current.currentCompany,
        responsibilities: current.currentResponsibilities,
      };
      return {
        ...current,
        currentRole: '',
        currentCompany: '',
        currentResponsibilities: '',
        pastRoles: [newPastRole, ...current.pastRoles],
      };
    });
  };

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="cv-modal-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Applicant CV</p>
            <h2 id="cv-modal-title">{isNewApplicant ? 'Create New Version' : 'Capture work experience'}</h2>
            <p className="modal-copy">
              {isNewApplicant
                ? 'Enter the applicant\'s work experience details to create the first CV version.'
                : 'Review the applicant\'s CV versions and select or create one for the interview.'}
            </p>
          </div>
        </div>

        {!isEditMode ? (
          <div className="modal-content">
            {/* Version Tags */}
            {cvVersions && cvVersions.length > 0 ? (
              <div className="cv-version-tags">
                <p className="cv-version-header">CV Versions</p>
                <div className="token-list">
                  {cvVersions.map((versionItem) => {
                    const version = versionItem.cv?.version;
                    const isSelected = selectedVersion?.cv?.version === version;
                    return (
                      <button
                        key={version}
                        type="button"
                        className={`token-chip ${isSelected ? 'selected' : ''}`}
                        onClick={() => setSelectedVersion(versionItem)}
                        style={{
                          background: isSelected ? 'rgba(56, 189, 248, 0.3)' : undefined,
                          borderColor: isSelected ? 'rgba(125, 211, 252, 0.6)' : undefined,
                        }}
                      >
                        v{version}
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="no-profiles">No existing CV versions.</p>
            )}

            {/* Read-only CV Details */}
            {selectedVersion ? (
              <div className="cv-readonly">
                <div className="cv-detail-row">
                  <span className="cv-detail-label">Current Role</span>
                  <span className="cv-detail-value">{selectedVersion.cv?.currentRole || 'N/A'}</span>
                </div>
                <div className="cv-detail-row">
                  <span className="cv-detail-label">Current Company</span>
                  <span className="cv-detail-value">{selectedVersion.cv?.currentCompany || 'N/A'}</span>
                </div>
                <div className="cv-detail-row full-width">
                  <span className="cv-detail-label">Current Responsibilities</span>
                  <span className="cv-detail-value">{selectedVersion.cv?.currentResponsibilities || 'N/A'}</span>
                </div>

                {selectedVersion.cv?.pastRoles && selectedVersion.cv.pastRoles.length > 0 ? (
                  <div className="cv-past-roles full-width">
                    <p className="past-roles-label">Past Roles</p>
                    {selectedVersion.cv.pastRoles.map((role, index) => (
                      <div className="past-role-card" key={index}>
                        <div className="past-role-header">
                          <span className="past-role-number">Role {index + 1}</span>
                        </div>
                        <div className="cv-detail-row">
                          <span className="cv-detail-label">Role</span>
                          <span className="cv-detail-value">{role.role || 'N/A'}</span>
                        </div>
                        <div className="cv-detail-row">
                          <span className="cv-detail-label">Company</span>
                          <span className="cv-detail-value">{role.company || 'N/A'}</span>
                        </div>
                        <div className="cv-detail-row full-width">
                          <span className="cv-detail-label">Responsibilities</span>
                          <span className="cv-detail-value">{role.responsibilities || 'N/A'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>
        ) : (
          /* Edit Mode */
          <div className="modal-content">
            <form id="cv-edit-form" className="applicant-form" onSubmit={handleEditSubmit}>
              <label>
                Current role
                <input
                  type="text"
                  value={editForm.currentRole}
                  onChange={(event) => updateEditField('currentRole', event.target.value)}
                  placeholder="AI Engineer"
                  required
                />
              </label>
              <label>
                Current company
                <input
                  type="text"
                  value={editForm.currentCompany}
                  onChange={(event) => updateEditField('currentCompany', event.target.value)}
                  placeholder="TechCorp Inc."
                  required
                />
              </label>
              <label className="full-width">
                Current responsibilities
                <textarea
                  value={editForm.currentResponsibilities}
                  onChange={(event) => updateEditField('currentResponsibilities', event.target.value)}
                  placeholder="Describe the applicant's current responsibilities..."
                  rows={4}
                  required
                />
              </label>

              <div className="full-width">
                <button
                  type="button"
                  className="pill secondary"
                  onClick={moveCurrentRoleToPast}
                  disabled={!editForm.currentRole.trim()}
                >
                  + Move current role to past roles
                </button>
              </div>

              <div className="full-width past-roles-section">
                <label className="past-roles-label">Past roles</label>
                {editForm.pastRoles.map((role, index) => (
                  <div className="past-role-card" key={index}>
                    <div className="past-role-header">
                      <span className="past-role-number">Role {index + 1}</span>
                      <button
                        type="button"
                        className="token-remove"
                        onClick={() => removePastRole(index)}
                        aria-label={`Remove role ${index + 1}`}
                      >
                        ×
                      </button>
                    </div>
                    <label>
                      Role
                      <input
                        type="text"
                        value={role.role}
                        onChange={(event) => updatePastRole(index, 'role', event.target.value)}
                        placeholder="Data Scientist"
                      />
                    </label>
                    <label>
                      Company
                      <input
                        type="text"
                        value={role.company}
                        onChange={(event) => updatePastRole(index, 'company', event.target.value)}
                        placeholder="OldCo Inc."
                      />
                    </label>
                    <label className="full-width">
                      Responsibilities
                      <textarea
                        value={role.responsibilities}
                        onChange={(event) => updatePastRole(index, 'responsibilities', event.target.value)}
                        placeholder="Describe responsibilities..."
                        rows={3}
                      />
                    </label>
                  </div>
                ))}
                <button type="button" className="pill secondary add-role-button" onClick={addPastRole}>
                  + Add past role
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="modal-footer">
          {!isEditMode ? (
            <>
              <button type="button" className="pill secondary" onClick={onBack}>
                Back
              </button>
              <div className="action-buttons" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="pill secondary"
                  onClick={handleCreateFromScratch}
                  disabled={!applicantId}
                >
                  Create New Version
                </button>
                <button
                  type="button"
                  className="pill secondary"
                  onClick={handleCreateFromThisVersion}
                  disabled={!selectedVersion || !applicantId}
                >
                  {`Create New Version From v${selectedVersion?.cv?.version || 'Selected'}`}
                </button>
                <button
                  type="button"
                  className="pill"
                  onClick={handleUseThisVersion}
                  disabled={!selectedVersion}
                >
                  Use this version
                </button>
              </div>
            </>
          ) : (
            <>
              <button type="button" className="pill secondary" onClick={handleBack}>
                Back
              </button>
              <button type="submit" form="cv-edit-form" className="pill">
                Next
              </button>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
