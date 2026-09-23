/**
 * Controlador de Speech-to-Text (STT) y deteccion de companeros (Chiclets) para Estudiante360.
 * GovLab - Universidad de la Sabana.
 */

let recognition = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

function initSTT() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recordBtn = document.getElementById("record-btn");
    const textArea = document.getElementById("texto-observacion");
    const statusLine = document.getElementById("stt-status");

    if (!recordBtn || !textArea) return;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "es-CO"; // Espanol Colombia

        recognition.onstart = () => {
            isRecording = true;
            recordBtn.classList.add("recording");
            recordBtn.innerHTML = "Detener Grabacion (Escuchando...)";
            if (statusLine) {
                statusLine.className = "status-line active";
                statusLine.innerText = "Microfono activo: Hable con naturalidad...";
            }
        };

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            textArea.value = transcript;
            buscarChiclets(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("STT Web Speech Error:", event.error);
            if (statusLine) {
                statusLine.className = "status-line";
                statusLine.innerText = "Aviso: " + event.error + ". Puede escribir manualmente o usar Whisper.";
            }
            detenerGrabacion();
        };

        recognition.onend = () => {
            detenerGrabacion();
        };

        recordBtn.onclick = () => {
            if (!isRecording) {
                try {
                    recognition.start();
                } catch (e) {
                    console.error("Error al iniciar STT:", e);
                }
            } else {
                recognition.stop();
            }
        };
    } else {
        if (statusLine) {
            statusLine.innerText = "Web Speech API no disponible en este navegador. Usando modo de grabacion Whisper.";
        }
        configurarMediaRecorder(recordBtn, textArea, statusLine);
    }
}

function detenerGrabacion() {
    isRecording = false;
    const recordBtn = document.getElementById("record-btn");
    const statusLine = document.getElementById("stt-status");
    if (recordBtn) {
        recordBtn.classList.remove("recording");
        recordBtn.innerHTML = "Dictar Observacion (Hablar)";
    }
    if (statusLine) {
        statusLine.className = "status-line";
        statusLine.innerText = "Audio capturado. Puede revisar el texto o interpretar la rubrica.";
    }
}

function configurarMediaRecorder(btn, textArea, statusLine) {
    btn.onclick = async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    const formData = new FormData();
                    formData.append("audio_file", audioBlob, "grabacion.webm");

                    if (statusLine) {
                        statusLine.className = "status-line loading";
                        statusLine.innerText = "Transcribiendo con Whisper en el servidor...";
                    }

                    try {
                        const resp = await fetch("/api/stt/transcribe", {
                            method: "POST",
                            body: formData
                        });
                        const data = await resp.json();
                        if (data.texto) {
                            textArea.value = data.texto;
                            buscarChiclets(data.texto);
                        }
                    } catch (err) {
                        console.error("Error Whisper:", err);
                    } finally {
                        if (statusLine) {
                            statusLine.className = "status-line";
                            statusLine.innerText = "Transcripcion finalizada.";
                        }
                    }
                };

                mediaRecorder.start();
                isRecording = true;
                btn.classList.add("recording");
                btn.innerHTML = "Detener Grabacion (Whisper)";
            } catch (err) {
                alert("No se pudo acceder al microfono: " + err.message);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            btn.classList.remove("recording");
            btn.innerHTML = "Dictar Observacion (Hablar)";
        }
    };
}

function buscarChiclets(texto) {
    const contenedorChiclets = document.getElementById("chiclets-container");
    const cursoIdInput = document.getElementById("current-curso-id");
    if (!contenedorChiclets || !cursoIdInput) return;

    const cursoId = cursoIdInput.value;
    if (!cursoId || texto.length < 4) {
        contenedorChiclets.innerHTML = "";
        return;
    }

    fetch(`/reportes/detectar-chiclets?curso_id=${cursoId}&texto=${encodeURIComponent(texto)}`)
        .then(res => res.text())
        .then(html => {
            contenedorChiclets.innerHTML = html;
        })
        .catch(err => console.error("Error al detectar chiclets:", err));
}

document.addEventListener("DOMContentLoaded", initSTT);
document.body.addEventListener("htmx:afterSwap", initSTT);
