import { createContext, useContext } from "react";
import type { AlertColor } from "@mui/material/Alert";

export interface ToastContextValue {
  showToast: (message: string, severity?: AlertColor) => void;
}

export const ToastContext =
  createContext<ToastContextValue | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }

  return context;
}