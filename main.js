let mediaRecorder;
let recordedChunks = [];

const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const statusText = document.getElementById("upload-status");

startBtn.addEventListener("click", async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Your browser does not support audio recording.");
    return;
  }

  console.log("🎙️ Starting audio recording...");

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  recordedChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(recordedChunks, { type: "audio/webm" });
    const audioURL = URL.createObjectURL(audioBlob);

    const recordingResult = document.getElementById("recording-result");
    recordingResult.innerHTML = `
      <p>🎧 Here's your Echo:</p>
      <audio controls src="${audioURL}" autoplay></audio>
    `;

    statusText.textContent = "⏳ Uploading & transcribing...";
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");

    try {
      const response = await fetch("/upload-audio", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("✅ Upload successful:", result);
      statusText.textContent = `✅ Uploaded: ${result.filename}`;

      // Transcription call
      const transcribeForm = new FormData();
      transcribeForm.append("file", audioBlob, "recording.webm");

      const transcribeRes = await fetch("/transcribe/file", {
        method: "POST",
        body: transcribeForm,
      });

      const transcription = await transcribeRes.json();
      const transcriptionBox = document.getElementById("transcription-result");

      console.log("Transcription Result:", transcription.transcript);

      transcriptionBox.innerHTML = `<p>📝 Transcription:</p><p>${transcription}</p>`;
    } catch (error) {
      statusText.textContent = "❌ Upload/Transcription failed.";
      console.error("Error:", error);
    }
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
  statusText.textContent = "🎙️ Recording...";
});

stopBtn.addEventListener("click", () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    alert("No recording in progress.");
    return;
  }

  console.log("🛑 Stopping audio recording...");
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
});

async function generateAudio() {
  const text = document.getElementById("text-input").value;
  if (!text.trim()) {
    alert("Please enter some text.");
    return;
  }

  const response = await fetch("/generate-audio", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  const data = await response.json();

  if (data.audio_url) {
    const audioContainer = document.getElementById("audio-container");
    audioContainer.innerHTML = `
      <p>🔊 Generated audio:</p>
      <audio controls src="${data.audio_url}" autoplay></audio>
    `;
  } else {
    alert("Error generating audio. Check console.");
    console.error(data);
  }
}
