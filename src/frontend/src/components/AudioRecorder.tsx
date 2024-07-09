import React, { useState, useEffect } from "react";
import { Button, CircularProgress } from "@mui/material";
import API_URL from "../config/config";

const AudioRecorder: React.FC<{ doRefresh: () => void }> = ({ doRefresh }) => {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    // Cleanup media recorder on component unmount
    return () => {
      if (mediaRecorder) {
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [mediaRecorder]);

  const startRecording = () => {
    setAudioChunks([]);
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const recorder = new MediaRecorder(stream);
        recorder.ondataavailable = (e) => {
          setAudioChunks(prev => [...prev, e.data]);
        };
        recorder.start();
        setMediaRecorder(recorder);
        setRecording(true);
        setTimeout(() => {
          if (recorder.state === 'recording') {
            recorder.stop();
            setRecording(false);
          }
        }, 15000); // stop recording after 15 seconds
      })
      .catch(err => console.error('Error accessing microphone:', err));
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      setRecording(false);
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleUpload = async () => {
    if (audioChunks.length > 0) {
      const blob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
      const token = localStorage.getItem("accessToken") || undefined;
      const username = localStorage.getItem("username") || "unknownUser"; // Fetch username or use a default

      setIsUploading(true); // Set uploading state to true

      try {
        const formData = new FormData();

        // add data to formData
        formData.append('file', blob, `user${username}.webm`)

        const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'app-version': '1.2.0' // Ensure app version is sent with requests
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload file');
        }

        console.log("File uploaded successfully");
        setAudioChunks([]); // Clear audioChunks after successful upload
        doRefresh(); // Refresh user data after successful upload
      } catch (error) {
        console.error("Failed to upload audio", error);
        // Handle specific error cases here
      } finally {
        setIsUploading(false); // Reset uploading state
      }
    }
  };

  return (
    <div>
      {recording ? (
        <Button variant="contained" color="secondary" onClick={stopRecording}>Stop Recording</Button>
      ) : (
        <Button variant="contained" color="primary" onClick={startRecording}>Record (New) Motto</Button>
      )}
      {audioChunks.length > 0 && (
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={isUploading} // Disable button during upload
        >
          {isUploading ? <CircularProgress size={24} /> : "Upload Recording"}
        </Button>
      )}
    </div>
  );
};

export default AudioRecorder;
