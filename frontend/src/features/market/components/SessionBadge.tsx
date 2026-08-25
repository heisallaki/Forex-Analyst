import { Chip, Stack } from "@mui/material";

interface SessionBadgeProps {
  activeSessions: string[];
}

export function SessionBadge({ activeSessions }: SessionBadgeProps) {
  return (
    <Stack direction="row" spacing={1}>
      {activeSessions.map((session) => (
        <Chip key={session} label={session} color="primary" variant="outlined" />
      ))}
    </Stack>
  );
}