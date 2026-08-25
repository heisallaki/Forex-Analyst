import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";
import { ProtectedRoute } from "@/app/routes/ProtectedRoute";
import { AppLayout } from "@/app/layout/AppLayout";
import { HealthCheck } from "@/features/health/HealthCheck";
import { MarketsPage } from "@/features/market/pages/MarketsPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<HealthCheck />} />
            <Route path="/markets" element={<MarketsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}