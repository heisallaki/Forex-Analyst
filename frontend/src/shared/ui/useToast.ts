import { useContext } from "react";
import { ToastContext, ToastContextValue } from "@/shared/ui/ToastProvider";

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}