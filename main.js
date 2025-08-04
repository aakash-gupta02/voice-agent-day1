async function generateAudio() {
  const text = document.getElementById("text-input").value;
  if (!text.trim()) {
    alert("Please enter some text.");
    return;
  }

  const response = await fetch("/generate-audio", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text })
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
