import * as React from "react";
import {
  Box,
  Typography,
} from "@mui/material";
import MuiCard from "@mui/material/Card";
import { styled } from "@mui/material/styles";
// eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";
import { useTheme } from "@mui/material/styles";
import { examples } from "../utils/objects";

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
    width: "450px",
  },
}));


export default function ExampleResponse() {
  const [userInput, setUserInput] = React.useState("");
  const [displayedResponse, setDisplayedResponse] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [textColor, setTextColor] = React.useState("black");
  const [exampleIndex, setExampleIndex] = React.useState(0);

  const theme = useTheme();

  React.useEffect(() => {
    setTextColor(theme.palette.mode === "dark" ? "white" : "black");
  }, [theme.palette.mode]);



  React.useEffect(() => {
    const interval = setInterval(() => {
      setExampleIndex((prevIndex) => {
        if (prevIndex === examples.length - 1) {
          return 0;
        }
        return prevIndex + 1;
      });
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  React.useEffect(() => {
    let index = 0;
    setUserInput("");
    const interval = setInterval(() => {
      if (index < examples[exampleIndex].wrong.length) {
        let wrong = examples[exampleIndex].wrong[index];
        setUserInput((prev) => prev + wrong);
        index++;
      } else {
        clearInterval(interval);
        handleGeneratePrompt();
      }
    }, 60);

    return () => clearInterval(interval);
  }, [exampleIndex]);

  const handleGeneratePrompt = () => {
    setIsLoading(true);
    setDisplayedResponse("");

    let index = 0;
    const interval = setInterval(() => {
      if (index < examples[exampleIndex].suggestion.length) {
        let suggestion = examples[exampleIndex].suggestion[index];
        setDisplayedResponse((prev) => prev + suggestion);
        index++;
      } else {
        setIsLoading(false);
        clearInterval(interval);
      }
    }, 40);
  };

  return (
    <Box>
      <Box
        component="form"
        noValidate
        sx={{ display: "flex", flexDirection: "column", width: "100%", gap: 2 }}
      >
        <Typography
          sx={{
            color: textColor,
            opacity: 0.5,
            userSelect: "none",
            fontSize: "0.8rem",
          }}
        >
          {userInput || "Generando prompt..."}
        </Typography>
      </Box>

      {displayedResponse && (
        <motion.div
          className="mt-4 p-4 bg-green-500 rounded-xl shadow-lg text-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Typography
            sx={{
              color: textColor,
              opacity: 0.5,
              userSelect: "none",
              fontSize: "0.8rem",
            }}
            variant="body1"
          >
            {displayedResponse}
          </Typography>
        </motion.div>
      )}
    </Box>
  );
}

