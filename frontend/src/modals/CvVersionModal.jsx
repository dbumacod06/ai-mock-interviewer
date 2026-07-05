import { useState } from 'react';

export default function CvVersionModal({
  existingVersions,
  onSelectVersion,
  onCreateNew,
  onBack,
}) {
  const [selectedVersion, setSelectedVersion] = useState(null);

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="applicant-modal" role="dialog" aria-modal="true" aria-labelledby="cv-version-title">
        <div className="modal-header">
          <div>
            <p className="eyebrow">CV Version</p>
            <h2 id="cv-version-title">Select CV version</h2>
            <p className="modal-copy">
              Choose an existing CV version or create a new one based on the latest version.
            </p>
          </div>
        </div>

        <div className="modal-content">
          <div className="cv-versions-list">
            {existingVersions && existingVersions.length > 0 ? (
              <div className="profile-cards">
                {existingVersions.map((versionItem) => {
                  const cv = versionItem.cv;
                  const isSelected = selectedVersion === cv.version;
                  return (
                    <div
                      className={`profile-card ${isSelected ? 'selected' : ''}`}
                      key={cv.version}
                      onClick={() => setSelectedVersion(cv.version)}
                      role="button"
                      tabIndex={0}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="profile-card-header">
                        <div>
                          <h4>Version {cv.version}</h4>
                          <p>{cv.currentRole} at {cv.currentCompany}</p>
                        </div>
                      </div>
                      <p className="profile-description">{cv.currentResponsibilities}</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="no-profiles">No existing CV versions found.</p>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="pill secondary" onClick={onBack}>
            Back
          </button>
          <button
            type="button"
            className="pill secondary"
            style={{ marginLeft: 'auto' }}
            onClick={onCreateNew}
          >
            + New version
          </button>
          <button
            type="button"
            className="pill"
            onClick={() => {
              if (selectedVersion) {
                onSelectVersion(selectedVersion);
              }
            }}
            disabled={!selectedVersion}
          >
            Use selected version
          </button>
        </div>
      </section>
    </div>
  );
}
