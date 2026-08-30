import { Suspense, lazy } from "react";
import type { ReactElement } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/app/routes/ProtectedRoute";
import { AppLayout } from "@/app/layout/AppLayout";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";

const LoginPage = lazy(() => import("@/features/auth/pages/LoginPage").then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() =>
  import("@/features/auth/pages/RegisterPage").then((m) => ({ default: m.RegisterPage }))
);
const ForgotPasswordPage = lazy(() =>
  import("@/features/auth/pages/ForgotPasswordPage").then((m) => ({ default: m.ForgotPasswordPage }))
);
const DashboardPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardPage").then((m) => ({ default: m.DashboardPage }))
);
const MarketsPage = lazy(() =>
  import("@/features/market/pages/MarketsPage").then((m) => ({ default: m.MarketsPage }))
);
const ChartsPage = lazy(() =>
  import("@/features/charts/pages/ChartsPage").then((m) => ({ default: m.ChartsPage }))
);
const AIAnalysisPage = lazy(() =>
  import("@/features/ai/pages/AIAnalysisPage").then((m) => ({ default: m.AIAnalysisPage }))
);
const SignalsPage = lazy(() =>
  import("@/features/signals/pages/SignalsPage").then((m) => ({ default: m.SignalsPage }))
);
const StrategiesPage = lazy(() =>
  import("@/features/strategies/pages/StrategiesPage").then((m) => ({ default: m.StrategiesPage }))
);
const BacktestPage = lazy(() =>
  import("@/features/backtest/pages/BacktestPage").then((m) => ({ default: m.BacktestPage }))
);
const PaperTradingPage = lazy(() =>
  import("@/features/paper/pages/PaperTradingPage").then((m) => ({ default: m.PaperTradingPage }))
);
const AnalyticsPage = lazy(() =>
  import("@/features/analytics/pages/AnalyticsPage").then((m) => ({ default: m.AnalyticsPage }))
);
const SettingsPage = lazy(() =>
  import("@/features/settings/pages/SettingsPage").then((m) => ({ default: m.SettingsPage }))
);

function withSuspense(element: ReactElement): ReactElement {
  return <Suspense fallback={<PageLoadingSkeleton />}>{element}</Suspense>;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={withSuspense(<LoginPage />)} />
        <Route path="/register" element={withSuspense(<RegisterPage />)} />
        <Route path="/forgot-password" element={withSuspense(<ForgotPasswordPage />)} />
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