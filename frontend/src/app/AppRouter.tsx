import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";
import { ProtectedRoute } from "@/app/routes/ProtectedRoute";
import { AppLayout } from "@/app/layout/AppLayout";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { MarketsPage } from "@/features/market/pages/MarketsPage";
import { ChartsPage } from "@/features/charts/pages/ChartsPage";
import { AIAnalysisPage } from "@/features/ai/pages/AIAnalysisPage";
import { SignalsPage } from "@/features/signals/pages/SignalsPage";
import { StrategiesPage } from "@/features/strategies/pages/StrategiesPage";
import { BacktestPage } from "@/features/backtest/pages/BacktestPage";
import { PaperTradingPage } from "@/features/paper/pages/PaperTradingPage";
import { AnalyticsPage } from "@/features/analytics/pages/AnalyticsPage";
import { SettingsPage } from "@/features/settings/pages/SettingsPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/markets" element={<MarketsPage />} />
            <Route path="/charts" element={<ChartsPage />} />
            <Route path="/ai" element={<AIAnalysisPage />} />
            <Route path="/signals" element={<SignalsPage />} />
            <Route path="/strategies" element={<StrategiesPage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/paper" element={<PaperTradingPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}