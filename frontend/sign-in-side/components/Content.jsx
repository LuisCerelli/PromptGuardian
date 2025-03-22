import * as React from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import AutoFixHighRoundedIcon from '@mui/icons-material/AutoFixHighRounded';
import ConstructionRoundedIcon from '@mui/icons-material/ConstructionRounded';
import SettingsSuggestRoundedIcon from '@mui/icons-material/SettingsSuggestRounded';
import ThumbUpAltRoundedIcon from '@mui/icons-material/ThumbUpAltRounded';
import { SitemarkIcon } from './CustomIcons';

const items = [
  {
    icon: <SettingsSuggestRoundedIcon sx={{ color: "text.secondary" }} />,
    title: "Intelligent prompt optimization",
    description:
      "The application refines your instructions to ensure the AI receives clear and structured prompts, achieving precise and consistent responses.",
  },
  {
    icon: <ConstructionRoundedIcon sx={{ color: "text.secondary" }} />,
    title: "Reliable performance",
    description:
      "By providing optimized prompts, ambiguity is minimized, helping the AI deliver accurate results with fewer misunderstandings.",
  },
  {
    icon: <ThumbUpAltRoundedIcon sx={{ color: "text.secondary" }} />,
    title: "Seamless user experience",
    description:
      "Its intuitive design simplifies the creation of effective prompts, reducing the effort needed to obtain desired outcomes.",
  },
  {
    icon: <AutoFixHighRoundedIcon sx={{ color: "text.secondary" }} />,
    title: "Enhanced accuracy",
    description:
      "With advanced algorithms, it generates prompts that align with your objectives, ensuring the AI responds exactly as intended.",
  },
];


export default function Content() {
  return (
    <Stack
      sx={{
        flexDirection: "row",
        alignSelf: "center",
        gap: 1,
        maxWidth: 1250,
      }}
    >
      {items.map((item, index) => (
        <Stack key={index} direction="row" sx={{ gap: 2 }}>
          {item.icon}
          <div>
            <Typography gutterBottom sx={{ fontWeight: "medium" }}>
              {item.title}
            </Typography>
            <Typography variant="caption" sx={{ color: "text.secondary" }}>
              {item.description}
            </Typography>
          </div>
        </Stack>
      ))}
    </Stack>
  );
}