import * as React from "react";
import {
  Box,
  Button,
  FormLabel,
  TextField,
  FormControl,
  Typography,
  CircularProgress,
} from "@mui/material";
import MuiCard from "@mui/material/Card";
import { styled } from "@mui/material/styles";
//eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";
import { Mic } from "@mui/icons-material";
const API_URL = import.meta.env.VITE_API_URL;
const API_URL_AUDIO = import.meta.env.VITE_API_URL_AUDIO;

const Card = styled(MuiCard)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignSelf: "center",
  width: "100%",
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  boxShadow:
    "hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px",
  [theme.breakpoints.up("sm")]: {
    width: "750px",
  },
}));

export default function CardGuard({ setGeneratedPrompt }) {
  const [userInput, setUserInput] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [isRecording, setIsRecording] = React.useState(false);
  const [isProcessingAudio, setIsProcessingAudio] = React.useState(false);
  const [audioURL, setAudioURL] = React.useState(null);
  const mediaRecorderRef = React.useRef(null);
  const recordingTimeoutRef = React.useRef(null);
  const audioChunksRef = React.useRef([]);
  const recognitionRef = React.useRef(null);

  const handleGeneratePrompt = async () => {
    if (!userInput.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userInput.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Error en la API: ${response.statusText}`);
      }

      const data = await response.json();

      const formattedResponse =
        data.sanitized_prompt || "No hay respuesta disponible.";

      setGeneratedPrompt(formattedResponse);
      setUserInput(" ");
    } catch (error) {
      console.error("Error al procesar el prompt:", error);
      setGeneratedPrompt("Hubo un problema al generar la respuesta.");
    } finally {
      setIsLoading(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      setIsProcessingAudio(true);
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      setTimeout(() => {
        setGeneratedPrompt("Prompt optimizado desde audio");
        setIsProcessingAudio(false);
      }, 2000);
    }
  };

  const handleAudioRecording = async () => {
    if (isRecording) {
      clearTimeout(recordingTimeoutRef.current);
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        setTimeout(() => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/wav",
          });
          const audioUrl = URL.createObjectURL(audioBlob);
          setAudioURL(audioUrl);
          setIsProcessingAudio(false);
        }, 2000);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsProcessingAudio(false);

      recordingTimeoutRef.current = setTimeout(stopRecording, 10000);
    } catch (error) {
      console.error("Error al acceder al micrófono:", error);
    }
  };

  const handleVoiceRecognition = () => {
    if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
      alert("Tu navegador no soporta la API de reconocimiento de voz.");
      return;
    }

    recognitionRef.current = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognitionRef.current.lang = "es-ES";
    recognitionRef.current.interimResults = false;
    recognitionRef.current.continuous = false;

    recognitionRef.current.onstart = () => {
      setIsRecording(true);
    };

    recognitionRef.current.onspeechend = () => {
      setIsRecording(false);
      recognitionRef.current.stop();
    };

    recognitionRef.current.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;

      try {
        const response = await fetch(API_URL_AUDIO, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: transcript }),
        });

        const data = await response.json();
        const textoCorregido = data.sanitized_prompt || transcript;
        // processed_prompt;
        setGeneratedPrompt(textoCorregido);
      } catch (error) {
        console.error("Error:", error);
        setGeneratedPrompt("Hubo un problema al procesar el audio.");
      }
    };

    recognitionRef.current.onerror = (event) => {
      console.error("Error de reconocimiento:", event.error);
      setGeneratedPrompt("Error al reconocer voz");
    };

    recognitionRef.current.start();
  };

  return (
    <Card variant="outlined" width="100%">
      <Typography
        component="h5"
        variant="h6"
        sx={{ width: "100%", fontSize: "clamp(1.5rem, 10vw, 0.15rem)" }}
      >
        Don't know what to ask? Let me help you.
      </Typography>

      <Box
        component="form"
        noValidate
        sx={{ display: "flex", flexDirection: "row", width: "100%", gap: 2 }}
      >
        <TextField
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Describe tu idea aquí..."
          variant="outlined"
          fullWidth
          margin="normal"
          disabled={isRecording}
        />

        <Button
          onClick={handleGeneratePrompt}
          variant="contained"
          color="primary"
          disabled={isLoading || !userInput.trim() || isRecording}
          sx={{
            marginTop: "1rem",
            color: "#ffffff",
            backgroundColor:
              isLoading || !userInput.trim() || isRecording
                ? "#757575"
                : "#1976d2",
            "&.Mui-disabled": { color: "#B0BEC5" },
          }}
        >
          {isLoading ? <CircularProgress size={24} /> : "Send"}
        </Button>

        <Button
          onClick={handleVoiceRecognition}
          variant="contained"
          color={isRecording || isProcessingAudio ? "error" : "primary"}
          sx={{ marginTop: "1rem", "&.Mui-disabled": { color: "#B0BEC5" } }}
          disabled={!!userInput.trim()}
        >
          {isProcessingAudio ? (
            <CircularProgress size={24} color="inherit" />
          ) : isRecording ? (
            "Stop"
          ) : (
            <Mic />
          )}
        </Button>
      </Box>
      {audioURL && (
        <Box sx={{ marginTop: 2 }}>
          <audio controls>
            <source src={audioURL} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
        </Box>
      )}
    </Card>
  );
}


