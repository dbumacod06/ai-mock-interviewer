import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ApplicantModal from './ApplicantModal';
import ApplicantConfirmationModal from './ApplicantConfirmationModal';
import CvModal from './CvModal';
import CvVersionSelection from './CvVersionSelection';
import JobProfileModal from './JobProfileModal';
import SessionSelection from './SessionSelection';
import InterviewReviewModal from './InterviewReviewModal';

const initialApplicantDetails = {
  firstName: '',
  lastName: '',
  preferredName: '',
};

const normalizeApplicant = (applicant, applicantId) => ({
  applicantId: applicant.applicantId || applicant.applicant_id || applicantId,
  firstName: applicant.firstName || applicant.first_name || '',
  lastName: applicant.lastName || applicant.last_name || '',
  preferredName: applicant.preferredName || applicant.preferred_name || '',
  currentRole: applicant.currentRole || applicant.current_role || '',
  currentCompany: applicant.currentCompany || applicant.current_company || '',
  previousCompanies: applicant.previousCompanies || applicant.previous_companies || '',
});

export default function App() {
  const [status, setStatus] = useState('Loading...');
  const [activeModal, setActiveModal] = useState('applicant');
  const [applicantDetails, setApplicantDetails] = useState(null);
  const [isApplicantLoading, setIsApplicantLoading] = useState(false);
  const [isBatchSaving, setIsBatchSaving] = useState(false);
  const [cvData, setCvData] = useState(null);
  const [jobProfiles, setJobProfiles] = useState([]);
  const [jobProfilePreviousModal, setJobProfilePreviousModal] = useState('sessionSelection');
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [assistantResponse, setAssistantResponse] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');
  const [messages, setMessages] = useState([]);
  const [interviewPhase, setInterviewPhase] = useState('');
  const [confirmationApplicantId, setConfirmationApplicantId] = useState(null);
  const [showReviewModal, setShowReviewModal] = useState(false);

  // Pending data for batch save
  const [pendingApplicantData, setPendingApplicantData] = useState(null);
  const [pendingCvData, setPendingCvData] = useState(null);
  const [pendingJobProfileData, setPendingJobProfileData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedCvVersion, setSelectedCvVersion] = useState(null);
  const [selectedJobProfileId, setSelectedJobProfileId] = useState(null);
  const [cvVersions, setCvVersions] = useState([]);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const conversationRef = useRef(null);

  useEffect(() => {
    fetch('/api/status')
      .then((res) => res.json())
      .then((data) => setStatus(`Connected: ${data.mode}`))
      .catch(() => setStatus('Backend not running yet'));
  }, []);

  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTo({
        top: conversationRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [transcript, assistantResponse, error, messages]);

  const openApplicantModal = (editMode = false) => {
    setIsEditing(editMode);
    if (editMode) {
      setSessionId('');
    }
    if (editMode && applicantDetails) {
      setPendingApplicantData(applicantDetails);
      setPendingCvData(cvData);
      setPendingJobProfileData(jobProfiles);
    } else {
      setPendingApplicantData(null);
      setPendingCvData(null);
      setPendingJobProfileData(null);
    }
    setActiveModal('applicant');
    setError('');
  };

  const handleCreateNewApplicant = () => {
    setApplicantDetails(null);
    setCvData(null);
    setJobProfiles([]);
    setPendingApplicantData(null);
    setPendingCvData(null);
    setPendingJobProfileData(null);
    setIsEditing(false);
    setSessionId('');
    setSelectedCvVersion(null);
    setSelectedJobProfileId(null);
    setCvVersions([]);
    setMessages([]);
    setInterviewPhase('');
  };

  const submitApplicantStep = async (applicantForm) => {
    const normalizedApplicant = {
      firstName: applicantForm.first_name.trim(),
      lastName: applicantForm.last_name.trim(),
      preferredName: applicantForm.preferred_name.trim(),
    };
    setPendingApplicantData(normalizedApplicant);

    // Fetch CV versions for the applicant
    if (applicantDetails?.applicantId) {
      try {
        const response = await fetch(
          `/api/applicant-cv/${encodeURIComponent(applicantDetails.applicantId)}/versions`
        );
        if (response.ok) {
          const data = await response.json();
          setCvVersions(data);
        }
      } catch {
        setCvVersions([]);
      }
    } else {
      setCvVersions([]);
    }

    setActiveModal('cv');
  };

  const submitCvStep = (cvForm) => {
    const cvPayload = {
      currentRole: cvForm.current_role || cvForm.currentRole || '',
      currentCompany: cvForm.current_company || cvForm.currentCompany || '',
      currentResponsibilities: cvForm.current_responsibilities || cvForm.currentResponsibilities || '',
      pastRoles: cvForm.past_roles || cvForm.pastRoles || [],
      version: cvForm.version,
    };
    setPendingCvData(cvPayload);
    saveApplicantAndCv(cvPayload);
  };

  const saveApplicantAndCv = async (cvPayload) => {
    if (!pendingApplicantData) {
      return;
    }

    setIsBatchSaving(true);
    setError('');

    try {
      let applicantId = applicantDetails?.applicantId;
      let applicantResult;

      // Step 1: Save applicant details
      if (isEditing && applicantId) {
        const response = await fetch(`/api/applicants/${encodeURIComponent(applicantId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            first_name: pendingApplicantData.firstName,
            last_name: pendingApplicantData.lastName,
            preferred_name: pendingApplicantData.preferredName,
          }),
        });
        applicantResult = await response.json();
        if (!response.ok) {
          throw new Error(applicantResult.detail || 'Applicant details could not be updated.');
        }
      } else {
        const response = await fetch('/api/applicants', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            first_name: pendingApplicantData.firstName,
            last_name: pendingApplicantData.lastName,
            preferred_name: pendingApplicantData.preferredName,
          }),
        });
        applicantResult = await response.json();
        if (!response.ok) {
          throw new Error(applicantResult.detail || 'Applicant details could not be saved.');
        }
        applicantId = applicantResult.applicant_id;
      }

      setApplicantDetails(normalizeApplicant(applicantResult.applicant, applicantId));
      setSessionId('');

      // Step 2: Save CV (only if it's a new CV without an existing version)
      if (cvPayload && !cvPayload.version) {
        const cvResponse = await fetch('/api/applicant-cv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            applicant_id: applicantId,
            current_role: cvPayload.currentRole,
            current_company: cvPayload.currentCompany,
            current_responsibilities: cvPayload.currentResponsibilities,
            past_roles: cvPayload.pastRoles,
          }),
        });
        const cvResult = await cvResponse.json();
        if (!cvResponse.ok) {
          throw new Error(cvResult.detail || 'CV could not be saved.');
        }
        setCvData(cvResult.cv);
        setSelectedCvVersion(cvResult.cv?.version || 1);
      } else if (cvPayload?.version) {
        // CV already exists, just set the version
        setCvData(cvPayload);
        setSelectedCvVersion(cvPayload.version);
      }

      // Step 3: Update applicant with CV fields
      const previousCompanies = cvPayload?.pastRoles
        ?.map((role) => role.company)
        .filter(Boolean)
        .join(', ') || '';
      
      const applicantUpdateResponse = await fetch(
        `/api/applicants/${encodeURIComponent(applicantId)}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_role: cvPayload?.currentRole || '',
            current_company: cvPayload?.currentCompany || '',
            previous_companies: previousCompanies,
          }),
        }
      );
      const applicantUpdateResult = await applicantUpdateResponse.json();
      if (!applicantUpdateResponse.ok) {
        throw new Error(applicantUpdateResult.detail || 'Failed to update applicant with CV fields.');
      }
      setApplicantDetails((current) => ({
        ...current,
        currentRole: applicantUpdateResult.applicant?.currentRole || cvPayload?.currentRole || '',
        currentCompany: applicantUpdateResult.applicant?.currentCompany || cvPayload?.currentCompany || '',
        previousCompanies: applicantUpdateResult.applicant?.previousCompanies || previousCompanies,
      }));

      // Step 4: For new applicants, show confirmation with applicant ID, then go to job profile creation.
      // For existing applicants starting a new session, go to job profile.
      if (isEditing) {
        setJobProfilePreviousModal('cv');
        setActiveModal('jobProfile');
      } else {
        setJobProfilePreviousModal('applicant');
        setActiveModal(null);
        setConfirmationApplicantId(applicantId);
      }
      setStatus(`Applicant profile saved: ${applicantId}`);
    } catch (err) {
      setError(err.message || 'Something went wrong while saving the profile.');
      setStatus('Profile save failed');
    } finally {
      setIsBatchSaving(false);
    }
  };

  const saveJobProfileAndCreateSession = async (profileData) => {
    if (!profileData || !applicantDetails?.applicantId) {
      return;
    }

    setIsBatchSaving(true);
    setError('');

    try {
      const applicantId = applicantDetails.applicantId;
      let jobProfileId;

      // Step 1: Save or update job profile
      if (profileData.profileId) {
        const updateResponse = await fetch(
          `/api/applicant-job-profiles/${encodeURIComponent(profileData.profileId)}`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              job_title: profileData.job_title,
              company: profileData.company,
              job_description: profileData.job_description,
              company_vision: profileData.company_vision,
              company_mission: profileData.company_mission,
              additional_context: profileData.additional_context,
            }),
          }
        );
        const updateResult = await updateResponse.json();
        if (!updateResponse.ok) {
          throw new Error(updateResult.detail || 'Job profile could not be updated.');
        }
        jobProfileId = profileData.profileId;
        setJobProfiles((current) =>
          current.map((p) =>
            (p.profileId || p.id) === profileData.profileId ? updateResult.profile : p
          )
        );
      } else {
        const jobProfileResponse = await fetch('/api/applicant-job-profiles', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            applicant_id: applicantId,
            job_title: profileData.job_title,
            company: profileData.company,
            job_description: profileData.job_description,
            company_vision: profileData.company_vision,
            company_mission: profileData.company_mission,
            additional_context: profileData.additional_context,
          }),
        });
        const jobProfileResult = await jobProfileResponse.json();
        if (!jobProfileResponse.ok) {
          throw new Error(jobProfileResult.detail || 'Job profile could not be saved.');
        }
        jobProfileId = jobProfileResult.profile?.profileId || '';
        setJobProfiles((current) => [...current, jobProfileResult.profile]);
      }
      setSelectedJobProfileId(jobProfileId);

      // Step 2: Create session
      const sessionResponse = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          applicant_id: applicantId,
          cv_version: selectedCvVersion,
          job_profile_id: jobProfileId,
        }),
      });
      const sessionResult = await sessionResponse.json();
      if (!sessionResponse.ok) {
        throw new Error(sessionResult.detail || 'Failed to create session.');
      }
      setSessionId(sessionResult.session_id);
      await fetchConversationHistory(sessionResult.session_id);

      setActiveModal(null);
      setStatus(`Session created: ${sessionResult.session_id}`);
    } catch (err) {
      setError(err.message || 'Something went wrong while saving the job profile.');
      setStatus('Job profile save failed');
    } finally {
      setIsBatchSaving(false);
    }
  };

  const findApplicantDetails = async (applicantId) => {
    if (!applicantId) {
      return;
    }

    setIsApplicantLoading(true);
    setError('');
    setStatus('Finding applicant record...');

    try {
      const response = await fetch(`/api/applicants/${encodeURIComponent(applicantId)}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Applicant record could not be found.');
      }

      const applicant = normalizeApplicant(data.applicant, data.applicant_id);
      setApplicantDetails(applicant);
      setPendingApplicantData(applicant);
      setIsEditing(true);
      setSessionId('');

      // Fetch CV versions
      try {
        const cvResponse = await fetch(
          `/api/applicant-cv/${encodeURIComponent(data.applicant_id)}/versions`
        );
        if (cvResponse.ok) {
          const cvData = await cvResponse.json();
          setCvVersions(cvData);
        }
      } catch {
        setCvVersions([]);
      }

      await fetchApplicantJobProfiles(data.applicant_id);

      setActiveModal('sessionSelection');
      setStatus(`Applicant loaded: ${data.applicant_id}`);
    } catch (err) {
      setError(err.message || 'Something went wrong while loading the applicant profile.');
      setStatus('Applicant lookup failed');
    } finally {
      setIsApplicantLoading(false);
    }
  };

  const fetchApplicantCv = async (applicantId) => {
    try {
      const response = await fetch(`/api/applicant-cv/${encodeURIComponent(applicantId)}`);
      if (response.ok) {
        const data = await response.json();
        setCvData(data.cv);
        setPendingCvData(data.cv);
      }
    } catch {
      setCvData(null);
      setPendingCvData(null);
    }
  };

  const fetchConversationHistory = async (sid) => {
    if (!sid) return;
    try {
      const res = await fetch(`/api/conversations/${encodeURIComponent(sid)}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
        setInterviewPhase(data.interview_phase || '');
      }
    } catch {
      setMessages([]);
      setInterviewPhase('');
    }
  };

  const fetchApplicantJobProfiles = async (applicantId) => {
    try {
      const response = await fetch(
        `/api/applicant-job-profiles/${encodeURIComponent(applicantId)}`
      );
      if (response.ok) {
        const data = await response.json();
        const profiles = data.map((item) => item.profile);
        setJobProfiles(profiles);
        setPendingJobProfileData(profiles);
      }
    } catch {
      setJobProfiles([]);
      setPendingJobProfileData(null);
    }
  };

  const handleCvVersionSelect = (version) => {
    setSelectedCvVersion(version);
    const selectedVersionData = cvVersions.find((v) => v.cv?.version === version);
    if (selectedVersionData) {
      setPendingCvData(selectedVersionData.cv);
      setCvData(selectedVersionData.cv);
      saveApplicantAndCv(selectedVersionData.cv);
    }
  };

  const handleCreateNewCvVersion = () => {
    const latestVersion = cvVersions[0]?.cv;
    if (latestVersion) {
      setPendingCvData(latestVersion);
    }
    setActiveModal('cv');
  };

  const handleCvVersionBack = () => {
    setActiveModal('applicant');
  };

  const handleContinueSession = (sessionId) => {
    setSessionId(sessionId);
    setActiveModal(null);
    fetchConversationHistory(sessionId);
  };

  const handleStartNewSession = () => {
    setActiveModal('cv');
  };

  const handleConfirmationProceed = () => {
    setConfirmationApplicantId(null);
    setActiveModal('jobProfile');
  };

  const startRecording = async () => {
    setError('');
    setTranscript('');
    setAssistantResponse('');

    if (!navigator.mediaDevices?.getUserMedia) {
      setError('This browser does not support microphone recording.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      const detectSpeaking = () => {
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        setIsSpeaking(average > 18);
        animationFrameRef.current = window.requestAnimationFrame(detectSpeaking);
      };

      detectSpeaking();

      const preferredMimeTypes = [
        'audio/mpeg',
        'audio/mp3',
        'audio/mp4',
        'audio/webm;codecs=opus',
      ];
      const mimeType = preferredMimeTypes.find((type) => MediaRecorder.isTypeSupported(type)) || undefined;

      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        setStatus('Preparing recording for transcription...');
        const rawBlob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        const extension = rawBlob.type.includes('mpeg') || rawBlob.type.includes('mp3') ? '.mp3'
          : rawBlob.type.includes('mp4') ? '.m4a'
          : '.webm';
        const audioFile = new File([rawBlob], `recording-${Date.now()}${extension}`, {
          type: rawBlob.type || 'audio/webm',
        });

        try {
          const formData = new FormData();
          formData.append('applicant_id', applicantDetails?.applicantId || '');
          if (sessionId) {
            formData.append('session_id', sessionId);
          }
          formData.append('file', audioFile, audioFile.name);

          setStatus('Transcribing recording...');
          const response = await fetch('/api/transcribe', {
            method: 'POST',
            body: formData,
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.detail || 'Transcription failed.');
          }

          setTranscript(data.transcribed_text || data.text || '');
          setAssistantResponse(data.model_response || '');
          setSessionId(data.session_id || '');
          setMessages((prev) => [
            ...prev,
            { role: 'user', content: data.corrected_text || data.transcribed_text || '' },
            { role: 'assistant', content: data.model_response || '' },
          ]);
          setInterviewPhase(data.interview_phase || '');
          setTranscript('');
          setAssistantResponse('');
          setStatus(`Saved ${data.filename} and ready for the next recording`);
        } catch (err) {
          setError(err.message || 'Something went wrong while transcribing.');
          setStatus('Recording failed');
        } finally {
          stream.getTracks().forEach((track) => track.stop());
          if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
          }
          if (audioContextRef.current) {
            audioContextRef.current.close().catch(() => undefined);
            audioContextRef.current = null;
          }
          analyserRef.current = null;
          setIsSpeaking(false);
          setIsRecording(false);
        }
      };

      recorder.start();
      setIsRecording(true);
      setStatus('Recording from your microphone...');
    } catch (err) {
      setError(err.message || 'Microphone access was denied.');
      setStatus('Microphone unavailable');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      setStatus('Stopping recording...');
      setIsRecording(false);
      setIsSpeaking(false);
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <main className="app-shell">
      {activeModal === 'applicant' ? (
        <ApplicantModal
          applicantDetails={pendingApplicantData || initialApplicantDetails}
          isLoadingApplicant={isApplicantLoading}
          isEditing={isEditing}
          onFindApplicant={findApplicantDetails}
          onNext={submitApplicantStep}
          onCreateNew={handleCreateNewApplicant}
        />
      ) : null}

      {activeModal === 'cvVersionSelection' && applicantDetails?.applicantId ? (
        <CvVersionSelection
          existingVersions={cvVersions}
          onSelectVersion={handleCvVersionSelect}
          onCreateNew={handleCreateNewCvVersion}
          onBack={handleCvVersionBack}
        />
      ) : null}

      {activeModal === 'cv' && pendingApplicantData ? (
        <CvModal
          cvVersions={cvVersions}
          applicantId={applicantDetails?.applicantId}
          onNext={submitCvStep}
          onBack={() => {
            if (isEditing) {
              setActiveModal('sessionSelection');
            } else {
              setActiveModal('applicant');
            }
          }}
          isNewApplicant={!isEditing}
        />
      ) : null}

      {activeModal === 'jobProfile' && pendingApplicantData ? (
        <JobProfileModal
          existingProfiles={pendingJobProfileData || []}
          onBack={() => setActiveModal(jobProfilePreviousModal)}
          onSave={saveJobProfileAndCreateSession}
          isSaving={isBatchSaving}
          onResetSession={() => setSessionId('')}
          startInFormMode={!isEditing}
          isNewApplicant={!isEditing}
        />
      ) : null}

      {activeModal === 'sessionSelection' && applicantDetails?.applicantId ? (
        <SessionSelection
          applicantId={applicantDetails.applicantId}
          onContinueSession={handleContinueSession}
          onStartNewSession={handleStartNewSession}
        />
      ) : null}

      {showReviewModal && sessionId ? (
        <InterviewReviewModal
          sessionId={sessionId}
          onClose={() => setShowReviewModal(false)}
        />
      ) : null}

      {confirmationApplicantId ? (
        <ApplicantConfirmationModal
          applicantId={confirmationApplicantId}
          onProceed={handleConfirmationProceed}
        />
      ) : null}

      <aside className="sidebar">
        <h1>Interview Bot</h1>
        <p>Voice interview assistant</p>
        {applicantDetails ? (
          <section className="applicant-summary">
            <p className="summary-label">Applicant</p>
            <h3>{applicantDetails.preferredName || `${applicantDetails.firstName} ${applicantDetails.lastName}`}</h3>
          </section>
        ) : null}

        {cvData ? (
          <section className="applicant-summary cv-summary">
            <div className="summary-header">
              <div>
                <p className="summary-label">CV</p>
                <h3>{cvData.currentRole}</h3>
                <p className="summary-company">{cvData.currentCompany}</p>
              </div>
            </div>
            <p className="summary-meta">{cvData.currentResponsibilities}</p>
          </section>
        ) : null}

        {jobProfiles && jobProfiles.length > 0 ? (
          <section className="applicant-summary job-profile-summary">
            <div className="summary-header">
              <div>
                <p className="summary-label">Job Profiles</p>
              </div>
            </div>
            {jobProfiles.map((profile, index) => (
              <div className="profile-summary-item" key={profile.profileId || index}>
                <h4>{profile.jobTitle}</h4>
                <p>{profile.company}</p>
              </div>
            ))}
          </section>
        ) : null}
      </aside>

      <section className={`chat-panel ${messages.length === 0 ? 'initial' : ''}`}>
        <header className="chat-header">
          <div>
            <p className="eyebrow">Live assistant</p>
            <h2>Start and stop recording from your input device</h2>
          </div>
          <span className="chip">{status}</span>
        </header>

        <article className="conversation" ref={conversationRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`bubble ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {transcript ? <div className="bubble user">{transcript}</div> : null}
          {assistantResponse ? (
            <article className="bubble assistant response-card" aria-label="Assistant response">
              <p className="response-label">Assistant response</p>
              <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown-response">
                {assistantResponse}
              </ReactMarkdown>
            </article>
          ) : null}
          {error ? <div className="bubble user error">{error}</div> : null}
        </article>

        <footer className="composer">
          {interviewPhase !== 'done' ? (
            <button
              type="button"
              className={`mic-button ${isRecording ? 'recording' : 'idle'} ${isSpeaking ? 'speaking' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              aria-label={isRecording ? 'Stop recording' : 'Start recording'}
            >
              <svg viewBox="0 0 24 24" className="mic-icon" aria-hidden="true">
                <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm5-3a1 1 0 1 1 2 0 7 7 0 0 1-6 6.92V21h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-3.08A7 7 0 0 1 5 11a1 1 0 1 1 2 0 5 5 0 0 0 10 0Z" />
              </svg>
            </button>
          ) : (
            <button
              type="button"
              className="pill review-button"
              onClick={() => setShowReviewModal(true)}
            >
              Review Interview
            </button>
          )}
        </footer>
      </section>
    </main>
  );
}
