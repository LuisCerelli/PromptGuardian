import React from "react";
import { Box, Stack, Typography, CssBaseline, Grid } from "@mui/material";
import AppTheme from "../shared-theme/AppTheme";
import ColorModeSelect from "../shared-theme/ColorModeSelect";
import ImageLogo from "./utils/Logo.png";
import { Link } from "react-router-dom";

export default function About(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <ColorModeSelect sx={{ position: "fixed", top: "1rem", right: "1rem" }} />

      <Box sx={{ display: { xs: "none", md: "flex" }, margin: "20px" }}>
        <Link to="/" style={{ display: "flex", alignItems: "center" }}>
          <img
            src={ImageLogo}
            alt="Logo"
            style={{ width: "50px", height: "50px", cursor: "pointer" }}
          />
        </Link>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          p: 1,
          mt: -2,
        }}
      >
        <Grid
          container
          spacing={4}
          sx={{
            maxWidth: "1200px",
            margin: "auto",
            alignItems: "flex-start",
          }}
        >
          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <Typography variant="h4" gutterBottom>
                ¿Qué problema resuelve?
              </Typography>
              <Typography paragraph>
                Millones de personas en el mundo tienen dificultades para
                escribir correctamente o estructurar sus pensamientos en texto.
                Esto puede ser una barrera para acceder a información, realizar
                trámites en línea, aprender nuevas habilidades o incluso
                comunicarse con asistentes de IA.
              </Typography>
              <Typography>
                📌 Errores gramaticales y de comprensión que afectan la calidad
                de las respuestas que reciben.
                <br />
                📌 Falta de claridad en los prompts, lo que lleva a respuestas
                irrelevantes o confusas.
                <br />
                📌 Dificultades en la escritura que pueden hacer que eviten usar
                tecnologías de IA.
              </Typography>

              <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                ¿Cómo funciona?
              </Typography>
              <Typography>
                👉 Prompt Guard podría actuar como un asistente inteligente que
                mejora y adapta los prompts en tiempo real para personas con
                baja alfabetización o dificultades en la escritura.
              </Typography>
              <Typography>
                ✅ Corrección automática: Si alguien escribe "Dime cómo se va un
                docot", lo reestructura a "¿Cómo puedo llegar a un doctor?".
                <br />
                ✅ Mejor comprensión de IA: Traduce frases mal estructuradas en
                preguntas claras para obtener mejores respuestas.
                <br />
                ✅ Soporte por voz: Permite a los usuarios hablar en lugar de
                escribir, convirtiendo su voz en prompts mejorados.
                <br />✅ Modo inclusivo: Ajusta la complejidad de las respuestas
                según el nivel de comprensión del usuario.
              </Typography>
            </Stack>
          </Grid>

          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <Typography variant="h4" gutterBottom>
                ¿Cómo podría integrarse con Microsoft?
              </Typography>
              <Typography>
                🔹 Azure Speech-to-Text y Text-to-Speech para que los usuarios
                puedan interactuar por voz.
                <br />
                🔹 Microsoft Immersive Reader para ayudar en la lectura y
                comprensión de respuestas.
                <br />
                🔹 Integración con Microsoft Teams o Edge para asistencia en
                herramientas educativas.
              </Typography>

              <Typography variant="h4" gutterBottom sx={{ mt: 2 }}>
                Ejemplo de Uso
              </Typography>
              <Typography>
                Un adulto con dificultades para escribir quiere buscar
                información sobre un trámite. En lugar de escribir "ppr favor
                nesecito hacer un ID", Prompt Guard corrige y mejora su
                consulta:
                <br />
                ➡ Entrada del usuario: "nesesito sacar mi DNI pero no se como"
                <br />
                ➡ Prompt mejorado: "¿Cómo puedo tramitar mi documento de
                identidad en mi país?"
                <br />➡ Respuesta clara y útil de la IA.
              </Typography>
            </Stack>
          </Grid>
        </Grid>
      </Box>
    </AppTheme>
  );
}
