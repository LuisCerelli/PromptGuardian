import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Stack from '@mui/material/Stack';
import AppTheme from '../shared-theme/AppTheme';
import ColorModeSelect from '../shared-theme/ColorModeSelect';
import CardGuard from "./components/CardGuard";
import Content from './components/Content';
import ExampleResponse from "./components/ExampleResponse";
import { Box, Typography } from "@mui/material";
// eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";
import ImageLogo from "./utils/Logo.png";
import { Link } from "react-router-dom";

export default function SignInSide({ generatedPrompt, setGeneratedPrompt }, props) {
    React.useEffect(() => {
      if (generatedPrompt) {
        const utterance = new SpeechSynthesisUtterance(generatedPrompt);
        utterance.lang = "es-ES";
        utterance.rate = 1;
        window.speechSynthesis.speak(utterance);
      }
    }, [generatedPrompt]);
  
  return (
    <AppTheme {...props}>
      <Box sx={{ display: { xs: "none", md: "flex", margin: "20px" } }}>
        <Link
          to="/about"
          style={{ display: "flex", alignItems: "center" }}
        >
          <img
            src={ImageLogo}
            alt="Logo"
            style={{ width: "50px", height: "50px", cursor: "pointer" }}
          />
        </Link>
      </Box>
      <CssBaseline enableColorScheme />
      <ColorModeSelect sx={{ position: "fixed", top: "1rem", right: "1rem" }} />
      <Stack
        direction="column"
        component="main"
        sx={[
          {
            justifyContent: "center",
            height: "calc((1 - var(--template-frame-height, 0)) * 100%)",
            marginTop: "max(10px - var(--template-frame-height, 0px), 0px)",
            minHeight: "100%",
          },
          (theme) => ({
            "&::before": {
              content: '""',
              display: "block",
              position: "absolute",
              zIndex: -1,
              inset: 0,
              backgroundImage:
                "radial-gradient(ellipse at 50% 50%, hsl(210, 100%, 97%), hsl(0, 0%, 100%))",
              backgroundRepeat: "no-repeat",
              ...theme.applyStyles("dark", {
                backgroundImage:
                  "radial-gradient(at 50% 50%, hsla(210, 100%, 16%, 0.5), hsl(220, 30%, 5%))",
              }),
            },
          }),
        ]}
      >
        {"" === generatedPrompt && (
          <Stack
            direction={{ xs: "column-reverse", md: "row" }}
            sx={{
              position: "absolute",
              bottom: "5rem",
              left: { xs: "2rem", sm: "10rem", md: "20rem", lg: "25rem" },
              width: "auto",
              height: "auto",
              justifyContent: "center",
              gap: { xs: 6, sm: 12 },
              p: 2,
              mx: "auto",
            }}
          >
            <ExampleResponse
              sx={{
                pointerEvents: "none",
              }}
            />
          </Stack>
        )}

        <Stack
          direction={{ xs: "column-reverse", md: "row" }}
          sx={{
            justifyContent: "center",
            gap: { xs: 6, sm: 12 },
            p: 2,
            mx: "auto",
          }}
        >
          <Stack
            direction={{ xs: "column-reverse", md: "column" }}
            sx={{
              justifyContent: "center",
              gap: { xs: 6, sm: 12 },
              p: { xs: 2, sm: 4 },
              m: "auto",
            }}
          >
            <Content />
            {generatedPrompt && (
              <Stack direction="column" alignItems="center">
                <motion.div
                  className="p-4 bg-blue-500 rounded-xl text-white text-center shadow-lg"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <Typography variant="h6">Sugerencias:</Typography>
                  <Typography variant="body1" component="pre">
                    {generatedPrompt}
                  </Typography>
                </motion.div>
              </Stack>
            )}
            <CardGuard setGeneratedPrompt={setGeneratedPrompt} />
          </Stack>
        </Stack>
      </Stack>
    </AppTheme>
  );
}
