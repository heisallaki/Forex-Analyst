import { Box, Skeleton, Stack } from "@mui/material";

interface PageLoadingSkeletonProps {
  variant?: "cards" | "table";
}

export function PageLoadingSkeleton({ variant = "cards" }: PageLoadingSkeletonProps) {
  if (variant === "table") {
    return (
      <Box sx={{ p: { xs: 2, sm: 4 } }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
        <Stack spacing={1}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} variant="rounded" height={48} />
          ))}
        </Stack>
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      <Skeleton variant="text" width={220} height={40} sx={{ mb: 3 }} />
      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} variant="rounded" width={260} height={110} />
        ))}
      </Stack>
      <Skeleton variant="rounded" height={220} sx={{ mt: 3 }} />
    </Box>
  );
}