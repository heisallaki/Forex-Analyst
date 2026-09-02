import { ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import { ToastContext } from "./ToastContext";
import { Alert, AlertColor, Snackbar } from "@mui/material";

interface ToastMessage {
  id: number;
  message: string;
  severity: AlertColor;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [queue, setQueue] = useState<ToastMessage[]>([]);
  const [current, setCurrent] = useState<ToastMessage | null>(null);

  const showToast = useCallback((message: string, severity: AlertColor = "info") => {
    setQueue((prev) => [...prev, { id: Date.now() + Math.random(), message, severity }]);
  }, []);

  useEffect(() => {
    if (!current && queue.length > 0) {
      setCurrent(queue[0]);
      setQueue((prev) => prev.slice(1));
    }
  }, [current, queue]);

  const handleClose = () => {
    setCurrent(null);
  };

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Snackbar
        open={current !== null}
        autoHideDuration={4000}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        {current ? (
          <Alert onClose={handleClose} severity={current.severity} variant="filled" sx={{ borderRadius: 3 }}>
            {current.message}
          </Alert>
        ) : undefined}
      </Snackbar>
    </ToastContext.Provider>
  );
}