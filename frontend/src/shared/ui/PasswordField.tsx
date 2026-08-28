import { useState } from "react";
import { Box, IconButton, InputAdornment, LinearProgress, TextField, TextFieldProps, Typography } from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { evaluatePasswordStrength } from "@/shared/utils/passwordStrength";

interface PasswordFieldProps extends Omit<TextFieldProps, "type"> {
  showStrength?: boolean;
  value: string;
}

export function PasswordField({ showStrength, value, ...textFieldProps }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false);
  const strength = showStrength ? evaluatePasswordStrength(value) : null;

  return (
    <Box>
      <TextField
        {...textFieldProps}
        value={value}
        type={visible ? "text" : "password"}
        slotProps={{
          input: {
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label={visible ? "Hide password" : "Show password"}
                  onClick={() => setVisible((prev) => !prev)}
                  edge="end"
                  size="small"
                >
                  {visible ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                </IconButton>
              </InputAdornment>
            )
          }
        }}
      />
      {showStrength && value.length > 0 && strength && (
        <Box sx={{ mt: 0.5 }}>
          <LinearProgress
            variant="determinate"
            value={(strength.score / 5) * 100}
            color={strength.color}
            sx={{ height: 6, borderRadius: 3 }}
          />
          <Typography variant="caption" color="text.secondary">
            Password strength: {strength.label}
          </Typography>
        </Box>
      )}
    </Box>
  );
}